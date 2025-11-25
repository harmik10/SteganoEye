import cv2
import numpy as np

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

def extract_file_from_image(image_path, output_path="recovered_file"):
    img = cv2.imread(image_path)
    if img is None:
        print("[-] Error: Cannot load image")
        return

    flat_img = img.flatten()

    if len(flat_img) < 56:
        print("[-] Image too small to contain embedded data.")
        return

    header_bits = [str(flat_img[i] & 1) for i in range(56)]
    ext_bin = ''.join(header_bits[:24])
    length_bin = ''.join(header_bits[24:56])

    try:
        ext = ''.join([chr(int(ext_bin[i:i+8], 2)) for i in range(0, 24, 8)]).strip()
        data_len = int(length_bin, 2)
    except:
        print("[-] Failed to decode header. This might not be a valid stego image.")
        return

    total_bits = 56 + (data_len * 8)
    if total_bits > len(flat_img):
        print("[-] Error: Not enough data in the image to recover file.")
        return

    all_bits = [str(flat_img[i] & 1) for i in range(total_bits)]
    binary_data = ''.join(all_bits)

    binary_to_file(binary_data, output_path)

# ------------------------
# Command-line Interface
# ------------------------
def main():
    print("==== File Extractor ====")
    img_path = input("Enter path to stego image: ").strip()
    output_base = input("Enter base name for extracted file (e.g., recovered_file): ").strip()
    extract_file_from_image(img_path, output_base)

if __name__ == "__main__":
    main()
