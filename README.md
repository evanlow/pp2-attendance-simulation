# NRIC Verification Demo with OCR

A Flask web application demonstrating mock NRIC (Singapore Identity Card) verification using OCR technology.

**⚠️ DEMO ONLY - No data stored or persisted**

## Features

- 📷 Browser camera access for image capture
- 🔍 OCR text extraction using Tesseract
- 👤 Name detection (best-effort)
- 🔢 NRIC last 4 digits only (privacy-focused)
- ⏰ Singapore Time (SGT) timestamp
- 🎨 Beautiful responsive UI
- 🔒 No data persistence or storage

## Tech Stack

- **Backend**: Flask 3.0.0
- **OCR**: pytesseract + Tesseract OCR
- **Image Processing**: Pillow
- **Frontend**: HTML5, CSS3, JavaScript (getUserMedia API)
- **Deployment**: Heroku-ready

## Local Setup

### Prerequisites

- Python 3.10+
- Tesseract OCR installed

### Installation

1. Clone the repository:
```bash
git clone https://github.com/evanlow/pp2-attendance-simulation.git
cd pp2-attendance-simulation
```

2. Install Tesseract OCR:
   - **Windows**: Download from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

3. Create virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open browser: http://localhost:5000

## Heroku Deployment

This application is ready for Heroku deployment with all necessary configuration files:

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add buildpack for apt packages (Tesseract)
heroku buildpacks:add --index 1 heroku-community/apt

# Deploy
git push heroku main

# Open app
heroku open
```

## File Structure

```
├── app.py              # Flask backend with OCR processing
├── templates/
│   └── index.html      # Single-page web UI
├── requirements.txt    # Python dependencies
├── Procfile           # Heroku web server config
├── Aptfile            # Heroku system packages
└── .gitignore         # Git ignore rules
```

## Privacy & Security

- ✅ No database connections
- ✅ No file system writes
- ✅ Only last 4 NRIC digits exposed
- ✅ All processing in-memory only
- ✅ Images not saved or logged
- ✅ Clear disclaimer displayed

## Demo Screenshot

The application provides a clean interface for capturing NRIC images and displaying verification results with OCR-extracted information.

## License

This is a demonstration project for educational purposes only. Not intended for production use with real identity documents.

## Disclaimer

This application is for **demonstration purposes only**. It does not store, persist, or transmit any personal data. All processing happens in-memory and results are displayed only on the screen.

---

Built with ❤️ using Flask and Tesseract OCR
