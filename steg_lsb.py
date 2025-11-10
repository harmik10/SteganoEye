#harmik
import cv2
import numpy as np
import uuid
import os

# Ensure 'static' folder exists
os.makedirs("static", exist_ok=True)

def message_to_binary(message):
    return ''.join(format(ord(char), '08b') for char in message)

def hide_message_lsb_opencv(image_path, message):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Error: Cannot load image from '{image_path}'")

    binary_message = message_to_binary(message) + '1111111111111110'
    msg_len = len(binary_message)

    height, width, _ = img.shape
    total_bits = width * height * 3

    if msg_len > total_bits:
        raise ValueError("Message too large to hide in the image.")

    flat_img = img.flatten()
    for i in range(msg_len):
        flat_img[i] = (flat_img[i] & 0xFE) | int(binary_message[i])
    stego_img = flat_img.reshape((height, width, 3))

    # Generate unique filename and save to static/
    filename = f"stego_{uuid.uuid4().hex[:8]}.png"
    output_path = os.path.join("static", filename)
    cv2.imwrite(output_path, stego_img)

    return filename

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
    return binary_to_message(binary_data)
