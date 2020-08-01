#!/usr/bin/env python
# coding: utf-8

# ## Integration over Polytopes

# #### Extra dependencies : matplotlib (if using methods : plot_polytope and plot_polynomial) 

# In[ ]:


from sympy import sqrt
from sympy.abc import x, y, z
from sympy.geometry import *
from sympy.integrals.intpoly import *


# ## Methods : 

# ### polytope_integrate(poly, expr, **kwargs)
#     Integrates polynomials over 2/3-Polytopes.
# 
#     This function accepts the polytope in `poly` and the function in `expr` (uni/bi/trivariate polynomials are
#     implemented) and returns the exact integral of `expr` over `poly`.
#     
#     Parameters
#     ---------------------------------------
#     1. poly(Polygon) : 2/3-Polytope
#     2. expr(SymPy expression) : uni/bi-variate polynomial for 2-Polytope and uni/bi/tri-variate for 3-Polytope
#     
#     Optional Parameters
#     ---------------------------------------
#     1. clockwise(Boolean) : If user is not sure about orientation of vertices of the 2-Polytope and wants
#        to clockwise sort the points.
#     2. max_degree(Integer) : Maximum degree of any monomial of the input polynomial. This would require 
#      
#    #### Examples :

# In[ ]:


triangle = Polygon(Point(0,0), Point(1,1), Point(1,0))
plot_polytope(triangle)
print("Area of Triangle with vertices : (0,0), (1,1), (1,0) : ", polytope_integrate(triangle, 1))
print("x*y integrated over Triangle with vertices : (0,0), (1,1), (1,0) : ", polytope_integrate(triangle, x*y),"\n")

hexagon = Polygon(Point(0, 0), Point(-sqrt(3) / 2, 0.5),
                  Point(-sqrt(3) / 2, 3 / 2), Point(0, 2),
                  Point(sqrt(3) / 2, 3 / 2), Point(sqrt(3) / 2, 0.5))
plot_polytope(hexagon)
print("Area of regular hexagon with unit side length  : ", polytope_integrate(hexagon, 1))
print("x + y**2 integrated over regular hexagon with unit side length  : ", polytope_integrate(hexagon, x + y**2))

polys = [1, x, y, x*y]
print("1, x, y, x*y integrated over hexagon : ", polytope_integrate(hexagon, polys, max_degree=2))


# ### main_integrate3d(expr, facets, vertices, hp_params)
#     Function to translate the problem of integrating uni/bi/tri-variate
#     polynomials over a 3-Polytope to integrating over its faces.
#     This is done using Generalized Stokes's Theorem and Euler's Theorem.
#     
#     Parameters
#     ------------------
#     1. expr : The input polynomial
#     2. facets : Faces of the 3-Polytope(expressed as indices of `vertices`)
#     3. vertices : Vertices that constitute the Polytope
#     4. hp_params : Hyperplane Parameters of the facets
#     
#    #### Examples:

# In[ ]:


cube = [[(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)],
         [2, 6, 7, 3], [3, 7, 5, 1], [7, 6, 4, 5], [1, 5, 4, 0], [3, 1, 0, 2], [0, 4, 6, 2]]
vertices = cube[0]
faces = cube[1:]
hp_params = hyperplane_parameters(faces, vertices)
main_integrate3d(1, faces, vertices, hp_params)


# ### polygon_integrate(facet, index, facets, vertices, expr, degree)
#     Helper function to integrate the input uni/bi/trivariate polynomial
#     over a certain face of the 3-Polytope.
#     
#     Parameters
#     ------------------
#     facet : Particular face of the 3-Polytope over which `expr` is integrated
#     index : The index of `facet` in `facets`
#     facets : Faces of the 3-Polytope(expressed as indices of `vertices`)
#     vertices : Vertices that constitute the facet
#     expr : The input polynomial
#     degree : Degree of `expr`
#     
#    #### Examples:

# In[ ]:


cube = [[(0, 0, 0), (0, 0, 5), (0, 5, 0), (0, 5, 5), (5, 0, 0),
                 (5, 0, 5), (5, 5, 0), (5, 5, 5)],
                 [2, 6, 7, 3], [3, 7, 5, 1], [7, 6, 4, 5], [1, 5, 4, 0],
                 [3, 1, 0, 2], [0, 4, 6, 2]]
facet = cube[1]
facets = cube[1:]
vertices = cube[0]
print("Area of polygon < [(0, 5, 0), (5, 5, 0), (5, 5, 5), (0, 5, 5)] > : ", polygon_integrate(facet, 0, facets, vertices, 1, 0))


# ### distance_to_side(point, line_seg)
# 
#     Helper function to compute the distance between given 3D point and
#     a line segment.
# 
#     Parameters
#     -----------------
#     point : 3D Point
#     line_seg : Line Segment
#     
# #### Examples:

# In[ ]:


point = (0, 0, 0)
distance_to_side(point, [(0, 0, 1), (0, 1, 0)])


# ### lineseg_integrate(polygon, index, line_seg, expr, degree)
#     Helper function to compute the line integral of `expr` over `line_seg`
# 
#     Parameters
#     -------------
#     polygon : Face of a 3-Polytope
#     index : index of line_seg in polygon
#     line_seg : Line Segment
# #### Examples :

# In[ ]:


polygon = [(0, 5, 0), (5, 5, 0), (5, 5, 5), (0, 5, 5)]
line_seg = [(0, 5, 0), (5, 5, 0)]
print(lineseg_integrate(polygon, 0, line_seg, 1, 0))


# ### main_integrate(expr, facets, hp_params, max_degree=None)
# 
#     Function to translate the problem of integrating univariate/bivariate
#     polynomials over a 2-Polytope to integrating over its boundary facets.
#     This is done using Generalized Stokes's Theorem and Euler's Theorem.
# 
#     Parameters
#     --------------------
#     expr : The input polynomial
#     facets : Facets(Line Segments) of the 2-Polytope
#     hp_params : Hyperplane Parameters of the facets
# 
#     Optional Parameters:
#     --------------------
#     max_degree : The maximum degree of any monomial of the input polynomial.
#     
# #### Examples:

# In[ ]:


triangle = Polygon(Point(0, 3), Point(5, 3), Point(1, 1))
facets = triangle.sides
hp_params = hyperplane_parameters(triangle)
print(main_integrate(x**2 + y**2, facets, hp_params))


# ### integration_reduction(facets, index, a, b, expr, dims, degree)
#     This is a helper function for polytope_integrate. It relates the result of the integral of a polynomial over a
#     d-dimensional entity to the result of the same integral of that polynomial over the (d - 1)-dimensional 
#     facet[index].
#     
#     For the 2D case, surface integral --> line integrals --> evaluation of polynomial at vertices of line segments
#     For the 3D case, volume integral --> 2D use case
#     
#     The only minor limitation is that some lines of code are 2D specific, but that can be easily changed. Note that
#     this function is a helper one and works for a facet which bounds the polytope(i.e. the intersection point with the
#     other facets is required), not for an independent line.
#     
#     Parameters
#     ------------------
#     facets : List of facets that decide the region enclose by 2-Polytope.
#     index : The index of the facet with respect to which the integral is supposed to be found.
#     a, b : Hyperplane parameters corresponding to facets.
#     expr : Uni/Bi-variate Polynomial
#     dims : List of symbols denoting axes
#     degree : Degree of the homogeneous polynoimal(expr)
#     
#    #### Examples:

# In[ ]:


facets = [Segment2D(Point(0, 0), Point(1, 1)), Segment2D(Point(1, 1), Point(1, 0)), Segment2D(Point(0, 0), Point(1, 0))]
print(integration_reduction(facets, 0, (0, 1), 0, 1, [x, y], 0))
print(integration_reduction(facets, 1, (0, 1), 0, 1, [x, y], 0))
print(integration_reduction(facets, 2, (0, 1), 0, 1, [x, y], 0))


# ### hyperplane_parameters(poly) :
#     poly : 2-Polytope
#     
#     Returns the list of hyperplane parameters for facets of the polygon.
#     
#     Limitation : 2D specific.
#    #### Examples:

# In[ ]:


triangle = Polygon(Point(0,0), Point(1,1), Point(1,0))
hyperplane_parameters(triangle)


# ### best_origin(a, b, lineseg, expr) :
#     a, b : Line parameters of the line-segment
#     expr : Uni/Bi-variate polynomial
#     
#     Returns a point on the lineseg whose vector inner product with the divergence of expr yields an expression with 
#     the least maximum total power. This is for reducing the number of computations in the integration reduction call.
#     
#     Limitation : 2D specific.
#     
#    #### Examples:

# In[ ]:


print("Best origin for x**3*y on x + y = 3 : ", best_origin((1,1), 3, Segment2D(Point(0, 3), Point(3, 0)), x**3*y))
print("Best origin for x*y**3 on x + y = 3 : ",best_origin((1,1), 3, Segment2D(Point(0, 3), Point(3, 0)), x*y**3))


# ### decompose(expr, separate=False) :
#     expr : Uni/Bi-variate polynomial.
#     separate(default : False) : If separate is True then return list of constituting monomials.
#     
#     Returns a dictionary of the terms having same total power. This is done to get homogeneous polynomials of
#     different degrees from the expression.
#     
#    #### Examples:

# In[ ]:


print(decompose(1 + x + x**2 + x*y))
print(decompose(x**2 + x + y + 1 + x**3 + x**2*y + y**4 + x**3*y + y**2*x**2))
print(decompose(x**2 + x + y + 1 + x**3 + x**2*y + y**4 + x**3*y + y**2*x**2, 1))


# ### norm(expr) :
#      
#     point : Tuple/SymPy Point object/Dictionary
#     
#     Returns Euclidean norm of the point object.
# 
#    #### Examples:

# In[ ]:


print(norm((1, 2)))
print(norm(Point(1, 2)))
print(norm({x: 3, y: 3, z: 1}))


# ### intersection(lineseg_1, lineseg_2) :
#      
#     lineseg_1, lineseg_2 : The input line segments whose intersection is to be found.
#     
#     Returns intersection point of two lines of which lineseg_1, lineseg_2 are part of. This function is
#     called for adjacent line segments so the intersection point is always present with line segment boundaries.
# 
#    #### Examples:

# In[ ]:


print(intersection(Segment2D(Point(0, 0), Point(2, 2)), Segment2D(Point(1, 0), Point(0, 1))))
print(intersection(Segment2D(Point(2, 0), Point(2, 2)), Segment2D(Point(0, 0), Point(4, 4))))


# ### is_vertex(ent) :
#      
#     ent : Geometrical entity to denote a vertex.
#     
#     Returns True if ent is a vertex. Currently tuples of length 2 or 3 and SymPy Point object are supported.
#    #### Examples:

# In[ ]:


print(is_vertex(Point(2, 8)))
print(is_vertex(Point(2, 8, 1)))
print(is_vertex((1, 1)))
print(is_vertex([2, 9]))
print(is_vertex(Polygon(Point(0, 0), Point(1, 1), Point(1, 0))))


# ### plot_polytope(poly) :
#      
#     poly : 2-Polytope
#     
#     Plots the 2-Polytope. Currently just defers it to plotting module in SymPy which in turn uses matplotlib.
#         
#    #### Examples:

# In[ ]:


hexagon = Polygon(Point(0, 0), Point(-sqrt(3) / 2, 0.5),
                  Point(-sqrt(3) / 2, 3 / 2), Point(0, 2),
                  Point(sqrt(3) / 2, 3 / 2), Point(sqrt(3) / 2, 0.5))
plot_polytope(hexagon)

twist = Polygon(Point(-1, 1), Point(0, 0), Point(1, 1), Point(1, -1),
                Point(0, 0), Point(-1, -1))
plot_polytope(twist)


# ### plot_polynomial(expr) :
#      
#     expr : The uni/bi-variate polynomial to plot
#     
#     Plots the polynomial. Currently just defers it to plotting module in SymPy which in turn uses matplotlib.
#         
#    #### Examples:

# In[ ]:


expr = x**2
plot_polynomial(expr)

expr = x*y
plot_polynomial(expr)


# In[ ]:




