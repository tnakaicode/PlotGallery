import cv2

img = cv2.imread('data_block.jpg')
cv2.imshow('img', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
