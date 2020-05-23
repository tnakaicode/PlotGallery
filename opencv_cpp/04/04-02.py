import cv2
import numpy as np

img_src = cv2.imread('04-02-a.jpg', 1)
img_template = cv2.imread('04-02-b.jpg', 1)

img_dst = img_src.copy()

h, w, ch = img_template.shape
img_minmax = cv2.matchTemplate(img_src, img_template, cv2.TM_CCOEFF_NORMED)
min_val, max_val, min_pt, max_pt = cv2.minMaxLoc(img_minmax)
cv2.rectangle(img_dst, max_pt, (max_pt[0] + w, max_pt[1] + h), (255, 255, 255), 10)

cv2.imshow('src', img_src)
cv2.imshow('template', img_template)
cv2.imshow('minmax', img_minmax)
cv2.imshow('dst', img_dst)

cv2.waitKey(0)
cv2.destroyAllWindows()
