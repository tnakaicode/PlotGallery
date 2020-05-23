import cv2

FLOW_W = 10
FLOW_H = 10

img_pre = cv2.imread('03-02-a.jpg', 1)
img_now = cv2.imread('03-02-b.jpg', 1)

img_pre_g = cv2.cvtColor(img_pre, cv2.COLOR_BGR2GRAY)
img_now_g = cv2.cvtColor(img_now, cv2.COLOR_BGR2GRAY)

flow = cv2.calcOpticalFlowFarneback(img_pre_g, img_now_g, None, 0.5, 3, 30, 3, 3, 1.1, 0)

rows, cols, ch = img_now.shape

for y in range(0, cols, FLOW_H):
	for x in range(0, rows, FLOW_W):
		ps = (y, x)
		pe = (ps[0] + int(flow[x][y][0]), ps[1] + int(flow[x][y][1]))
		cv2.line(img_now, ps, pe, (0, 0, 255), 2)

cv2.imshow('opticalflow', img_now)
cv2.waitKey(0)
cv2.destroyAllWindows()
