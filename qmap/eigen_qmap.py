import SimpleQmap as sq
import numpy as np
import matplotlib.pyplot as plt

twopi = 2.0 * np.pi


def qnum_index(uevecs, bchevecs):
    index = []
    duplicate = False
    idx = None
    for bchvec in bchevecs:
        ovl2 = np.array([bchvec.inner(uvec).abs2() for uvec in uevecs])
        idx = ovl2.argmax()
        while idx in index:
            ovl2 = np.delete(ovl2, idx)
            try:
                idx = ovl2.argmax()
            except ValueError:
                findex = set(np.arange(len(bchevecs)))
                sindex = set(index)
                diff = list(findex - sindex)[0]
                index.append(diff)
                break
        index.append(idx)
    return index


dim = 30
k = 1
qmin, qmax = -np.pi, np.pi
pmin, pmax = -np.pi, np.pi

domain = np.array([[qmin, qmax], [pmin, pmax]])

Hsol = sq.SplitHamiltonian(dim, domain)
Usol = sq.SplitUnitary(dim, domain)


def T(x): return x**2 / 2
def V(x): return np.cos(x)


mat = Usol.TVmatrix(T, V)
uevals, uevecs = mat.eig()
hbar = Hsol.hbar
matT = Hsol.matTqrep(T)
matV = Hsol.matVqrep(V)
matH = matT + matV + (matT * matV - matV * matT) / 2 * (-1.j / hbar)
bchevals, bchevecs = matH.eigh()

index = qnum_index(uevecs, bchevecs)
uevals = uevals[index]
uevecs = [uevecs[i] for i in index]


from SimpleQmap.utility import hsm_axes
fig = plt.figure()
ax1, ax2, ax3 = hsm_axes(fig)
ax = [ax1, ax2, ax3]

plt.ion()

x = np.linspace(domain[0, 0], domain[0, 1], 100)
y = np.linspace(domain[1, 0], domain[1, 1], 100)
Q, P = np.meshgrid(x, y)

for i, vec in enumerate(uevecs):

    #vec = sq.State(scaleinfo, vec)

    x, y, z = vec.hsmrep()
    ax[0].contourf(x, y, z, cmap=plt.cm.Oranges)

    q = vec.x[0]
    ax[1].plot(q, vec.abs2(), "-")
    ax[1].semilogy()
    ax[1].set_ylim(1e-30, 1)

    p = vec.x[1]
    prep = vec.prep().abs2()
    ax[2].plot(prep, q, "-")
    ax[2].semilogx()
    ax[2].set_xlim(1e-30, 1)

    fig.suptitle("%d-th eigenstate" % i)
fig.savefig("./eigen_qmap.png")