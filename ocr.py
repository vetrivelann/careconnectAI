from PIL import Image
import pytesseract
import re

# 🔥 SET TESSERACT PATH (IMPORTANT)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# =========================
# 📄 EXTRACT TEXT FROM IMAGE
# =========================
def extract_text(image_file):
    try:
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return f"Error extracting text: {e}"


# =========================
# 🧠 EXTRACT PATIENT NAME
# =========================
def extract_patient_name(text):
    try:
        # Match: Patient Name: Arjun Kumar
        match = re.search(r'Patient Name[:\-]\s*(.*)', text)

        if match:
            name = match.group(1).strip()

            # Remove extra unwanted parts if OCR messy
            name = name.split("\n")[0]

            return name

        return None

    except:
        return None