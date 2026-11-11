"""Simple color-and-shape traffic sign *candidate* detector.

This is a portfolio reconstruction using OpenCV rules, not the original
Azure Computer Vision / Custom Vision model and not a driving safety system.
"""
from __future__ import annotations

import cv2
import numpy as np


def _iou(a: dict, b: dict) -> float:
    ax, ay, aw, ah = a["bbox"]
    bx, by, bw, bh = b["bbox"]
    x1, y1 = max(ax, bx), max(ay, by)
    x2, y2 = min(ax + aw, bx + bw), min(ay + ah, by + bh)
    overlap = max(0, x2 - x1) * max(0, y2 - y1)
    union = aw * ah + bw * bh - overlap
    return overlap / union if union else 0.0


def analyze(image_bytes: bytes) -> dict:
    """Return potential sign regions in ORIGINAL image pixel coordinates."""
    if not image_bytes:
        raise ValueError("이미지 파일을 선택해 주세요.")

    encoded = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("JPG, PNG 또는 WebP 이미지 파일을 확인해 주세요.")

    original_h, original_w = image.shape[:2]
    if original_w < 32 or original_h < 32:
        raise ValueError("가로와 세로가 32픽셀 이상인 이미지를 사용해 주세요.")

    # Use a downscaled copy for predictable image processing cost.
    scale = min(1.0, 1200.0 / max(original_w, original_h))
    if scale < 1:
        image = cv2.resize(
            image, (round(original_w * scale), round(original_h * scale)),
            interpolation=cv2.INTER_AREA,
        )

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    red_low = cv2.inRange(hsv, np.array([0, 90, 65]), np.array([12, 255, 255]))
    red_high = cv2.inRange(hsv, np.array([170, 90, 65]), np.array([179, 255, 255]))
    blue = cv2.inRange(hsv, np.array([95, 75, 65]), np.array([135, 255, 255]))

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    masks = (
        ("red", cv2.bitwise_or(red_low, red_high)),
        ("blue", blue),
    )
    results = []
    h, w = image.shape[:2]
    for color_name, mask in masks:
        # A morphological close reconnects broken color regions.
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 200 or area > h * w * 0.65:
                continue
            x, y, bw, bh = cv2.boundingRect(contour)
            if min(bw, bh) < 18 or not 0.35 <= bw / bh <= 2.7:
                continue

            perimeter = cv2.arcLength(contour, True)
            if perimeter <= 0:
                continue
            vertices = len(cv2.approxPolyDP(contour, 0.045 * perimeter, True))
            circularity = 4 * np.pi * area / (perimeter * perimeter)

            if color_name == "red":
                if vertices == 3:
                    label = "삼각형 경고 표지 후보"
                    advice = "경고 표지로 보이는 영역이 있습니다. 주변 상황을 확인하세요."
                elif 7 <= vertices <= 9:
                    label = "팔각형 정지 표지 후보"
                    advice = "정지 표지 형태의 영역이 있습니다. 실제 표지판을 확인하세요."
                elif circularity >= 0.65:
                    label = "원형 규제 표지 후보"
                    advice = "규제 표지로 보이는 영역이 있습니다. 표지 내용을 확인하세요."
                else:
                    label = "빨간색 표지 후보"
                    advice = "빨간색 표지 형태가 감지되었습니다. 주변을 확인하세요."
            else:
                label = "파란색 안내 표지 후보"
                advice = "안내 표지로 보이는 영역이 있습니다. 표지 내용을 확인하세요."

            bbox = [
                round(x / scale), round(y / scale),
                round(bw / scale), round(bh / scale),
            ]
            results.append({
                "label": label,
                "advice": advice,
                "bbox": bbox,
                "color": color_name,
                "area": int(area),
            })

    # Suppress overlapping rectangles. Area measures mask pixels, NOT confidence.
    kept = []
    for detection in sorted(results, key=lambda item: item["area"], reverse=True):
        if all(_iou(detection, previous) < 0.40 for previous in kept):
            kept.append(detection)
        if len(kept) >= 8:
            break

    for detection in kept:
        detection.pop("area", None)
    return {
        "width": original_w,
        "height": original_h,
        "detections": kept,
        "disclaimer": "색상·형태 기반 데모 결과이며 실제 교통표지판 판독이나 운전 판단에 사용할 수 없습니다.",
    }
