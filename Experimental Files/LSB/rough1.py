import os
from PIL import Image

def message_to_binary(message):
    return ''.join(format(ord(char), '08b') for char in message)

def generate_dynamic_filename(original_path, suffix="_stego", extension=".png"):
    base = os.path.splitext(os.path.basename(original_path))[0]
    directory = os.path.dirname(original_path) or '.'
    filename = f"{base}{suffix}{extension}"
    full_path = os.path.join(directory, filename)
    
    counter = 1
    while os.path.exists(full_path):
        filename = f"{base}{suffix}_{counter}{extension}"
        full_path = os.path.join(directory, filename)
        counter += 1
    return full_path

def hide_message_lsb(image_path, message, output_path=None):
    try:
        img = Image.open(image_path).convert('RGB')
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    pixels = img.load()
    width, height = img.size

    binary_message = message_to_binary(message) + '11111110'  # 8-bit end marker
    msg_len = len(binary_message)
    data_index = 0

    for y in range(height):
        for x in range(width):
            if data_index >= msg_len:
                break
            r, g, b = pixels[x, y]
            if data_index < msg_len:
                r = (r & ~1) | int(binary_message[data_index])
                data_index += 1
            if data_index < msg_len:
                g = (g & ~1) | int(binary_message[data_index])
                data_index += 1
            if data_index < msg_len:
                b = (b & ~1) | int(binary_message[data_index])
                data_index += 1
            pixels[x, y] = (r, g, b)
        if data_index >= msg_len:
            break

    if output_path is None:
        output_path = generate_dynamic_filename(image_path)

    img.save(output_path)
    print(f"Message hidden successfully in: {output_path}")

# 🔹 Main: take user input
if __name__ == "__main__":
    image_path = input("Enter the image path: ").strip()
    message = input("Enter the secret message to hide: ").strip()
    hide_message_lsb(image_path, message)
