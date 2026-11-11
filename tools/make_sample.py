"""Generate a synthetic image to try the detector (not a real road sign)."""
from pathlib import Path

import cv2
import numpy as np

canvas = np.full((520, 900, 3), (238, 245, 248), dtype=np.uint8)
cv2.rectangle(canvas, (0, 400), (900, 520), (195, 200, 205), -1)
cv2.circle(canvas, (260, 210), 115, (0, 0, 220), thickness=25)
cv2.circle(canvas, (260, 210), 88, (255, 255, 255), thickness=-1)
cv2.rectangle(canvas, (560, 105), (770, 330), (210, 98, 22), thickness=-1)
cv2.rectangle(canvas, (576, 121), (754, 314), (255, 255, 255), thickness=9)
cv2.putText(canvas, "DEMO", (587, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
out = Path(__file__).resolve().parent.parent / "sample_signs.png"
cv2.imwrite(str(out), canvas)
print(f"Created: {out}")
