import cv2

img = cv2.imread('data/block.jpg')
height = img.shape[0]
width = img.shape[1]
resized_img = cv2.resize(img, (int(width/2), height))
cv2.imwrite('resized.jpg', resized_img)

gray_img = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
cv2.imwrite('gray.jpg', gray_img)

canny_img = cv2.Canny(img, 50, 100)
cv2.imwrite('canny.jpg', canny_img)
