import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
import time
import sys


def step(x, sigma):
    cov = np.diag(sigma)
    dt = 0.1
    x = x + dt * np.random.multivariate_normal([0, 0], cov, 20)
    return x


def draw(t):
    plt.clf()
    plt.suptitle(f"t={t}")
    ax = plt.gca()
    ax.scatter(x[:10, 0], x[:10, 1], c="black", s=10)
    ax.plot(x[10:20, 0], x[10:20, 1], "r^")
    for i in range(10):
        c = patches.Circle(xy=x[i], radius=0.05, fc='grey', alpha=0.1)
        ax.add_patch(c)
        c = patches.Circle(xy=x[i + 10], radius=0.05, fc='pink', alpha=0.2)
        ax.add_patch(c)

    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_aspect('equal')
    plt.pause(0.01)


class Brown (object):

    def __init__(self, x, sigma):
        self.fig, self.axs = plt.subplots()
        self.x = x

        n_iter = 100
        self.sigma = sigma
        self.x = step(self.x, self.sigma)

    def draw_initial(self):
        t = 0
        self.text = self.fig.suptitle(f"t={t}")
        self.scat = self.axs.scatter(
            self.x[:10, 0], self.x[:10, 1], c="black", s=10)
        self.line, = self.axs.plot(self.x[10:20, 0], self.x[10:20, 1], "r^")
        self.cs = []
        for i in range(10):
            c = patches.Circle(xy=self.x[i], radius=0.05, fc='grey', alpha=0.1)
            self.axs.add_patch(c)
            self.cs.append(c)
        for i in range(10):
            c = patches.Circle(xy=self.x[i + 10],
                               radius=0.05, fc='pink', alpha=0.2)
            self.axs.add_patch(c)
            self.cs.append(c)

        self.axs.set_xlim(-1, 1)
        self.axs.set_ylim(-1, 1)
        self.axs.set_aspect('equal')
        return

    def animate(self, t):
        self.x = step(self.x, self.sigma)

        self.text.set_text(f"t={t}")
        self.scat.set_offsets(self.x[:10, :])
        self.line.set_data(self.x[10:20, 0], x[10:20, 1])
        for i in range(20):
            self.cs[i].center = self.x[i]

        sys.stdout.write(f"\r{t}")
        sys.stdout.flush()
        return


if __name__ == '__main__':
    n_iter = 100
    sigma = np.full(2, 0.1 / 3)

    x = np.zeros((20, 2))
    x = step(x, sigma)

    start = time.time()
    # fig, ax = plt.subplots()
    # for t in range(n_iter):
    #    x = step(x, sigma)
    #    draw(t)
    elapsed_time1 = time.time() - start

    start2 = time.time()

    x = np.zeros((20, 2))
    x = step(x, sigma)

    obj = Brown(x, sigma)
    ani = animation.FuncAnimation(obj.fig, obj.animate,
                                  frames=range(0, n_iter),
                                  init_func=obj.draw_initial,
                                  save_count=1, repeat=False)
    ani.save("./brown.gif", writer="Pillow")
    elapsed_time2 = time.time() - start2

    print()
    print(f"t1: {elapsed_time1}")
    print(f"t2: {elapsed_time2}")
