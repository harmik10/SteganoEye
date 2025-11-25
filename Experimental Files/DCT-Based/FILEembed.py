import cv2
import numpy as np
import base64
import os

# Pair encoding using DCT
def encode_bit_in_dct_pair(dct_block, bit):
    a = dct_block[3][4]
    b = dct_block[4][3]
    if bit == '1':
        if a <= b:
            dct_block[3][4] = b + 1
    else:  # bit == '0'
        if a > b:
            dct_block[4][3] = a + 1
    return dct_block

def embed_message_into_image(cover_image_path, message_file_path, output_path):
    if not os.path.exists(message_file_path):
        raise FileNotFoundError("Message file does not exist.")

    with open(message_file_path, 'rb') as f:
        message_data = f.read()

    b64_encoded = base64.b64encode(message_data)
    bitstream = ''.join(format(byte, '08b') for byte in b64_encoded)

    # Append a fixed 16-bit END marker
    bitstream += '1111111111111110'

    img = cv2.imread(cover_image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid or unreadable image format.")

    height, width, _ = img.shape
    img = img.astype(np.float32)

    bit_idx = 0
    for row in range(0, height, 8):
        for col in range(0, width, 8):
            if bit_idx >= len(bitstream):
                break

            block = img[row:row+8, col:col+8, 0]
            if block.shape != (8, 8):
                continue

            dct_block = cv2.dct(block)
            dct_block = encode_bit_in_dct_pair(dct_block, bitstream[bit_idx])
            img[row:row+8, col:col+8, 0] = cv2.idct(dct_block)
            bit_idx += 1
        if bit_idx >= len(bitstream):
            break

    if bit_idx < len(bitstream):
        raise ValueError("Image too small to embed the full message.")

    img = np.clip(img, 0, 255).astype(np.uint8)
    cv2.imwrite(output_path, img)
    print(f"✅ Message embedded successfully in: {output_path}")

def main():
    print("📥 DCT Steganography Embedding (Marker-Based)")
    cover_path = input("Enter path to input cover image: ").strip()
    secret_file = input("Enter path to file to hide: ").strip()
    output_path = input("Enter output image filename (e.g., stego.png): ").strip()

    try:
        embed_message_into_image(cover_path, secret_file, output_path)
    except Exception as e:
        print("❌ Error:", e)

if __name__ == '__main__':
    main()
