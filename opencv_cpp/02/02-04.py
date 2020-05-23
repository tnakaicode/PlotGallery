import numpy as np
import cv2

img_src1 = cv2.imread('02-02-a.jpg', 0)
img_src2 = cv2.imread('02-02-b.jpg', 0)

detector = cv2.AKAZE_create()
kpts1, desc1 = detector.detectAndCompute(img_src1, None)
kpts2, desc2 = detector.detectAndCompute(img_src2, None)

matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
matches = matcher.match(desc1, desc2)

h1, w1 = img_src1.shape
h2, w2 = img_src2.shape
img_dst = np.zeros((max(h1, h2), w1 + w2, 3), np.uint8)

cv2.drawMatches(img_src1, kpts1, img_src2, kpts2, matches, img_dst)
cv2.imshow('dst', img_dst)
cv2.waitKey(0)
cv2.destroyAllWindows()
