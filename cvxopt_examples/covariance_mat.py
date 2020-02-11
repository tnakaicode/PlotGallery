import math
from cvxopt import matrix, spmatrix, log, mul, blas, lapack, amd, cholmod
from cvxopt import spmatrix, matrix, umfpack
from cvxopt.cholmod import options


def covsel(Y):
    """
    Returns the solution of

         minimize    -log det K + Tr(KY)
         subject to  K_{ij}=0,  (i,j) not in indices listed in I,J.

    Y is a symmetric sparse matrix with nonzero diagonal elements.
    I = Y.I,  J = Y.J.
    """

    I, J = Y.I, Y.J
    n, m = Y.size[0], len(I)
    N = I + J * n         # non-zero positions for one-argument indexing
    D = [k for k in range(m) if I[k] == J[k]]  # position of diagonal elements

    # starting point: symmetric identity with nonzero pattern I,J
    K = spmatrix(0.0, I, J)
    K[::n + 1] = 1.0

    # Kn is used in the line search
    Kn = spmatrix(0.0, I, J)

    # symbolic factorization of K
    F = cholmod.symbolic(K)

    # Kinv will be the inverse of K
    Kinv = matrix(0.0, (n, n))

    for iters in range(100):

        # numeric factorization of K
        cholmod.numeric(K, F)
        d = cholmod.diag(F)

        # compute Kinv by solving K*X = I
        Kinv[:] = 0.0
        Kinv[::n + 1] = 1.0
        cholmod.solve(F, Kinv)

        # solve Newton system
        grad = 2 * (Y.V - Kinv[N])
        hess = 2 * (mul(Kinv[I, J], Kinv[J, I]) + mul(Kinv[I, I], Kinv[J, J]))
        v = -grad
        lapack.posv(hess, v)

        # stopping criterion
        sqntdecr = -blas.dot(grad, v)
        print("Newton decrement squared:%- 7.5e" % sqntdecr)
        if (sqntdecr < 1e-12):
            print("number of iterations: ", iters + 1)
            break

        # line search
        dx = +v
        dx[D] *= 2      # scale the diagonal elems
        f = -2.0 * sum(log(d))    # f = -log det K
        s = 1
        for lsiter in range(50):
            Kn.V = K.V + s * dx
            try:
                cholmod.numeric(Kn, F)
            except ArithmeticError:
                s *= 0.5
            else:
                d = cholmod.diag(F)
                fn = -2.0 * sum(log(d)) + 2 * s * blas.dot(v, Y.V)
                if (fn < f - 0.01 * s * sqntdecr):
                    break
                s *= 0.5

        K.V = Kn.V

    return K


A = spmatrix([10, 3, 5, -2, 5, 2], [0, 2, 1, 2, 2, 3], [0, 0, 1, 1, 2, 3])
P = amd.order(A)
print(P)

V = [2, 3, 3, -1, 4, 4, -3, 1, 2, 2, 6, 1]
I = [0, 1, 0, 2, 4, 1, 2, 3, 4, 2, 1, 4]
J = [0, 0, 1, 1, 1, 2, 2, 2, 2, 3, 4, 4]
A = spmatrix(V, I, J)
B = matrix(1.0, (5, 1))
umfpack.linsolve(A, B)
print(B)

VA = [2, 3, 3, -1, 4, 4, -3, 1, 2, 2, 6, 1]
VB = [4, 3, 3, -1, 4, 4, -3, 1, 2, 2, 6, 2]
I = [0, 1, 0, 2, 4, 1, 2, 3, 4, 2, 1, 4]
J = [0, 0, 1, 1, 1, 2, 2, 2, 2, 3, 4, 4]
A = spmatrix(VA, I, J)
B = spmatrix(VB, I, J)
x = matrix(1.0, (5, 1))
Fs = umfpack.symbolic(A)
FA = umfpack.numeric(A, Fs)
FB = umfpack.numeric(B, Fs)
umfpack.solve(A, FA, x)
umfpack.solve(B, FB, x)
umfpack.solve(A, FA, x, trans='T')
print(x)

A = spmatrix([10, 3, 5, -2, 5, 2], [0, 2, 1, 3, 2, 3], [0, 0, 1, 1, 2, 3])
X = matrix(range(8), (4, 2), 'd')
cholmod.linsolve(A, X)
print(X)

X = cholmod.splinsolve(A, spmatrix(1.0, range(4), range(4)))
print(X)

X = matrix(range(8), (4, 2), 'd')
F = cholmod.symbolic(A)
cholmod.numeric(A, F)
cholmod.solve(F, X)
print(X)

F = cholmod.symbolic(A)
cholmod.numeric(A, F)
print(2.0 * sum(log(cholmod.diag(F))))
options['supernodal'] = 0
F = cholmod.symbolic(A)
cholmod.numeric(A, F)
Di = matrix(1.0, (4, 1))
cholmod.solve(F, Di, sys=6)
print(-sum(log(Di)))
