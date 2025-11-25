from PIL import Image
img=Image.open('img1.jpg')
img=img.rotate(40, expand=True, resample=Image.BICUBIC,fillcolor='green')
img.show()