import cv2
import numpy as np
import os
from PIL import Image  # Pillow helps convert GIF/JPG to RGB PNG

def convert_to_png_if_needed(image_path):
    ext = os.path.splitext(image_path)[1].lower()
    if ext in ['.png']:
        return image_path  # already png
    # convert to png
    img = Image.open(image_path).convert("RGB")
    temp_path = "temp_cover.png"
    img.save(temp_path, "PNG")
    print(f"[INFO] Converted {image_path} to {temp_path} for lossless embedding.")
    return temp_path

def file_to_binary(file_path):
    with open(file_path, "rb") as f:
        content = f.read()
    ext = os.path.splitext(file_path)[1][1:]
    ext = ext.ljust(3, ' ')
    ext_bin = ''.join([format(ord(char), '08b') for char in ext])
    length_bin = format(len(content), '032b')
    data_bin = ''.join([format(byte, '08b') for byte in content])
    return ext_bin + length_bin + data_bin, len(content)

def check_capacity(image_path, file_size_bytes):
    img = cv2.imread(image_path)
    if img is None:
        print("[-] Error: Cannot load image")
        return False
    h, w, c = img.shape
    capacity_bits = h * w * c
    capacity_bytes = capacity_bits // 8
    print(f"[INFO] Cover image capacity: {capacity_bits} bits (~{capacity_bytes} bytes)")
    print(f"[INFO] File size: {file_size_bytes} bytes")
    if file_size_bytes > capacity_bytes - 8:
        print("[-] Warning: File too large for this cover image!")
        print("    ➡ Choose a larger cover image or smaller file.")
        return False
    return True

def embed_file_in_image(image_path, file_path, output_path="stego_image.png"):
    # convert jpg/gif to png first
    safe_image_path = convert_to_png_if_needed(image_path)

    # check size
    _, file_size = file_to_binary(file_path)
    if not check_capacity(safe_image_path, file_size):
        return

    img = cv2.imread(safe_image_path)
    if img is None:
        print("[-] Error: Cannot load image")
        return

    binary_data, _ = file_to_binary(file_path)
    data_len = len(binary_data)
    print(f"[+] Total bits to embed: {data_len}")

    flat_img = img.flatten()
    if data_len > len(flat_img):
        print("[-] Error: File is too large for this image.")
        return

    for i in range(data_len):
        flat_img[i] = (flat_img[i] & 254) | int(binary_data[i])

    stego_img = flat_img.reshape(img.shape)
    # ALWAYS save as PNG to preserve data
    if not output_path.lower().endswith(".png"):
        output_path += ".png"
    cv2.imwrite(output_path, stego_img)
    print(f"[+] File embedded successfully. Output saved to: {output_path}")

def main():
    print("==== File Embedder ====")
    img_path = input("Enter path to cover image (PNG/JPG/GIF): ").strip()
    file_path = input("Enter path to file to hide (.txt/.png/etc.): ").strip()
    output_path = input("Enter output stego image name (will be PNG): ").strip()
    embed_file_in_image(img_path, file_path, output_path)

if __name__ == "__main__":
    main()
