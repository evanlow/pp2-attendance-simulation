"""
Flask Web Application for Mock NRIC Verification Demo with OCR
DEMO ONLY - No data persistence, no storage
"""

from flask import Flask, render_template, request, jsonify
import pytesseract
from PIL import Image
import io
import re
from datetime import datetime
import pytz
import os

app = Flask(__name__)

# Configure pytesseract path (auto-detect environment)
# Windows: Use local installation path
if os.path.exists(r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
else:
    # Heroku/Linux: Set TESSDATA_PREFIX for Tesseract to find language data
    # Tesseract installed via Aptfile needs this environment variable
    tessdata_paths = [
        '/usr/share/tesseract-ocr/5/tessdata',
        '/usr/share/tesseract-ocr/4.00/tessdata',
        '/usr/share/tessdata',
        '/app/.apt/usr/share/tesseract-ocr/5/tessdata',
        '/app/.apt/usr/share/tesseract-ocr/4.00/tessdata'
    ]
    
    for path in tessdata_paths:
        if os.path.exists(path):
            os.environ['TESSDATA_PREFIX'] = path
            break


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/verify', methods=['POST'])
def verify_nric():
    """
    Process uploaded image:
    1. Receive image from browser
    2. Perform OCR
    3. Extract name and NRIC last 4 digits
    4. Generate SGT timestamp
    5. Return results (no storage)
    """
    try:
        # Get image from request
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        
        # Read image data
        image_data = image_file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Perform OCR
        ocr_text = pytesseract.image_to_string(image)
        
        # Extract information (best-effort parsing)
        name = extract_name(ocr_text)
        nric_last_4 = extract_nric_last_4(ocr_text)
        
        # Generate Singapore Time timestamp
        sgt = pytz.timezone('Asia/Singapore')
        timestamp = datetime.now(sgt).strftime('%Y-%m-%d %H:%M:%S %Z')
        
        # Return results (no storage, display only)
        return jsonify({
            'success': True,
            'ocr_text': ocr_text,
            'name': name,
            'nric_last_4': nric_last_4,
            'timestamp': timestamp
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def extract_name(text):
    """
    Extract candidate name from OCR text (best-effort)
    Looks for common patterns: "NAME:", "Name:", capitalized words
    """
    if not text:
        return "Not detected"
    
    # Try to find "NAME:" or "Name:" pattern
    name_match = re.search(r'(?:NAME|Name):\s*([A-Z][A-Za-z\s]+)', text, re.IGNORECASE)
    if name_match:
        return name_match.group(1).strip()
    
    # Fallback: Look for capitalized words (potential name)
    words = text.split()
    capitalized = [w for w in words if w and w[0].isupper() and len(w) > 2]
    if capitalized:
        # Take first 2-3 capitalized words as potential name
        return ' '.join(capitalized[:3])
    
    return "Not detected"


def extract_nric_last_4(text):
    """
    Extract NRIC last 4 digits only (never expose full NRIC)
    Looks for Singapore NRIC pattern: S/T/F/G + 7 digits + letter
    Returns only the last 4 digits
    """
    if not text:
        return "Not detected"
    
    # Singapore NRIC pattern: [STFG]1234567[A-Z]
    # We extract only the last 4 digits before the check letter
    nric_pattern = r'[STFG]\d{7}[A-Z]'
    matches = re.findall(nric_pattern, text, re.IGNORECASE)
    
    if matches:
        # Get first match and extract last 4 digits
        full_nric = matches[0].upper()
        # Extract digits only, then get last 4
        digits = re.findall(r'\d', full_nric)
        if len(digits) >= 4:
            return ''.join(digits[-4:])
    
    # Fallback: look for any 7-digit sequence and return last 4
    digit_sequences = re.findall(r'\d{7,}', text)
    if digit_sequences:
        return digit_sequences[0][-4:]
    
    return "Not detected"


if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=5000)
