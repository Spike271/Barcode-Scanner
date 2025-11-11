import cv2
import numpy as np
from pyzbar.pyzbar import decode
from datetime import datetime
import json


def decode_barcodes(frame) -> list:
    """Decode barcodes and QR codes from frame"""
    # Convert to grayscale for better detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Decode the barcodes
    decoded_objects = decode(gray)

    results = []
    for obj in decoded_objects:
        data = obj.data.decode('utf-8')
        code_type = obj.type
        points = obj.polygon

        # Convert polygon points to a numpy array
        if len(points) == 4:
            pts = np.array(points, np.int32)
            pts = pts.reshape((-1, 1, 2))
        else:
            # For some barcodes, we might get more points
            hull = cv2.convexHull(np.array(points, np.float32))
            pts = hull.astype(np.int32)

        results.append({
            'data': data,
            'type': code_type,
            'points': pts,
            'timestamp': datetime.now().isoformat()
        })

    return results


def draw_bounding_boxes(frame, decoded_objects) -> None:
    """Draw bounding boxes and labels around detected codes"""
    for obj in decoded_objects:
        # Draw bounding box
        cv2.polylines(frame, [obj['points']], True, (0, 255, 0), 3)

        # Draw label background
        label = f"{obj['type']}: {obj['data']}"
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]

        # Get the top-left point for the label
        x, y = obj['points'][0][0]
        cv2.rectangle(frame, (x, y - text_size[1] - 10),
                      (x + text_size[0] + 10, y), (0, 255, 0), -1)

        # Draw label text
        cv2.putText(frame, label, (x + 5, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)


class BarcodeQRScanner:
    def __init__(self):
        self.cap = None
        self.scanned_codes = set()

    def initialize_camera(self, camera_index=0) -> bool:
        """Initialize the camera"""
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise Exception("Could not open camera")

        # Set camera resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        return True

    def scan_from_camera(self) -> None:
        """Real-time scanning from a camera"""
        try:
            if not self.initialize_camera():
                print("Failed to initialize camera")
                return

            print("Camera started. Press 'q' to quit, 's' to save scanned codes")

            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to grab frame")
                    break

                # Decode barcodes
                decoded_objects = decode_barcodes(frame)

                # Process new codes
                for obj in decoded_objects:
                    if obj['data'] not in self.scanned_codes:
                        self.scanned_codes.add(obj['data'])
                        print(f"Scanned: {obj['type']} - {obj['data']}")

                # Draw bounding boxes
                draw_bounding_boxes(frame, decoded_objects)

                # Display frame
                cv2.imshow('Barcode & QR Code Scanner', frame)

                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self.save_scanned_codes()

        finally:
            self.cleanup()

    def scan_from_image(self, image_path) -> None:
        """Scan barcodes from an image file"""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                print(f"Could not load image: {image_path}")
                return

            # Decode barcodes
            decoded_objects = decode_barcodes(image)

            if decoded_objects:
                print(f"Found {len(decoded_objects)} code(s) in {image_path}:")
                for obj in decoded_objects:
                    print(f"  {obj['type']}: {obj['data']}")
                    self.scanned_codes.add(obj['data'])

                # Draw bounding boxes and display
                draw_bounding_boxes(image, decoded_objects)
                cv2.imshow('Scanned Image', image)
                cv2.waitKey(0)
            else:
                print(f"No barcodes or QR codes found in {image_path}")

        finally:
            cv2.destroyAllWindows()

    def save_scanned_codes(self, filename="scanned_codes.json") -> None:
        """Save scanned codes to a JSON file"""
        codes_list = list(self.scanned_codes)
        with open(filename, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_codes': len(codes_list),
                'codes': codes_list
            }, f, indent=2)
        print(f"Scanned codes saved to {filename}")

    def cleanup(self) -> None:
        """Clean up resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
