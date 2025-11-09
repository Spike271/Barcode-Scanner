# 📱 Barcode Scanner

A powerful and intuitive Python-based barcode scanning application that captures, processes, and stores barcode data with ease.

## ✨ Features

- **Real-time Barcode Detection**: Scan barcodes instantly using your webcam or camera
- **Multiple Format Support**: Handles various barcode formats (1D and 2D codes)
- **Data Persistence**: Automatically saves scanned barcode data to JSON for easy access
- **Computer Vision Powered**: Leverages OpenCV for robust image processing
- **User-Friendly Interface**: Simple and intuitive application design
- **Efficient Processing**: Optimized for fast barcode recognition

## 🚀 Quick Start

### Prerequisites

- Python 3.13.9 or higher
- Virtualenv for environment management
- A camera/webcam connected to your system

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd barcode-scanner
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   The project includes:
   - `opencv-python` - Computer vision library for image processing
   - `pillow` - Image manipulation and processing
   - `numpy` - Numerical computing

### Usage

**Run the scanner:**
```bash
python main.py
```