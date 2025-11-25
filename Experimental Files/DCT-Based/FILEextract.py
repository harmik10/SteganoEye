import cv2
import numpy as np
import base64
import os

def decode_bit_from_dct_pair(dct_block):
    return '1' if dct_block[3][4] > dct_block[4][3] else '0'

def extract_all_bits(image):
    height, width, _ = image.shape
    image = image.astype(np.float32)
    bits = []

    for row in range(0, height, 8):
        for col in range(0, width, 8):
            block = image[row:row+8, col:col+8, 0]
            if block.shape != (8, 8):
                continue
            dct_block = cv2.dct(block)
            bits.append(decode_bit_from_dct_pair(dct_block))
    return bits

def bits_to_bytes(bits):
    return bytes(int(''.join(bits[i:i+8]), 2) for i in range(0, len(bits), 8))

def extract_message_from_image(stego_path):
    img = cv2.imread(stego_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Stego image is unreadable or invalid.")

    all_bits = extract_all_bits(img)

    # Look for end marker
    end_marker = '1111111111111110'
    bitstream = ''.join(all_bits)
    end_idx = bitstream.find(end_marker)

    if end_idx == -1:
        raise ValueError("End marker not found. File may be corrupted or modified.")

    message_bits = bitstream[:end_idx]
    b64_bytes = bits_to_bytes(message_bits)

    # Fix padding before decoding
    pad_len = (4 - len(b64_bytes) % 4) % 4
    b64_padded = b64_bytes + b'=' * pad_len

    try:
        original_data = base64.b64decode(b64_padded)
        return original_data
    except Exception as e:
        raise ValueError(f"Base64 decoding failed: {e}")

def main():
    print("📤 DCT Steganography Extraction (Marker-Based)")
    stego_path = input("Enter path of the stego image: ").strip()

    try:
        extracted = extract_message_from_image(stego_path)
        if not extracted:
            print("⚠️ Extraction failed or message was empty.")
            return

        output_dir = os.path.dirname(stego_path)
        output_path = os.path.join(output_dir, "extracted_file")

        if extracted[:4] == b'\x89PNG':
            output_path += ".png"
        elif extracted[:2] == b'\xff\xd8':
            output_path += ".jpg"
        elif extracted[:2] == b'BM':
            output_path += ".bmp"
        elif extracted.startswith(b'%PDF'):
            output_path += ".pdf"
        elif extracted.startswith(b'PK'):
            output_path += ".zip"
        else:
            output_path += ".bin"

        with open(output_path, 'wb') as f:
            f.write(extracted)
        print(f"✅ File extracted and saved to: {output_path}")

    except Exception as e:
        print("❌ Error:", e)

if __name__ == '__main__':
    main()
