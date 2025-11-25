from PIL import Image
import io

def image_to_binary(image_path):
    try:
        with Image.open(image_path) as img:
            # Save image into a bytes buffer
            with io.BytesIO() as buffer:
                img.save(buffer, format=img.format)  # Save in original format (e.g., PNG, JPEG)
                binary_data = buffer.getvalue()
                return binary_data
    except Exception as e:
        print(f"Error: {e}")
        return None

binary_data = image_to_binary("b1.jpg")  #input your image path here

if binary_data:
    print(f"Image converted to binary. Length: {len(binary_data)} bytes")
    print(binary_data[:100])  # Print first 100 bytes for preview
