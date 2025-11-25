import cv2
import numpy as np
import base64
import os

def extract_message_from_image(stego_path):
    img = cv2.imread(stego_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Stego image not found or invalid.")

    height, width, _ = img.shape
    img = img.astype(np.float32)
    binary_data = ''

    for row in range(0, height, 8):
        for col in range(0, width, 8):
            block = img[row:row+8, col:col+8, 0]
            if block.shape[0] < 8 or block.shape[1] < 8:
                continue
            dct_block = cv2.dct(block)
            coeff = int(dct_block[4][4])
            coeff_bin = format(coeff, '08b')
            binary_data += coeff_bin[-1]

            if binary_data.endswith('1111111111111110'):  # End marker
                break
        if binary_data.endswith('1111111111111110'):
            break

    binary_data = binary_data[:-16]  # Remove end marker
    byte_data = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    b64_bytes = bytes([int(b, 2) for b in byte_data])

    try:
        original_data = base64.b64decode(b64_bytes)
        return original_data
    except Exception as e:
        print("⚠️ Base64 decode failed:", e)
        return None

def main():
    print("📤 DCT Steganography Extraction")
    stego_path = input("Enter path of the stego image: ").strip()

    if not os.path.exists(stego_path):
        print("❌ Stego image not found.")
        return

    output_type = input("Do you want to extract as 'text' or 'file'? ").strip().lower()

    try:
        extracted = extract_message_from_image(stego_path)
        if not extracted:
            print("⚠️ Extraction failed or no message found.")
            return

        # Get the directory of the input stego image
        base_dir = os.path.dirname(stego_path)

        if output_type == 'text':
            try:
                text = extracted.decode()
                output_path = os.path.join(base_dir, "extracted.txt")
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"✅ Text extracted and saved to: {output_path}")
            except UnicodeDecodeError:
                print("❌ Cannot decode as text. Try extracting as a file.")
        else:
            # Save binary data as .bin or .png
            output_path = os.path.join(base_dir, "extracted_file")
            # Try to detect common magic headers
            if extracted[:4] == b'\x89PNG':
                output_path += ".png"
            elif extracted[:2] == b'\xff\xd8':
                output_path += ".jpg"
            elif extracted[:2] == b'BM':
                output_path += ".bmp"
            else:
                output_path += ".bin"

            with open(output_path, 'wb') as f:
                f.write(extracted)
            print(f"✅ File extracted and saved to: {output_path}")

    except Exception as e:
        print("❌ Error:", e)

if __name__ == '__main__':
    main()
