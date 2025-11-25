from PIL import Image

img=Image.new('RGB', (700, 500),(50, 250, 230))
img.paste((255, 0, 0), (50, 50, 150, 150))
img.paste((0, 255, 0), (200, 50, 300, 150))

img.show()