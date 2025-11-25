import cv2
import numpy as np
import base64
import os

def read_message_data(input_type, message_input):
    if input_type == 'text':
        return message_input.encode()
    elif input_type == 'file':
        if not os.path.exists(message_input):
            raise FileNotFoundError("Message file does not exist.")
        with open(message_input, 'rb') as f:
            return f.read()
    else:
        raise ValueError("Invalid input_type")

def embed_message_in_image(img_path, message_data, output_path):
    b64_data = base64.b64encode(message_data)
    b64_bits = ''.join(format(byte, '08b') for byte in b64_data) + '1111111111111110'  # END MARKER

    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Image not found or unsupported format.")

    height, width, _ = img.shape
    img = img.astype(np.float32)
    data_idx = 0

    for row in range(0, height, 8):
        for col in range(0, width, 8):
            if data_idx >= len(b64_bits):
                break
            block = img[row:row+8, col:col+8, 0]  # Blue channel
            if block.shape[0] < 8 or block.shape[1] < 8:
                continue
            dct_block = cv2.dct(block)

            coeff = int(dct_block[4][4])
            coeff_bin = format(coeff, '08b')
            new_bin = coeff_bin[:-1] + b64_bits[data_idx]
            dct_block[4][4] = int(new_bin, 2)
            img[row:row+8, col:col+8, 0] = cv2.idct(dct_block)
            data_idx += 1

        if data_idx >= len(b64_bits):
            break

    img = np.clip(img, 0, 255).astype(np.uint8)
    cv2.imwrite(output_path, img)
    print(f"\n✅ Message embedded successfully into: {output_path}")

def main():
    print("📥 DCT Steganography Embedding")
    img_path = input("Enter path of the input image file: ").strip()
    choice = input("Choose message type — 'text' or 'file': ").strip().lower()

    if choice == 'text':
        message = input("Enter the message to hide: ")
    elif choice == 'file':
        message = input("Enter path of the file to hide: ").strip()
    else:
        print("❌ Invalid message type. Must be 'text' or 'file'.")
        return

    output_path = input("Enter output image filename (e.g., stego.png): ").strip()
    try:
        message_data = read_message_data(choice, message)
        embed_message_in_image(img_path, message_data, output_path)
    except Exception as e:
        print("❌ Error:", e)

if __name__ == '__main__':
    main()
