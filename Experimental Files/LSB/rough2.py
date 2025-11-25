from PIL import Image

def binary_to_message(binary_data):
    message = ''
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        if byte == '11111110':  # End marker
            break
        message += chr(int(byte, 2))
    return message

def extract_message_lsb(image_path):
    try:
        img = Image.open(image_path).convert('RGB')
    except Exception as e:
        print(f"Error opening image: {e}")
        return

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
    print("->", message)

# 🔹 Main: take user input
if __name__ == "__main__":
    image_path = input("Enter the path of the image to extract the message from: ").strip()
    extract_message_lsb(image_path)
