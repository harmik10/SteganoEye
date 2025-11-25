import cv2
import numpy as np
from tkinter import Tk, filedialog

def binary_to_message(binary_data):
    end_marker = '1111111111111110'
    end_index = binary_data.find(end_marker)
    if end_index != -1:
        binary_data = binary_data[:end_index]
    else:
        return "[Error: End marker not found]"

    chars = [chr(int(binary_data[i:i+8], 2)) for i in range(0, len(binary_data), 8)]
    return ''.join(chars)

def extract_message_lsb_opencv(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Error: Cannot load image from '{image_path}'")

    flat_img = img.flatten()
    bits = np.bitwise_and(flat_img, 1)

    binary_data = ''.join(map(str, bits))
    message = binary_to_message(binary_data)
    print("🕵️ Hidden message extracted:")
    print(message)

def select_image_and_extract():
    Tk().withdraw()
    image_path = filedialog.askopenfilename(title="Select the stego image to extract message from")
    if not image_path:
        print("⚠️ No image selected.")
        return
    extract_message_lsb_opencv(image_path)

# Run
select_image_and_extract()
