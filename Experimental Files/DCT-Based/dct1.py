import numpy as np
import cv2
import matplotlib.pyplot as plt

# Create a 2x2 grayscale image
gray_img = np.array([[ [ 152,  155,  161,  166,  170],
  [ 163,  159,  155,  190, 109],
  [ 185, 104, 114, 120, 121],
  [102, 123, 126, 130, 134],
  [120, 130, 140, 150, 160] ]
], dtype=np.uint8)

# Show image
plt.imshow(gray_img, cmap='gray')
plt.title("Grayscale Image")
plt.show()
