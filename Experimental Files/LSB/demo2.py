from PIL import Image

def binary_to_message(binary_data):
    end_marker = '1111111111111110'  # 16-bit end marker
    end_index = binary_data.find(end_marker)
    if end_index != -1:
        binary_data = binary_data[:end_index]

    message = ''
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        if len(byte) == 8:
            message += chr(int(byte, 2))
    return message

def extract_message_lsb(image_path):
    img = Image.open(image_path).convert('RGB')
    pixels = img.load()
    width, height = img.size

    binary_data = ''
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            binary_data += str(r & 1)
            binary_data += str(g & 1)
            binary_data += str(b & 1)

    message = binary_to_message(binary_data)
    print("Hidden message extracted:")
    print(message)

#Input the image file name from user
image_path = input("Enter the path of the stego image (e.g., stego_image.png): ")
extract_message_lsb(image_path)
