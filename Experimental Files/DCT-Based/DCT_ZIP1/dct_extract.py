import cv2
import numpy as np
from scipy.fftpack import dct
import time

def extract_text_dct(stego_path):
    image = cv2.imread(stego_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print("❌ Error: Image not found.")
        return

    h, w = image.shape
    print(f"🔍 Extracting from {h}x{w} image")

    bits = ""
    message = ""
    end_marker = "#####"

    start_time = time.time()
    block_count = 0

    for row in range(0, h, 8):
        for col in range(0, w, 8):
            block = image[row:row+8, col:col+8]
            if block.shape != (8, 8):
                continue

            dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
            for pos in [(3, 3), (4, 4)]:
                coeff = int(np.round(dct_block[pos]))
                coeff_bin = format((coeff + 256) % 256, '08b')
                bits += coeff_bin[-1]

                if len(bits) == 8:
                    char = chr(int(bits, 2))
                    message += char
                    if message.endswith(end_marker):
                        print("✅ Hidden Message Found:\n")
                        print(message[:-5])
                        print(f"⏱️ Time taken: {round(time.time() - start_time, 2)} seconds")
                        return
                    bits = ""

            block_count += 1
            if block_count % 1000 == 0:
                print(f"🧪 Checked {block_count} blocks...")

    print("❌ No hidden message found.")
    print(f"⏱️ Time taken: {round(time.time() - start_time, 2)} seconds")

if __name__ == "__main__":
    print("🔍 DCT Text Extraction")
    path = input("🖼️ Enter path to stego image: ")
    extract_text_dct(path)
