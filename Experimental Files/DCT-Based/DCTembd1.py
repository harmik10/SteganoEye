import cv2
import numpy as np
from scipy.fftpack import dct, idct

def message_to_bits(msg):
    return ''.join(format(ord(i), '08b') for i in msg)

def embed_text_dct(image_array, message):
    message += "#####"
    bits = message_to_bits(message)
    bit_idx = 0

    stego_image = np.copy(image_array)
    h, w = stego_image.shape

    for row in range(0, h, 8):
        for col in range(0, w, 8):
            if bit_idx >= len(bits):
                break
            block = stego_image[row:row+8, col:col+8]
            if block.shape != (8, 8): continue

            dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
            for pos in [(3,3), (4,4)]:
                if bit_idx >= len(bits): break
                coeff = int(np.round(dct_block[pos]))
                coeff_bin = list(format((coeff + 256) % 256, '08b'))
                coeff_bin[-1] = bits[bit_idx]
                new_coeff = int("".join(coeff_bin), 2)
                if coeff < 0: new_coeff = -new_coeff
                dct_block[pos] = new_coeff
                bit_idx += 1

            idct_block = idct(idct(dct_block.T, norm='ortho').T, norm='ortho')
            stego_image[row:row+8, col:col+8] = np.clip(np.round(idct_block), 0, 255)

    return stego_image.astype(np.uint8)

# Create clean image and embed
image = np.full((512, 512), 180, dtype=np.uint8)
message = "Harmik Sarvaliya 230317"
stego = embed_text_dct(image, message)
cv2.imwrite("stego_fixed.png", stego)
