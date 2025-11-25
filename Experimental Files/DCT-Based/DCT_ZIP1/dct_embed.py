import cv2
import numpy as np
from scipy.fftpack import dct, idct

def message_to_bits(msg):
    return ''.join(format(ord(i), '08b') for i in msg)

def embed_text_dct(image_path, message, output_path='stego_image.png'):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print("❌ Error: Image not found.")
        return

    if not output_path.lower().endswith('.png'):
        print("⚠️ Use PNG output to preserve quality. Changing extension to .png")
        output_path = output_path.rsplit('.', 1)[0] + ".png"

    message += "#####"
    bits = message_to_bits(message)
    bit_idx = 0

    stego_image = np.copy(image)
    h, w = stego_image.shape

    for row in range(0, h, 8):
        for col in range(0, w, 8):
            if bit_idx >= len(bits):
                break

            block = stego_image[row:row+8, col:col+8]
            if block.shape != (8, 8):
                continue

            dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')

            for pos in [(3, 3), (4, 4)]:
                if bit_idx >= len(bits):
                    break
                coeff = dct_block[pos]
                coeff_int = int(np.round(coeff))
                coeff_bin = list(format((coeff_int + 256) % 256, '08b'))
                coeff_bin[-1] = bits[bit_idx]
                new_coeff = int("".join(coeff_bin), 2)
                if coeff_int < 0:
                    new_coeff = -new_coeff
                dct_block[pos] = new_coeff
                bit_idx += 1

            idct_block = idct(idct(dct_block.T, norm='ortho').T, norm='ortho')
            stego_image[row:row+8, col:col+8] = np.clip(np.round(idct_block), 0, 255)

        if bit_idx >= len(bits):
            break

    cv2.imwrite(output_path, stego_image.astype(np.uint8))
    print(f"✅ Stego image saved as: {output_path}")

if __name__ == "__main__":
    print("🧠 DCT Text Embedding")
    image_path = input("🖼️ Enter path to input image (PNG recommended): ")
    message = input("💬 Enter the message to embed: ")
    output_path = input("📁 Output stego image filename (default: stego_image.png): ").strip() or "stego_image.png"
    embed_text_dct(image_path, message, output_path)
