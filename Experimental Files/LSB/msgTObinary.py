
message = input("Enter the message you want to hide: ")

def message_to_binary(message):
    binary = ''
    for char in message:
        ascii_value = ord(char)
        binary_char = format(ascii_value, '08b')
        binary += binary_char
    return binary

print("Your message: ",message_to_binary(message))
 