import cv2
import numpy as np
import zigzag
import os

# Standard JPEG quantization table (Luminance)
QUANTIZATION_TABLE = np.array([
    [16, 11, 10, 16, 24, 40, 51, 61],
    [12, 12, 14, 19, 26, 58, 60, 55],
    [14, 13, 16, 24, 40, 57, 69, 56],
    [14, 17, 22, 29, 51, 87, 80, 62],
    [18, 22, 37, 56, 68, 109, 103, 77],
    [24, 35, 55, 64, 81, 104, 113, 92],
    [49, 64, 78, 87, 103, 121, 120, 101],
    [72, 92, 95, 98, 112, 100, 103, 99]
])

def to_bitstream(file_path):
    """Read a file and convert it to a bitstream."""
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
    return ''.join(format(byte, '08b') for byte in file_bytes)

def bytes_to_file(bitstream, output_path):
    """Convert a bitstream back to bytes and write to a file."""
    byte_array = bytearray()
    for i in range(0, len(bitstream), 8):
        byte = bitstream[i:i+8]
        if len(byte) < 8:
            # Ignore padding if not a full byte
            continue
        byte_array.append(int(byte, 2))
    with open(output_path, 'wb') as f:
        f.write(byte_array)

def embed_data(cover_image_path, secret_file_path, stego_image_path):
    """Embeds a secret file into a cover image using DCT."""
    # 1. Read and Prepare Cover Image
    if not os.path.exists(cover_image_path):
        raise FileNotFoundError(f"Cover image not found at {cover_image_path}")
    cover_image = cv2.imread(cover_image_path, cv2.IMREAD_COLOR)
    if cover_image is None:
        raise ValueError("Failed to read the cover image.")

    height, width, _ = cover_image.shape
    # Pad dimensions to be multiple of 8
    new_height = (height + 7) & ~7
    new_width = (width + 7) & ~7
    padded_image = np.zeros((new_height, new_width, 3), dtype=np.uint8)
    padded_image[0:height, 0:width] = cover_image

    cover_image_f32 = np.float32(padded_image)
    cover_image_YCC = cv2.cvtColor(cover_image_f32, cv2.COLOR_BGR2YCrCb)
    y_channel, cr_channel, cb_channel = cv2.split(cover_image_YCC)

    # 2. Prepare Secret Data
    if not os.path.exists(secret_file_path):
        raise FileNotFoundError(f"Secret file not found at {secret_file_path}")
    secret_bitstream = to_bitstream(secret_file_path)
    data_len_bitstream = format(len(secret_bitstream), '032b')
    total_bitstream = data_len_bitstream + secret_bitstream

    # Check if the image is large enough
    max_embeddable_bits = (new_width // 8) * (new_height // 8) * 63  # 63 AC coeffs per block
    if len(total_bitstream) > max_embeddable_bits:
        raise ValueError("Image is too small to hold the secret file.")

    # 3. Iterate and Embed
    bit_index = 0
    embedded_y_channel = np.zeros_like(y_channel)
    for r in range(0, new_height, 8):
        for c in range(0, new_width, 8):
            block = y_channel[r:r+8, c:c+8]
            dct_block = cv2.dct(block)
            quant_block = np.round(dct_block / QUANTIZATION_TABLE)
            zz_quant_block = zigzag.zigzag(quant_block)

            # Embed data in AC coefficients
            for i in range(1, 64):  # Skip DC coefficient at index 0
                if bit_index < len(total_bitstream):
                    coeff = int(zz_quant_block[i])
                    # LSB modification
                    new_coeff = (coeff & ~1) | int(total_bitstream[bit_index])
                    zz_quant_block[i] = new_coeff
                    bit_index += 1
                else:
                    break
            
            if bit_index >= len(total_bitstream) and bit_index % 8 != 0:
                # Pad with zeros to make it a full byte, helps in extraction
                while bit_index % 8 != 0:
                    zz_quant_block[bit_index % 63 + 1] = (int(zz_quant_block[bit_index % 63 + 1]) & ~1)
                    bit_index += 1


            # Reverse the process
            inv_zz_block = zigzag.inverse_zigzag(zz_quant_block, 8, 8)
            dequant_block = inv_zz_block * QUANTIZATION_TABLE
            idct_block = cv2.idct(dequant_block)
            embedded_y_channel[r:r+8, c:c+8] = idct_block

    # 4. Reconstruct and Save Image
    stego_image_YCC = cv2.merge([embedded_y_channel, cr_channel, cb_channel])
    stego_image_BGR = cv2.cvtColor(stego_image_YCC, cv2.COLOR_YCrCb2BGR)
    
    # Un-pad the image
    stego_image_BGR = stego_image_BGR[0:height, 0:width]

    final_stego_image = np.uint8(np.clip(stego_image_BGR, 0, 255))
    cv2.imwrite(stego_image_path, final_stego_image)
    print(f"✅ Secret data embedded successfully into '{stego_image_path}'")

def extract_data(stego_image_path, output_file_path):
    """Extracts a secret file from a stego image."""
    # 1. Read and Prepare Stego Image
    if not os.path.exists(stego_image_path):
        raise FileNotFoundError(f"Stego image not found at {stego_image_path}")
    stego_image = cv2.imread(stego_image_path, cv2.IMREAD_COLOR)
    if stego_image is None:
        raise ValueError("Failed to read the stego image.")

    stego_image_f32 = np.float32(stego_image)
    stego_image_YCC = cv2.cvtColor(stego_image_f32, cv2.COLOR_BGR2YCrCb)
    y_channel, _, _ = cv2.split(stego_image_YCC)

    # 2. Iterate and Extract
    extracted_bits = ""
    data_len = -1
    extracted_len_bits = ""
    
    height, width = y_channel.shape
    
    done = False
    for r in range(0, height, 8):
        for c in range(0, width, 8):
            block = y_channel[r:r+8, c:c+8]
            dct_block = cv2.dct(block)
            quant_block = np.round(dct_block / QUANTIZATION_TABLE)
            zz_quant_block = zigzag.zigzag(quant_block)

            # Extract bits from AC coefficients
            for i in range(1, 64):
                coeff = int(zz_quant_block[i])
                extracted_bit = str(coeff & 1)

                if len(extracted_len_bits) < 32:
                    extracted_len_bits += extracted_bit
                    if len(extracted_len_bits) == 32:
                        data_len = int(extracted_len_bits, 2)
                elif len(extracted_bits) < data_len:
                    extracted_bits += extracted_bit
                else:
                    done = True
                    break
            if done:
                break
        if done:
            break

    if data_len == -1:
        raise ValueError("Could not determine the length of the hidden data.")

    # 3. Reconstruct File
    bytes_to_file(extracted_bits, output_file_path)
    print(f"✅ Secret data extracted successfully to '{output_file_path}'")

def main():
    """Main function to drive the steganography process."""
    while True:
        choice = input("Choose an option:\n1. Embed data\n2. Extract data\n3. Exit\nEnter choice (1, 2, or 3): ").strip()
        if choice == '1':
            cover_path = input("Enter the path to the cover image: ").strip()
            secret_path = input("Enter the path to the secret file: ").strip()
            stego_path = input("Enter the desired output path for the stego image: ").strip()
            try:
                embed_data(cover_path, secret_path, stego_path)
            except Exception as e:
                print(f"❌ An error occurred during embedding: {e}")
        elif choice == '2':
            stego_path = input("Enter the path to the stego image: ").strip()
            output_path = input("Enter the output path for the extracted file: ").strip()
            try:
                extract_data(stego_path, output_path)
            except Exception as e:
                print(f"❌ An error occurred during extraction: {e}")
        elif choice == '3':
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()