import cv2
import numpy as np

with open("extracted.txt", "rb") as f:
    data = f.read()
    try:
        text = data.decode()
        print("✅ Extracted Text Message:")
        print(text)
    except UnicodeDecodeError:
        print("❌ The file does not contain plain text (likely a binary file like image or zip).")
