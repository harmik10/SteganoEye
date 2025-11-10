import cv2
import numpy as np
import os
from PIL import Image  # for conversion (JPG/GIF to PNG)

# Ensure static folder exists
os.makedirs("static", exist_ok=True)

def convert_to_png_if_needed(image_path):
    ext = os.path.splitext(image_path)[1].lower()
    if ext == '.png':
        return image_path  # already PNG
    img = Image.open(image_path).convert("RGB")
    temp_path = "temp_cover.png"
    img.save(temp_path, "PNG")
    print(f"[INFO] Converted {image_path} to {temp_path} for lossless embedding.")
    return temp_path

def file_to_binary(file_path):
    with open(file_path, "rb") as f:
        content = f.read()
    ext = os.path.splitext(file_path)[1][1:]  # get extension without dot
    ext = ext.ljust(3, ' ')
    ext_bin = ''.join([format(ord(c), '08b') for c in ext])
    length_bin = format(len(content), '032b')
    data_bin = ''.join([format(byte, '08b') for byte in content])
    return ext_bin + length_bin + data_bin, len(content)

def check_capacity(image_path, file_size_bytes):
    img = cv2.imread(image_path)
    if img is None:
        print("[-] Error: Cannot load image.")
        return False
    h, w, c = img.shape
    capacity_bits = h * w * c
    needed_bits = (file_size_bytes * 8) + 56  # 24 bits for ext, 32 for length
    print(f"[INFO] Cover image capacity: {capacity_bits} bits (~{capacity_bits//8} bytes)")
    print(f"[INFO] Needed: {needed_bits} bits (~{needed_bits//8} bytes)")
    if needed_bits > capacity_bits:
        print("[-] Warning: File too large for this cover image!")
        return False
    return True

def embed_file_in_image(image_path, file_path, output_path="stego_image.png"):
    # Convert cover image to PNG if needed
    safe_image_path = convert_to_png_if_needed(image_path)
    # Convert hidden file to binary
    binary_data, file_size = file_to_binary(file_path)

    # Check capacity
    if not check_capacity(safe_image_path, file_size):
        raise ValueError("File too large for this cover image!")

    # Read image
    img = cv2.imread(safe_image_path)
    if img is None:
        raise ValueError("Cannot load image for embedding.")

    data_len = len(binary_data)
    flat_img = img.flatten()

    if data_len > len(flat_img):
        raise ValueError("File is too large for this image.")

    # Embed data bit by bit into LSB
    for i in range(data_len):
        flat_img[i] = (flat_img[i] & 0xFE) | int(binary_data[i])

    stego_img = flat_img.reshape(img.shape)

    if not output_path.lower().endswith(".png"):
        output_path += ".png"
    cv2.imwrite(output_path, stego_img)
    print(f"[+] File embedded successfully. Output saved to: {output_path}")
    return output_path  # return path for app.py

def binary_to_file(binary_data, output_path):
    ext_bin = binary_data[:24]
    length_bin = binary_data[24:56]
    ext = ''.join([chr(int(ext_bin[i:i+8], 2)) for i in range(0, 24, 8)]).strip()
    data_len = int(length_bin, 2)

    file_data_bin = binary_data[56:56 + (data_len * 8)]
    file_bytes = bytearray()
    for i in range(0, len(file_data_bin), 8):
        byte = file_data_bin[i:i+8]
        file_bytes.append(int(byte, 2))

    full_path = output_path + "." + ext
    with open(full_path, 'wb') as f:
        f.write(file_bytes)
    print(f"[+] File extracted and saved as: {full_path}")
    return full_path  # return full file path for app.py

def extract_file_from_image(image_path, output_base="recovered_file"):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Cannot load image for extraction.")

    flat_img = img.flatten()
    if len(flat_img) < 56:
        raise ValueError("Image too small or no data present.")

    header_bits = [str(flat_img[i] & 1) for i in range(56)]
    ext_bin = ''.join(header_bits[:24])
    length_bin = ''.join(header_bits[24:56])

    try:
        ext = ''.join([chr(int(ext_bin[i:i+8], 2)) for i in range(0, 24, 8)]).strip()
        data_len = int(length_bin, 2)
    except:
        raise ValueError("Failed to decode header. Not a valid stego image.")

    total_bits = 56 + (data_len * 8)
    if total_bits > len(flat_img):
        raise ValueError("Not enough data in the image to recover file.")

    all_bits = [str(flat_img[i] & 1) for i in range(total_bits)]
    binary_data = ''.join(all_bits)

    return binary_to_file(binary_data, output_base)
