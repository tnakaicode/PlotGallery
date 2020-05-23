import cv2
import numpy as np

win_src = 'src'
win_bin = 'bin'

cap = cv2.VideoCapture(0)
ret, img_src = cap.read()
h, w, ch = img_src.shape

div = 5
rct = (0, 0, int(w / div), int(h / div))

cv2.namedWindow(win_src, cv2.WINDOW_NORMAL)
cv2.namedWindow(win_bin, cv2.WINDOW_NORMAL)

cri = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 10, 1)

while(True):
    th = 220
    ret, img_src = cap.read()
    bgr = cv2.split(img_src)
    ret, img_bin = cv2.threshold(bgr[2], th, 255, cv2.THRESH_BINARY)
   
    ret, rct = cv2.meanShift(img_bin, rct, cri)
    x, y, w, h = rct
    img_src = cv2.rectangle(img_src, (x, y), (x + w, y + h), (255, 0, 0), 3)

    cv2.imshow(win_src, img_src)
    cv2.imshow(win_bin, img_bin)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
