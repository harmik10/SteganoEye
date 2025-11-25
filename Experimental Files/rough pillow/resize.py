from PIL import Image

img=Image.open('img1.jpg')
print(img.width,img.height)
img.show()
img=img.resize((int(img.width/2),int(img.height/2)), resample=Image.LANCZOS,box=(20, 20, 200, 900)) 
img.show()