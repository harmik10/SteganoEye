from PIL import Image

def message_to_binary(message):
    return ''.join([format(ord(char), '08b') for char in message])

def hide_message_lsb(image_path, message, output_path='stego_image.png'):
    img = Image.open(image_path).convert('RGB')
    pixels = img.load()

    width, height = img.size
    binary_message = message_to_binary(message) + '1111111111111110'  # 16-bit end marker
    data_index = 0
    msg_len = len(binary_message)

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

    img.save(output_path)
    print(f"Message hidden successfully in '{output_path}'")

#Input the message here
message = input("Enter the message you want to hide: ")
hide_message_lsb("b1.jpg", message)
