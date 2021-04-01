// SETTINGS
lx = 1.;
ly = 1.;
r1 = 2.;
r2 = 10.;
Nx = 8;
Ny = 8;
lc0 = ly/Ny;
lc1 = 0.5;
lc2 = 2.;

Point(1) = {0.,  0., 0., lc0};
Point(2) = {0,  -ly, 0., lc0};
Point(3) = {lx, -ly, 0., lc0};
Point(4) = {lx,  0., 0., lc0};
Point(5) = {0., -r1, 0., lc1};
Point(6) = {r1,  0., 0., lc1};
Point(7) = {0., -r2, 0., lc2};
Point(8) = {r2,  0., 0., lc2};


// Center square
Line(1)  = {1,2};
Line(2)  = {2,3};
Line(3)  = {3,4};
Line(4)  = {4,1};
Transfinite Line {2,4} = Nx;
Transfinite Line {1,3} = Ny;
Line Loop(1)           = {1,2,3,4};
Plane Surface(1) = {1};
Transfinite Surface {1};


// Shell 1
Line(5)   = {2,5};
Circle(6) = {5,1,6};
Line(7)   = {6,4};
Line Loop(2) = {5,6,7,-3,-2};
Plane Surface(2) = {2};

// Shell 2
Line(8)   = {5,7};
Circle(9) = {7,1,8};
Line(10)   = {8,6};
Line Loop(3) = {8,9,10,-6};
Plane Surface(3) = {3};




Recombine Surface {1,2,3};
Physical Line("Surface") = {4,7};
Physical Line("Bottom") = {9};
Physical Line("Axis") = {1,5,8};
Physical Surface("Core") = {1};
Physical Surface("Shell1") = {2};
Physical Surface("Shell2") = {3};


