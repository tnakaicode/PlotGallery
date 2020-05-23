import cv2
import numpy as np

FLOW_W = 10
FLOW_H = 10

img_pre = cv2.imread('03-02-a.jpg', 1)
img_now = cv2.imread('03-02-b.jpg', 1)

img_pre_g = cv2.cvtColor(img_pre, cv2.COLOR_BGR2GRAY)
img_now_g = cv2.cvtColor(img_now, cv2.COLOR_BGR2GRAY)

rows, cols, ch = img_now.shape

ps = np.empty((0, 2), np.float32)

for y in range(0, cols, FLOW_H):
	for x in range(0, rows, FLOW_W):
		pp = np.array([[y, x]], np.float32)
		ps = np.vstack((ps, pp))

pe, status, error = cv2.calcOpticalFlowPyrLK(img_pre_g, img_now_g, ps, None)

for i in range(len(ps)):
	cv2.line(img_now, (ps[i][0], ps[i][1]) , (pe[i][0], pe[i][1]), (0, 0, 255), 2)

cv2.imshow('opticalflow', img_now)
cv2.waitKey(0)
cv2.destroyAllWindows()
