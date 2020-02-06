import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import cv2
from PIL import Image, ImageDraw


def cv_fourcc(c1, c2, c3, c4):
    return (ord(c1) & 255) + ((ord(c2) & 255) << 8) + \
        ((ord(c3) & 255) << 16) + ((ord(c4) & 255) << 24)


#OUT_FILE_NAME = "output_video.mp4"
OUT_FILE_NAME = "output_video.avi"
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
dst = cv2.imread('./img/20200206130933.png')  # 一度、savefigしてから再読み込み
rows, cols, channels = dst.shape
out = cv2.VideoWriter(OUT_FILE_NAME, int(
    fourcc), int(10), (int(cols), int(rows)))
# out = cv2.VideoWriter(OUT_FILE_NAME, cv_fourcc('X', 'V', 'I', 'D'), 30, (cols, rows), True)  #avi

x = np.arange(0, 10, 0.1)
fig = plt.figure(figsize=(12, 8))
ax1 = fig.add_subplot(221)
ax2 = fig.add_subplot(222)
ax3 = fig.add_subplot(224)
ax4 = fig.add_subplot(223)
ax1.axis([0, 10, -1.2, 1.2])
ax2.axis([0, 100, 0, 100])
ax3.axis([-1.2, 1.2, 0, 10])
ax4.axis([0, 100, 0, 100])


def f(x, y):
    return np.sin(x) + np.cos(y)


x1 = np.linspace(0, 2 * np.pi, 100)
y1 = np.linspace(0, 2 * np.pi, 100).reshape(-1, 1)
ims = []
images = []
for a in range(10):
    fig.delaxes(ax1)
    fig.delaxes(ax3)
    ax1 = fig.add_subplot(221)
    ax3 = fig.add_subplot(224)
    y = np.sin(x - a)
    line, = ax1.plot(x, y, "r")
    ims.append([line])
    line, = ax3.plot(y, x, "r")
    ims.append([line])

    x1 += np.pi / 15.
    y1 += np.pi / 20.
    im = ax2.imshow(f(x1, y1), animated=True)
    ims.append([im])
    im = ax4.pcolormesh(f(x1, y1), cmap='hsv')
    ims.append([im])

    fig1 = plt.pause(0.001)
    # Gifアニメーションのために画像をためます
    plt.savefig("img/image" + str(a) + ".png")
    dst = cv2.imread('img/image' + str(a) + '.png')
    out.write(dst)  # mp4やaviに出力します
