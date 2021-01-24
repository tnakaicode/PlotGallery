#
# $Id: world.dem,v 1.11 2014/10/05 00:33:15 sfeam Exp $
#
#
set title "Gnuplot Correspondences \n geographic coordinate system"
unset key
set xrange [-180:180]
set yrange [-90:90]
set yzeroaxis
set xtics geographic
set ytics geographic
set format x "%D %E"
set format y "%D %N"
#
# plot a '3D version using spherical coordinate system' of the world.
reset
unset key
set border
set yzeroaxis
set xtics
set ytics
set angles degrees
set title "3D version using spherical coordinate system"
set ticslevel 0
set view 70,40,0.8,1.2
set view equal xyz
set mapping spherical
set parametric
set samples 32
set isosamples 9
set urange [-90:90]
set vrange [0:360]
splot cos(u)*cos(v),cos(u)*sin(v),sin(u) with lines lc rgb "cyan" ,\
      'world.dat' with lines lc rgb "red" ,\
      'world.cor' with points lt 1 pt 2 ,\
      'world_Japan.cor' with points lt 1 pt 2
