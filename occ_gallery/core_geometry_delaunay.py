"""
This file is a collection of quad-edge primitives,
and the functional core of the application.
"""


def debug(m, data=True, next=False, edges=False):
    """takes an Mesh-Object and prints debug stuff"""

    if data:
        print("Org, Dest")
        for qe in m.quadEdges:
            print(
                f"{qe}: [{qe.org.x:.4f} \
                    , {qe.org.y:.4f}] \
                    , [{qe.dest.x:.4f} \
                    , {qe.dest.y:.4f}]"
            )
        else:
            print("\n")

    if edges:
        print("Edges")
        for qe in m.quadEdges:
            print([e for e in qe.edges])
        else:
            print("\n")
    if next:
        print("Edge, Nexts")
        for qe in m.quadEdges:
            print(qe[0], [e.next for e in qe.edges])
        else:
            print("\n")
    return


class Vertex:
    def __init__(self, x=None, y=None):
        self.pos = [x, y]
        self.x = x
        self.y = y
        self.data = None

    def __str__(self):
        return f"{self.pos}"

    def __repr__(self):
        return f"{self.pos}"

    def __hash__(self):
        return hash("".join([str(x) for x in self.pos]))

    @property
    def id(self):
        return self.__hash__()


class Edge:

    """Actual edge, the main object we will do work with"""

    def __init__(self, parent, index=0, data=None):
        self.next = self
        self.data = data
        self.index = index
        self.parent = parent
        self.id = parent.id + f".{self.index}"

    def __repr__(self):
        return "Edge-{self.id}"

    def __str__(self):
        return f"{self.id}"


class QuadEdge:

    """Container for Edges, which can be accessed by get/setitem"""

    def __init__(self, org, dest, id="0"):
        self.id = id
        self.edges = [
            Edge(parent=self, data=org),
            Edge(parent=self, index=1),
            Edge(parent=self, index=2, data=dest),
            Edge(parent=self, index=3),
        ]
        self.org = org
        self.dest = dest

    def __str__(self):
        return f"{self.id}"

    def __repr__(self):
        return f"QuadEdge-{self.id}"

    def __getitem__(self, idx):
        return self.edges[idx]

    def __setitem__(self, idx, val):
        self.edges[idx] = val


def rot(e):
    return e.parent[(e.index + 1) % 4]


def invrot(e):
    return e.parent[(e.index + 3) % 4]


def sym(e):
    return e.parent[(e.index + 2) % 4]


def org(e):
    return e.data


def dest(e):
    return e.parent[sym(e).index].data


def onext(e):
    return e.next


def lnext(e):
    return rot(onext(invrot(e)))


def lprev(e):
    return sym(onext(e))


def oprev(e):
    return rot(onext(rot(e)))


def rprev(e):
    return onext(sym(e))


def dprev(e):
    return invrot(onext(invrot(e)))


def splice(a, b):
    alpha = rot(onext(a))
    beta = rot(onext(b))

    tmp = onext(alpha)

    alpha.next = onext(beta)
    beta.next = tmp

    tmp = onext(a)
    a.next = onext(b)
    b.next = tmp

    return


def ccw(vA, vB, vC):
    """
    Returns true iff Vertices a,b and c form a ccw oriented triangle

    This is adapted from Shewchuk's Routines for Arbitrary Precision
    Floating-point Arithmetic and Fast Robust Geometric Predicates.
    http://www.cs.cmu.edu/~quake/robust.html

    But of course its the nonrobust version.
    """
    ax, ay = vA.pos
    bx, by = vB.pos
    cx, cy = vC.pos

    return ((ax - cx) * (by - cy) - (bx - cx) * (ay - cy)) > 0


def inCircle(vA, vB, vC, vD):
    """
    Returns true iff Vertex d lies in circle defined by a,b and c

    This is adapted from Shewchuk's Routines for Arbitrary Precision
    Floating-point Arithmetic and Fast Robust Geometric Predicates.
    http://www.cs.cmu.edu/~quake/robust.html

    But of course its the nonrobust version.
    """

    adx = vA.x - vD.x
    ady = vA.y - vD.y
    bdx = vB.x - vD.x
    bdy = vB.y - vD.y
    cdx = vC.x - vD.x
    cdy = vC.y - vD.y

    abdet = adx * bdy - bdx * ady
    bcdet = bdx * cdy - cdx * bdy
    cadet = cdx * ady - adx * cdy
    alift = adx * adx + ady * ady
    blift = bdx * bdx + bdy * bdy
    clift = cdx * cdx + cdy * cdy

    return (alift * bcdet + blift * cadet + clift * abdet) > 0


def valid(e, basel):
    return ccw(dest(e), dest(basel), org(basel))


class Mesh:
    """
    Used to hold state of the mesh and
    to collect imperative functions regarding
    i/o, generation and deletion.
    """

    def __init__(self):
        self.quadEdges = []
        self.vertices = []
        self.nextEdge = 0
        self.rows = 1
        self.qid = 0

    def makeEdge(self, org, dest):
        """Construct Edges, adds QuadEdge to mesh. See Q&S"""

        qe = QuadEdge(org, dest, id=str(self.qid))
        qe[1].next = qe[3]
        qe[3].next = qe[1]

        self.quadEdges.append(qe)
        self.qid += 1

        return qe[0]

    def connect(self, a, b):
        """Connect two edges by a third, while making shure
        they share the same left face. See Q&S"""

        c = self.makeEdge(dest(a), org(b))
        splice(c, lnext(a))
        splice(sym(c), b)

        return c

    def deleteEdge(self, e):
        """Delete edge without changing the topology"""

        splice(e, oprev(e))
        splice(sym(e), oprev(sym(e)))
        # e.parent.edges.remove(e)
        self.quadEdges.remove(e.parent)

        return

    def loadVertices(self, vertList):
        """Sort vertices on the x-axis"""

        self.vertices = sorted(vertList, key=lambda vert: vert.x)

        return

    def delaunay(self, start=0, end=100, leftEdge=None, rightEdge=None, rows=None):
        """
        This is an implentation of the divide-and-conquer alorithm proposed
        by guibas & stolfi.

        It returns the outermost edges [leftEdge, rightEdge] of the convex
        hull it builds while connecting points to form a delaunay triangulation.
        """

        verts = self.vertices
        if start < (end - 2):  # four or more points
            print("over-4", start, end)
            # divide points in two halves
            split = (end - start) // 2 + start

            # recurse down the halves
            ldo, ldi = self.delaunay(start, split)
            rdi, rdo = self.delaunay((split + 1), end)

            # 'Compute the lower common tangent of L and R'
            while True:
                if ccw(org(rdi), org(ldi), dest(ldi)):  # leftOf
                    print("over-4", "left of")
                    ldi = lnext(ldi)
                elif ccw(org(ldi), dest(rdi), org(rdi)):  # rightOf
                    print("over-4", "right of")
                    rdi = rprev(rdi)
                else:
                    print("over-4", "not right/left of")
                    break

            # 'Create a first cross edge basel from rdi.Org to ldi.Org'
            basel = self.connect(sym(rdi), ldi)
            if org(ldi) == org(ldo):
                ldo = sym(basel)
            if org(rdi) == org(rdo):
                rdo = basel

            # merge the obtained halves
            # merge(m, ldo, ldi, rdi, rdo)

            while True:
                """
                'Locate the first L point (lcand.Dest) to be encountered
                 by the rising bubble and delete L edges out of basel.Dest'
                """
                lcand = rprev(basel)
                if valid(lcand, basel):
                    while inCircle(
                        dest(basel), org(basel), dest(
                            lcand), dest(onext(lcand))
                    ):
                        t = onext(lcand)
                        self.deleteEdge(lcand)
                        lcand = t

                """
                'Symmetrically, locate the first R point to be hit
                 and delete R edges'
                """
                rcand = oprev(basel)
                if valid(rcand, basel):
                    while inCircle(
                        dest(basel), org(basel), dest(
                            rcand), dest(oprev(rcand))
                    ):
                        t = oprev(rcand)
                        self.deleteEdge(rcand)
                        rcand = t

                """
                'If both lcand and rcand are invalid,
                 then basel is the upper common tangent'
                """

                lvalid = valid(lcand, basel)
                rvalid = valid(rcand, basel)

                if not lvalid and not rvalid:
                    break

                """
                'The next cross edge is to be connected to either
                 lcand.Dest or rcand.Dest. If both are valid, then
                 choose the appropriate one using the InCircle test:'
                """
                if (
                    not lvalid
                    or rvalid
                    and inCircle(dest(lcand), org(lcand), org(rcand), dest(rcand))
                ):
                    # 'Add cross edge basel from rcand.Dest to basel.Dest'
                    basel = self.connect(rcand, sym(basel))

                else:
                    # 'Add cross edge basel from basel.Org to lcand.Dest'
                    basel = self.connect(sym(basel), sym(lcand))

            xMin = verts[start]
            xMax = verts[end]
            while org(ldo) != xMin:
                ldo = rprev(ldo)

            while org(rdo) != xMax:
                rdo = lprev(rdo)

            print(start, end, "over-4", [ldo, rdo])
            print()
            return [ldo, rdo]

        elif start >= (end - 1):  # two or one points
            """
            Original Comment:
             'Let s1, s2 be the two sites, in sorted order.
              Create an edge a from s1 to s2'
            """

            a = self.makeEdge(verts[start], verts[end])

            if start == end:
                exit()

            print(start, end, "two/one", [a, sym(a)])
            return [a, sym(a)]

        else:  # Three points
            """
            Original Comment:
             'Let s1, s2, s3 be the three sites, in sorted order.
              Create edges a connecting s1 to s2 and b connecting s2 to s3'
            """

            assert len(verts[start: end + 1]) == 3  # just in case

            v1, v2, v3 = verts[start: end + 1]
            a = self.makeEdge(v1, v2)
            b = self.makeEdge(v2, v3)
            splice(sym(a), b)

            """'Now close the triangle'"""

            if ccw(v1, v3, v2):
                c = self.connect(b, a)
                print(start, end, "three-1", [sym(c), c])
                return [sym(c), c]

            elif ccw(v1, v2, v3):
                c = self.connect(b, a)
                print(start, end, "three-2", [a, sym(b)])
                return [a, sym(b)]

            else:  # points are colinear
                self.deleteEdge(c)
                print(start, end, "three-3", [a, sym(b)])
                return [a, sym(b)]


if __name__ == "__main__":
    from random import seed, uniform
    seed(123123123)

    N = 20  # number of vertices

    vertices = [Vertex(uniform(0, 100), uniform(0, 100)) for v in range(N)]

    m = Mesh()  # this object holds the edges and vertices

    m.loadVertices(vertices)

    end = N - 1

    m.delaunay(0, end)  # computes the triangulation

    # populates a list of [org, dest], values for further manipulation
    lines = []
    for qe in m.quadEdges:
        if qe.org is not None:
            lines += [[[qe.org.x, qe.dest.x], [qe.org.y, qe.dest.y]]]

    # plotting, for example:

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    plt.scatter([v.x for v in vertices], [v.y for v in vertices])

    for line in lines:
        start, end = line

        ax.plot(start, end)

    plt.show()
