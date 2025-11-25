from PIL import Image
image = Image.new("img1.jpg")
image.show()
image = image.convert("L")  # Convert to grayscale
image.save("img1_gray.jpg")  # Save the grayscale image
