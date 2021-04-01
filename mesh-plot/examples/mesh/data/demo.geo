lcar     = .01;
Point(1) = {0., 0., 0., lcar};
Point(2) = {1., 0., 0., lcar*10.0};
Point(3) = {1., 1., 0., lcar};
Point(4) = {0., 1., 0., lcar/10.};
Line(1)  = {1,2};
Line(2)  = {2,3};
Line(3)  = {3,4};
Line(4)  = {4,1};
Line Loop(1)        = {1,2,3,4};
Plane Surface(1)    = {1};
//Transfinite Surface {1};
Recombine Surface {1};
Physical Surface("Front") = 1;

