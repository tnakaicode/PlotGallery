import cv2

img_src = cv2.imread('01-06.jpg', 1)
img_gray = cv2.cvtColor(img_src, cv2.COLOR_BGR2GRAY)
img_dst = img_src.copy()

corners = cv2.goodFeaturesToTrack(img_gray, 1000, 0.1, 5)

for i in corners:
    x,y = i.ravel()
    cv2.circle(img_dst, (x,y), 3, (0, 0, 255), 2)

cv2.imshow('src', img_src)
cv2.imshow('dst', img_dst)

cv2.waitKey(0)
cv2.destroyAllWindows()
