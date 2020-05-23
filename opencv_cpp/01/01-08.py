import cv2
import numpy as np

img_src = cv2.imread('01-13.jpg', 1)
img_dst = img_src.copy()
img_gray = cv2.cvtColor(img_src, cv2.COLOR_BGR2GRAY)

img_edge = cv2.Canny(img_gray, 80, 120)

circles = cv2.HoughCircles(img_edge, cv2.HOUGH_GRADIENT, 50, 100)

for x, y, r in circles[0,:]:
    cv2.circle(img_dst, (x, y), r, (0, 0, 255), 3)

cv2.imshow('src', img_src)
cv2.imshow('edge', img_edge)
cv2.imshow('dst', img_dst)
cv2.waitKey(0)
cv2.destroyAllWindows()
