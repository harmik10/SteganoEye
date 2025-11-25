'''
Author: Mason Edgar
ECE 529 - Algorithm Project
Image Steganography
'''
#------ External Libraries ------#
import cv2
import struct
import bitstring
import numpy as np
import zigzag as zz
#================================#
#---------- Source Files --------#
import image_preparation as img
import data_embedding as stego
#================================#

NUM_CHANNELS = 3
COVER_IMAGE_FILEPATH  = "./your_carrier_image.png"  # Cover image (PNG recommended)
STEGO_IMAGE_FILEPATH  = "./stego_image.png"
SECRET_MESSAGE_STRING = "Input your secret message here"

# ============================================================================= #
# =========================== BEGIN CODE OPERATION ============================ #
# ============================================================================= #

# Load and pad cover image to be 8x8 compliant
raw_cover_image = cv2.imread(COVER_IMAGE_FILEPATH, flags=cv2.IMREAD_COLOR)
height, width = raw_cover_image.shape[:2]

while height % 8 != 0:
    height += 1
while width % 8 != 0:
    width += 1

valid_dim = (width, height)
padded_image = cv2.resize(raw_cover_image, valid_dim)
cover_image_f32 = np.float32(padded_image)

# Convert to YCrCb and separate channels
cover_image_YCC = img.YCC_Image(cv2.cvtColor(cover_image_f32, cv2.COLOR_BGR2YCrCb))

# Placeholder for stego image
stego_image = np.empty_like(cover_image_f32)

for chan_index in range(NUM_CHANNELS):
    # ---------- DCT Stage ----------
    dct_blocks = [cv2.dct(block) for block in cover_image_YCC.channels[chan_index]]

    # ---------- Quantization ----------
    dct_quants = [np.around(np.divide(block, img.JPEG_STD_LUM_QUANT_TABLE)) for block in dct_blocks]

    # ---------- ZigZag Sorting ----------
    sorted_coefficients = [zz.zigzag(block) for block in dct_quants]

    # ---------- Embedding Stage ----------
    if chan_index == 0:  # Luminance (Y) channel
        # Convert secret message to bitstream
        secret_data_bits = bitstring.BitArray()
        for char in SECRET_MESSAGE_STRING.encode('ascii'):
            secret_data_bits.append(bitstring.pack('uint:8', char))
        # You can also add a terminator marker if needed, e.g., 8 bits: 11111110 (254)
        secret_data_bits.append('0b11111110')

        # Embed into DCT coefficients
        embedded_dct_blocks = stego.embed_encoded_data_into_DCT(secret_data_bits.bin, sorted_coefficients)
        desorted_coefficients = [zz.inverse_zigzag(block, vmax=8, hmax=8) for block in embedded_dct_blocks]
    else:
        # No data embedding on Cr and Cb; just reorder coefficients
        desorted_coefficients = [zz.inverse_zigzag(block, vmax=8, hmax=8) for block in sorted_coefficients]

    # ---------- Dequantization ----------
    dct_dequants = [np.multiply(block, img.JPEG_STD_LUM_QUANT_TABLE) for block in desorted_coefficients]

    # ---------- Inverse DCT ----------
    idct_blocks = [cv2.idct(block) for block in dct_dequants]

    # ---------- Reconstruct Channel ----------
    stego_image[:, :, chan_index] = np.asarray(img.stitch_8x8_blocks_back_together(cover_image_YCC.width, idct_blocks))

# Convert back to BGR and clamp
stego_image_BGR = cv2.cvtColor(stego_image, cv2.COLOR_YCR_CB2BGR)
final_stego_image = np.uint8(np.clip(stego_image_BGR, 0, 255))

# Save output
cv2.imwrite(STEGO_IMAGE_FILEPATH, final_stego_image)
print("✅ Stego image saved successfully at:", STEGO_IMAGE_FILEPATH)
