import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import cv2
from PIL import Image, ImageTk
from barcode_scanner import BarcodeQRScanner, draw_bounding_boxes, decode_barcodes
import threading

class ScannerGUI:
    def __init__(self, name):
        self.root = name
        self.root.title("Barcode & QR Code Scanner")
        self.root.geometry("800x600")

        self.results_text = None
        self.video_label = None
        self.is_scanning = False
        self.scanner = BarcodeQRScanner()

        self.setup_ui()

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=0, column=0, sticky=tk.W, pady=5)

        # Buttons
        ttk.Button(controls_frame, text="Start Camera",
                   command=self.start_camera).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Stop Camera",
                   command=self.stop_camera).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Scan Image",
                   command=self.scan_image).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Save Results",
                   command=self.save_results).pack(side="left", padx=5)

        # Video display
        self.video_label = ttk.Label(main_frame)
        self.video_label.grid(row=1, column=0, pady=10)

        # Result display
        results_frame = ttk.LabelFrame(main_frame, text="Scanned Codes", padding="5")
        results_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        self.results_text = tk.Text(results_frame, height=10, width=80)
        self.results_text.tag_configure("bold", font=("Arial", 12, "normal"))
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL,
                                  command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)


        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

    def start_camera(self):
        if not self.is_scanning:
            self.is_scanning = True
            thread = threading.Thread(target=self.camera_scan_thread)
            thread.daemon = True
            thread.start()

    def stop_camera(self):
        self.is_scanning = False

    def camera_scan_thread(self):
        try:
            if not self.scanner.initialize_camera():
                messagebox.showerror("Error", "Could not initialize camera")
                return

            while self.is_scanning:
                ret, frame = self.scanner.cap.read()
                if not ret:
                    break

                # Decode barcodes
                decoded_objects = decode_barcodes(frame)

                # Process new codes
                for obj in decoded_objects:
                    if obj['data'] not in self.scanner.scanned_codes:
                        self.scanner.scanned_codes.add(obj['data'])
                        self.add_result(f"{obj['type']}: {obj['data']}")

                # Draw bounding boxes
                draw_bounding_boxes(frame, decoded_objects)

                # Convert frame for display in GUI
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame_rgb)
                image.thumbnail((640, 480))
                photo = ImageTk.PhotoImage(image)

                # Update GUI in main thread
                self.root.after(0, self.update_video_display, photo)

        except Exception as e:
            messagebox.showerror("Error", f"Camera error: {str(e)}")
        finally:
            self.scanner.cleanup()
            self.is_scanning = False

    def update_video_display(self, photo):
        self.video_label.configure(image=photo)
        self.video_label.image = photo

    def add_result(self, result):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, result + "\n")

    def scan_image(self):
        filename = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        if filename:
            self.scanner.scan_from_image(filename)
            # Update results
            self.results_text.delete(1.0, tk.END)
            for code in self.scanner.scanned_codes:
                self.add_result(f"QR/BARCODE: {code}")

    def save_results(self):
        self.scanner.save_scanned_codes()
        messagebox.showinfo("Success", "Results saved to scanned_codes.json")


if __name__ == "__main__":
    root = tk.Tk()
    app = ScannerGUI(root)
    root.mainloop()