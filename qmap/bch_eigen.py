import SimpleQmap as sq
import numpy as np
import matplotlib.pyplot as plt
twopi = 2.0 * np.pi


def bchHamitonianTerm(x, y, order):
    if order == 1:
        return x + y
    elif order == 2:
        return (x * y - y * x) / 2
    elif order == 3:
        return x * x * y / 12 - x * y * x / 6 + x * y * y / 12 + y * x * x / 12 - y * x * y / 6 + y * y * x / 12
    elif order == 4:
        return x * x * y * y / 24 - x * y * x * y / 12 + y * x * y * x / 12 - y * y * x * x / 24
    elif order == 5:
        return (
            - x * x * x * x * y / 720 + x * x * x * y * x / 180 + x * x * x * y * y / 180 - x * x * y * x * x / 120 - x * x * y * x * y / 120 - x * x * y * y * x / 120 +
            x * x * y * y * y / 180 + x * y * x * x * x / 180 - x * y * x * x * y / 120 + x * y * x * y * x / 30 - x * y * x * y * y / 120 - x * y * y * x * x / 120 - x * y * y * x * y / 120 +
            x * y * y * y * x / 180 - x * y * y * y * y / 720 - y * x * x * x * x / 720 + y * x * x * x * y / 180 - y * x * x * y * x / 120 - y * x * x * y * y / 120 - y * x * y * x * x / 120 +
            y * x * y * x * y / 30 - y * x * y * y * x / 120 + y * x * y * y * y / 180 + y * y * x * x * x / 180 - y * y * x * x * y / 120 - y * y * x * y * x / 120 - y * y * x * y * y / 120 +
            y * y * y * x * x / 180 + y * y * y * x * y / 180 - y * y * y * y * x / 720
        )
    else:
        raise ValueError("order > 6 does not implement")


def bchHamiltonian(matT, matV, order):
    s = (-1.j / matT.hbar)
    x = matT
    y = matV
    return sum([s**(i - 1) * bchHamitonianTerm(x, y, i) for i in range(1, order + 1)])


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


def T(x): return x**2 / 2
def V(x): return np.cos(x)


dim = 50
k = 1
qrange = [-np.pi, np.pi]
prange = [-np.pi, np.pi]

domain = np.array([qrange, prange])

Hsol = sq.SplitHamiltonian(dim, domain)
matT = Hsol.matTqrep(T)
matV = Hsol.matVqrep(V)

bchHam = bchHamiltonian(matT, matV, 2)
bchevals, bchevecs = bchHam.eigh()


Usol = sq.SplitUnitary(dim, domain)
U = Usol.TVmatrix(T, V)
uevals, uevecs = U.eig()

index = qnum_index(uevecs, bchevecs)

uevals = uevals[index]
uevecs = [uevecs[i] for i in index]

x = np.linspace(domain[0, 0], domain[0, 1], 100)
y = np.linspace(domain[1, 0], domain[1, 1], 100)
Q, P = np.meshgrid(x, y)

from SimpleQmap.utility import hsm_axes

fig = plt.figure()
ax1, ax2, ax3 = hsm_axes(fig)
ax = [ax1, ax2, ax3]

plt.ion()
for i in range(dim):
    evec = uevecs[i]
    bchvec = bchevecs[i]

    #x,y,z = evec.hsmrep()
    x, y, z = bchvec.hsmrep()
    ax[0].contourf(x, y, z, cmap=plt.cm.Oranges)

    q = evec.x[0]
    ax[1].plot(q, evec.abs2(), "-")
    ax[1].plot(q, bchvec.abs2(), "-")
    ax[1].semilogy()
    ax[1].set_ylim(1e-35, 1)

    p = evec.x[1]
    prep = evec.prep().abs2()
    bchprep = bchvec.prep().abs2()
    ax[2].plot(prep, q, "-")
    ax[2].plot(bchprep, q, "-")
    ax[2].semilogx()
    ax[2].set_xlim(1e-35, 1)

    norm = evec.inner(bchvec).abs2()
    fig.suptitle(
        r"%d-th eigenstate, $|\langle \Psi_n|J_n^{(bch)}\rangle|^2$=%f" % (i, norm))
fig.savefig("./bch_eigen.png")