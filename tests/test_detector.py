"""Run with python -m unittest discover -s tests -v"""
import unittest

try:
    import cv2
    import numpy as np
    from detector import analyze
    AVAILABLE = True
except ImportError:
    AVAILABLE = False


@unittest.skipUnless(AVAILABLE, "Install requirements.txt first")
class DetectorTests(unittest.TestCase):
    def test_invalid_image(self):
        with self.assertRaises(ValueError):
            analyze(b"this is not an image")

    def test_blank_image_has_no_candidates(self):
        image = np.full((500, 500, 3), 255, dtype=np.uint8)
        ok, raw = cv2.imencode(".png", image)
        self.assertTrue(ok)
        self.assertEqual(analyze(raw.tobytes())["detections"], [])

    def test_red_circle_is_detected_as_candidate(self):
        image = np.full((500, 500, 3), 255, dtype=np.uint8)
        cv2.circle(image, (250, 250), 100, (0, 0, 220), thickness=22)
        ok, raw = cv2.imencode(".png", image)
        self.assertTrue(ok)
        result = analyze(raw.tobytes())
        self.assertGreater(len(result["detections"]), 0)
        self.assertTrue(any(d["color"] == "red" for d in result["detections"]))

    def test_blue_rectangle_is_detected_as_candidate(self):
        image = np.full((500, 500, 3), 255, dtype=np.uint8)
        cv2.rectangle(image, (160, 160), (350, 300), (230, 90, 20), thickness=-1)
        ok, raw = cv2.imencode(".png", image)
        self.assertTrue(ok)
        result = analyze(raw.tobytes())
        self.assertTrue(any(d["color"] == "blue" for d in result["detections"]))


if __name__ == "__main__":
    unittest.main()
