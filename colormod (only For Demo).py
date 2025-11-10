from PIL import Image
import os

# Ask user to input the image path
image_path = input("Enter image file path: ").strip()

# Check if file exists
if not os.path.isfile(image_path):
    print("❌ File not found. Please check the path and try again.")
else:
    try:
        # Open image with PIL
        img = Image.open(image_path)

        # Show details
        print("\n✅ Image loaded successfully!")
        print("File:", image_path)
        print("Format:", img.format)     # e.g., PNG, JPEG
        print("Size (width x height):", img.size)
        print("Color Mode:", img.mode)   # e.g., RGB, RGBA, L, P

    except Exception as e:
        print("❌ Error reading image:", e)
