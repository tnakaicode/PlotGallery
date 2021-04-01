lc = .01;
Point(1) = {0,0,0,lc};
Point(2) = {.5,0,0,lc};
Point(3) = {.5,.5,0,lc};
Point(4) = {1,.5,0,lc};
Point(5) = {1,1,0,lc};
Point(6) = {0,1,0,lc};
Point(7) = {.5,.25,0,lc};
Point(8) = {.5,.75,0,lc};
Point(9) = {.125,.875,0,lc};
Point(10) = {.125,.875-.05,0,lc};
Point(11) = {.125,.875+.05,0,lc};

Line(1)  = {1,2};
Circle(2)  = {2,3,4};
Line(3)  = {4,5};
Line(4)  = {5,6};
Line(5)  = {6,1};
Circle(6)  = {7,3,8};
Circle(7)  = {8,3,7};
Circle(8)  = {10,9,11};
Circle(9)  = {11,9,10};

//Transfinite Line {8} = 15;
//Transfinite Line {9} = 10;


Line Loop(1) = {6,7}; // interior loop
Line Loop(2) = {1,2,3,4,5}; // exterior loop
Line Loop(3) = {8,9};// hole
//Plane Surface(1) = {1}; // interior surface
Plane Surface(2) = {2,1,3}; // exterior surface (with a hole)
Recombine Surface {2};
Physical Surface("SURFACE") = {2};
