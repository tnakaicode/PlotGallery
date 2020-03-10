#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ArtistAnimationを用いて、mp4,gif動画を作成するプログラム
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def create_movie(show_fig=True, save_mp4=False, save_gif=False):
    fig = plt.figure()
    ax = []
    ims = []

    for i in range(6):
        ax.append(fig.add_subplot(3, 2, i + 1))

    x = np.arange(0, 10, 0.1)
    y = np.arange(0, 10, 0.1)
    t = np.arange(0, 20, 1)
    mx = np.arange(0, 10)
    my = np.arange(0, 10)
    X, Y = np.meshgrid(mx, my)

    first = True

    for _t in t:
        # subplot1: 折れ線+補助線
        y1 = np.sin(x - _t)
        y2 = np.cos(x - _t)
        im = ax[0].plot(x, y1, "r", label="sin")
        im += ax[0].plot(x, y2, "b", label="cos")
        im += [ax[0].hlines([0], 0, 10, "g",
                            linestyle="dotted", linewidth=0.5)]
        if first is True:
            ax[0].legend()
            ax[0].set_xlim(0, 10)
            ax[0].set_ylim(-1, 1)

        # subplot2: 散布図
        _x = np.random.normal(1, 1, 100)
        _y = np.random.normal(1, 1, 100)
        im += [ax[1].scatter(_x, _y, c="r", alpha=0.1, marker=".")]
        _x = np.random.normal(-1, 1, 100)
        _y = np.random.normal(-1, 1, 100)
        im += [ax[1].scatter(_x, _y, c="b", alpha=0.1, marker=".")]
        if first is True:
            ax[1].set_xlim(-5, 5)
            ax[1].set_ylim(-5, 5)

        # subplot3: ヒストグラム
        _x = np.random.normal(50, 10, 1000)
        n, bin, patch = ax[2].hist(_x, color="g")
        im += patch

        # subplot4: 棒グラフ
        _x = np.arange(10)
        _y = np.mod(_x - _t, 10)
        im += ax[3].bar(_x, _y, color="b")

        # subplot5: 円グラフ
        _x = np.random.rand(5)
        patch, text = ax[4].pie(_x, colors=["r", "g", "b", "y", "c"])
        im += patch

        # subplot6: ヒートマップ
        _z = np.cos(X - _t) + np.cos(Y - _t)
        p = ax[5].pcolor(X, Y, _z)
        im += [p]

        if first is True:
            fig.colorbar(p, ax=ax[5])

        ims.append(im)
        first = False

    ani = animation.ArtistAnimation(fig, ims, interval=100)

    if show_fig is True:
        plt.show()
    if save_mp4 is True:
        # mp4での保存にはffpmegのパスが通っている必要がある
        ani.save("plot.mp4", writer="ffmpeg", dpi=300)
    if save_gif is True:
        # gifでの保存にはmatplotlibにimagemagickのパスが通っている必要がある
        ani.save("plot.gif", writer="imagemagick")


if __name__ == "__main__":
    # print(matplotlib.matplotlib_fname())  # matplotlibの設定ファイル確認用
    create_movie(False, True, True)
