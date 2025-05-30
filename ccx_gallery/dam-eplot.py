#!/usr/bin/env python3
import math
import sys

import pycalculix as pyc

# We'll be modeling a masonry gravity dam, the Beetaloo dam in Australia
# This time, we'll include multiple time steps, and element plotting
# make model
model_name = 'dam-eplot'
model = pyc.FeaModel(model_name)
# this sets dist units to meters, labels our consistent units
model.set_units('m')

# set whether or not to show gui plots
show_gui = False
if '-nogui' in sys.argv:
    show_gui = False
# set element shape
eshape = 'quad'
if '-tri' in sys.argv:
    eshape = 'tri'

# Problem constants
grav = 9.81  # m/s^2
dens_water = 1000  # kg/m^3
press_atm = 101325  # Pascals = N/m^2 = kg/(m-s^2)
dam_ht_ft = 115
water_ht_ft = 109
length_dam_ft = 580

# derived dims
water_ax = (water_ht_ft - 22) / math.tan(math.radians(89)) + 12
top_ax = (dam_ht_ft - 22) / math.tan(math.radians(89)) + 12
thickness = length_dam_ft * 0.3048  # conversion to metric

# derived dimensions, tan = o/a --> o/tan = a
pts_ft_water = [[8, 0], [22, 12], [water_ht_ft, water_ax]]
pts_ft_air = [[dam_ht_ft, top_ax], [dam_ht_ft, top_ax + 14]]
water_ht_m = water_ht_ft * 0.3048

# make part, coordinates are x, y = radial, axial
part = pyc.Part(model)
part.goto(0.0, 0.0)
water_lines = []
air_lines = []
for [x, y] in pts_ft_water:
    [x, y] = [x * 0.3048, y * 0.3048]  # conversion to metric
    [L1, p1, p2] = part.draw_line_to(x, y)
    water_lines.append(L1)
for [x, y] in pts_ft_air:
    [x, y] = [x * 0.3048, y * 0.3048]  # conversion to metric
    [L1, p1, p2] = part.draw_line_to(x, y)
    air_lines.append(L1)
# make the two arcs
pts_ft_arcs = [[[22, 73], [146, 208]], [[14, 98], [41, 93]]]
for [[x, y], [xc, yc]] in pts_ft_arcs:
    [x, y] = [x * 0.3048, y * 0.3048]
    [xc, yc] = [xc * 0.3048, yc * 0.3048]
    [L1, p1, p2] = part.draw_arc(x, y, xc, yc)
    air_lines.append(L1)
# make the last 3 lines after the arcs
pts_ft_other = [[2, 110], [0, 110]]
for [x, y] in pts_ft_other:
    [x, y] = [x * 0.3048, y * 0.3048]  # conversion to metric
    [L1, p1, p2] = part.draw_line_to(x, y)
    air_lines.append(L1)
part.draw_line_to(0, 0)
# view the points, lines, and areas
model.plot_geometry(model_name + '_geom', display=show_gui)

# set part material
mat = pyc.Material('concrete')
mat.set_mech_props(2300, 30000 * (10**6), 0.2)
model.set_matl(mat, part)

# set the element type, line division, and mesh the database
model.set_eshape(eshape, 2)
model.set_etype('plstrain', part, thickness)
model.set_ediv('L8', 2)
# mesh with 1.0 or less fineness, smaller is finer
model.mesh(0.5, 'gmsh')
# plot the part elements
model.plot_elements(model_name + '_elem', display=show_gui)

# set loads and constraints
model.set_load('press', air_lines, press_atm)
model.set_fluid_press(water_lines, dens_water, grav, water_ht_m,
                      press_atm)
model.set_gravity(grav, part)
model.set_constr('fix', part.bottom, 'x')
model.set_constr('fix', part.bottom, 'y')
model.plot_pressures(model_name + '_press_1', display=show_gui)
model.plot_constraints(model_name + '_constr', display=show_gui)

# make model and solve it
prob = pyc.Problem(model, 'struct')
prob.solve()

# query results and store them
disp = False    # turn off display plotting
fields = 'Seqv,S1,S2,S3'    # store the fields to write
fields = fields.split(',')

for time in prob.rfile.steps:
    prob.rfile.set_time(time)
    for field in fields:
        fname = '%s_%i_%s' % (model_name, int(time), field)
        # nodal plotting
        prob.rfile.nplot(field, fname + '_n', display=disp)
        if 'S' in field:
            # element plotting
            prob.rfile.eplot(field, fname + '_e', display=disp)
