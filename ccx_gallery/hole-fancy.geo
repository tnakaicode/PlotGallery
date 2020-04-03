Point(0) = {4.000000, -3.000000, 0.000000};
Point(1) = {4.000000, 3.000000, 0.000000};
Point(2) = {-4.000000, 3.000000, 0.000000};
Point(3) = {-4.000000, -3.000000, 0.000000};
Point(8) = {3.000000, -1.000000, 0.000000};
Point(9) = {2.000000, -1.000000, 0.000000};
Point(10) = {2.000000, -2.000000, 0.000000};
Point(11) = {-2.000000, -2.000000, 0.000000};
Point(12) = {-2.000000, -1.000000, 0.000000};
Point(13) = {-3.000000, -1.000000, 0.000000};
Point(5) = {-3.000000, 1.000000, 0.000000};
Point(6) = {-2.000000, 1.000000, 0.000000};
Point(14) = {-2.000000, 2.000000, 0.000000};
Point(15) = {2.000000, 2.000000, 0.000000};
Point(16) = {2.000000, 1.000000, 0.000000};
Point(17) = {3.000000, 1.000000, 0.000000};
Point(18) = {4.000000, 1.000000, 0.000000};
Point(19) = {4.000000, -1.000000, 0.000000};
Point(4) = {2.000000, -3.000000, 0.000000};
Point(20) = {-2.000000, -3.000000, 0.000000};
Point(21) = {-4.000000, -1.000000, 0.000000};
Point(22) = {-4.000000, 1.000000, 0.000000};
Point(23) = {-2.000000, 3.000000, 0.000000};
Point(24) = {2.000000, 3.000000, 0.000000};
Line(25) = {0,19};
Line(26) = {1,24};
Line(27) = {2,22};
Line(28) = {3,20};
Line(29) = {17,8};
Line(30) = {10,11};
Line(31) = {13,5};
Line(32) = {14,15};
Circle(33) = {8, 9, 10};
Circle(34) = {11, 12, 13};
Circle(35) = {5, 6, 14};
Circle(36) = {15, 16, 17};
Line(37) = {18,1};
Line(38) = {18,17};
Line(39) = {19,18};
Line(40) = {19,8};
Line(41) = {4,0};
Line(42) = {10,4};
Line(43) = {20,4};
Line(44) = {11,20};
Line(45) = {21,3};
Line(46) = {13,21};
Line(47) = {22,21};
Line(48) = {5,22};
Line(49) = {23,2};
Line(50) = {14,23};
Line(51) = {24,23};
Line(52) = {15,24};
Line Loop(53) = {25,40,33,42,41};
Plane Surface(54) = {53};
Physical Surface('A0') = {54};
Line Loop(55) = {39,38,29,-40};
Plane Surface(56) = {55};
Physical Surface('A1') = {56};
Line Loop(57) = {30,44,43,-42};
Plane Surface(58) = {57};
Physical Surface('A2') = {58};
Line Loop(59) = {34,46,45,28,-44};
Plane Surface(60) = {59};
Physical Surface('A3') = {60};
Line Loop(61) = {31,48,47,-46};
Plane Surface(62) = {61};
Physical Surface('A4') = {62};
Line Loop(63) = {35,50,49,27,-48};
Plane Surface(64) = {63};
Physical Surface('A5') = {64};
Line Loop(65) = {32,52,51,-50};
Plane Surface(66) = {65};
Physical Surface('A6') = {66};
Line Loop(67) = {36,-38,37,26,-52};
Plane Surface(68) = {67};
Physical Surface('A7') = {68};
Physical Surface('PART0') = {54,56,58,60,62,64,66,68};
Physical Line('L0') = {25};
Physical Line('L1') = {26};
Physical Line('L2') = {27};
Physical Line('L3') = {28};
Physical Line('L4') = {29};
Physical Line('L5') = {30};
Physical Line('L6') = {31};
Physical Line('L7') = {32};
Physical Line('L8') = {33};
Physical Line('L9') = {34};
Physical Line('L10') = {35};
Physical Line('L11') = {36};
Physical Line('L12') = {37};
Physical Line('L13') = {38};
Physical Line('L14') = {39};
Physical Line('L15') = {40};
Physical Line('L16') = {41};
Physical Line('L17') = {42};
Physical Line('L18') = {43};
Physical Line('L19') = {44};
Physical Line('L20') = {45};
Physical Line('L21') = {46};
Physical Line('L22') = {47};
Physical Line('L23') = {48};
Physical Line('L24') = {49};
Physical Line('L25') = {50};
Physical Line('L26') = {51};
Physical Line('L27') = {52};
Physical Point('P0') = {0};
Physical Point('P1') = {1};
Physical Point('P2') = {2};
Physical Point('P3') = {3};
Physical Point('P8') = {8};
Physical Point('P9') = {9};
Physical Point('P10') = {10};
Physical Point('P11') = {11};
Physical Point('P12') = {12};
Physical Point('P13') = {13};
Physical Point('P5') = {5};
Physical Point('P6') = {6};
Physical Point('P14') = {14};
Physical Point('P15') = {15};
Physical Point('P16') = {16};
Physical Point('P17') = {17};
Physical Point('P18') = {18};
Physical Point('P19') = {19};
Physical Point('P4') = {4};
Physical Point('P20') = {20};
Physical Point('P21') = {21};
Physical Point('P22') = {22};
Physical Point('P23') = {23};
Physical Point('P24') = {24};
Mesh.RecombinationAlgorithm = 1; //blossom
Mesh.RecombineAll = 1; //turns on quads
Mesh.SubdivisionAlgorithm = 1; // quadrangles only
Mesh.CharacteristicLengthExtendFromBoundary = 1;
Mesh.CharacteristicLengthMin = 0;
Mesh.CharacteristicLengthMax = 1e+022;
Mesh.CharacteristicLengthFromPoints = 1;
Mesh.Algorithm = 8; //delquad = delauny for quads
Mesh.ElementOrder = 2; //linear or second set here
Mesh.SecondOrderIncomplete=1; //no face node w/ 2nd order
Mesh.SaveGroupsOfNodes = 1; // save node groups