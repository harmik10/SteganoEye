from PIL import Image

# Open both images
img1 = Image.open("C:/Users/harmik patel/Desktop/8K W/wallpaperflare.com_wallpaper (17).jpg")
img2 = Image.open("C:/Users/harmik patel/Desktop/8K W/wallpaperflare.com_wallpaper (18).jpg")

# Ensure both images are the same size and mode
img1 = img1.resize((700, 400)).convert("RGBA")
img2 = img2.resize((700, 400)).convert("RGBA")

# Blend the images
blended_img = Image.blend(img1, img2, alpha=0.5)

# Show the blended image
blended_img.show()
