import cv2
import numpy as np
import os

def file_to_binary(file_path):
    with open(file_path, "rb") as f:
        content = f.read()
    ext = os.path.splitext(file_path)[1][1:]  # extension without dot
    ext = ext.ljust(3, ' ')  # pad to 3 characters
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

    if file_size_bytes > capacity_bytes - 8:  # minus a little for header
        print("[-] Warning: File too large for this cover image!")
        print("    ➡ Choose a larger cover image or smaller file.")
        return False
    return True

def embed_file_in_image(image_path, file_path, output_path="stego_image.png"):
    # check size first
    _, file_size = file_to_binary(file_path)
    if not check_capacity(image_path, file_size):
        return  # stop if not compatible

    img = cv2.imread(image_path)
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
    cv2.imwrite(output_path, stego_img)
    print(f"[+] File embedded successfully. Output saved to: {output_path}")

# ------------------------
# Command-line Interface
# ------------------------
def main():
    print("==== File Embedder ====")
    img_path = input("Enter path to cover image: ").strip()
    file_path = input("Enter path to file to hide (.txt/.png/etc.): ").strip()
    output_path = input("Enter output stego image name (e.g., stego.png): ").strip()
    embed_file_in_image(img_path, file_path, output_path)

if __name__ == "__main__":
    main()
