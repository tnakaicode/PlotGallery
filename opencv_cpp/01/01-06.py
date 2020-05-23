import cv2
import numpy as np

img_src = cv2.imread('01-12.jpg', 1)
img_dst = img_src.copy()
img_gray = cv2.cvtColor(img_src, cv2.COLOR_BGR2GRAY)

img_edge = cv2.Canny(img_gray, 200, 200)

lines = cv2.HoughLines(img_edge, 1, np.pi/180, 120)

rows, cols = img_dst.shape[:2]

for rho, theta in lines[:, 0]:
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a*rho
    y0 = b*rho
    cv2.line(img_dst,
	(int(x0 - cols*(b)), int(y0 + cols*(a))), 
	(int(x0 + cols*(b)), int(y0 - cols*(a))), 
	(0, 0, 255), 2)

cv2.imshow('src', img_src)
cv2.imshow('edge', img_edge)
cv2.imshow('dst', img_dst)
cv2.waitKey(0)
cv2.destroyAllWindows()
