import cv2
import numpy as np
from tkinter import Tk, filedialog

def message_to_binary(message):
    return ''.join(format(ord(char), '08b') for char in message)

def hide_message_lsb_opencv(image_path, message, output_path='stego_image.png'):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Error: Cannot load image from '{image_path}'")

    binary_message = message_to_binary(message) + '1111111111111110'
    data_index = 0
    msg_len = len(binary_message)

    height, width, _ = img.shape
    total_bits = width * height * 3

    if msg_len > total_bits:
        raise ValueError("Message too large to hide in the image.")

    flat_img = img.flatten()

    for i in range(msg_len):
        flat_img[i] = (flat_img[i] & 0xFE) | int(binary_message[i])

    stego_img = flat_img.reshape((height, width, 3))
    cv2.imwrite(output_path, stego_img)
    print(f"✅ Message hidden successfully in '{output_path}'")

def select_image_and_hide():
    Tk().withdraw()  # Hide the main Tk window
    image_path = filedialog.askopenfilename(title="Select the image to hide the message")
    if not image_path:
        print("⚠️ No image selected.")
        return
    message = input("Enter the message you want to hide: ")
    hide_message_lsb_opencv(image_path, message)

# Run
select_image_and_hide()
