"""
================================================================================
Bump mesh convergence
================================================================================

In this example mesh convergence is carried out in the case of a bump.
H and QX errors are computed by comparison to single layer 1D analytical solution.

"""
import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
import freshkiss3d as fk
import freshkiss3d.extra.plots as fk_plt

#sphinx_gallery_thumbnail_number = 5

os.system('rm -r outputs')

################################################################################
#
#Mesh parameters:
#--------------------

N_mesh = 4 #Number of mesh for mesh convergence
First_mesh = 2
NL = [1 for r in range(N_mesh)]

################################################################################
#
#Case parameters:
#--------------------

FLOW = 'sub'

if FLOW == 'sub':
    FREE_SURFACE_0 = 0.7
    Q_IN = 0.2 
if FLOW == 'trans':
    FREE_SURFACE_0 = 0.7
    Q_IN = 1.5
if FLOW == 'trans_shock':
    FREE_SURFACE_0 = 0.33
    Q_IN = 0.18

H_OUT = FREE_SURFACE_0
FINAL_TIME = 1000.

WHEN = [5.99*FINAL_TIME/6.]
MESH_SPLITTING = False
PLOT_MESH = True
PLOT_SOL = False
PLOT_ERROR = True
SAVE_ERROR = True

X_B = 10.
def topo(x):
    if 8.< x <12.:
        topo = 0.2 - 0.05*(x - X_B)**2
    else:
        topo = 0.0
    return topo

def topo_gaussian(x):
    topo = 0.25*np.exp(-0.5*(x-X_B)**2)
    return topo

################################################################################
#  
#Lists initialization: 
#-----------------------

cases = []
simutime_list = []
triangular_mesh_list = []
NT = []
layer_list = []
primitives_list = []
problem_list = []
bump_analytic_list = []

################################################################################
#
#Meshes:
#--------------------

for M in range(N_mesh):
    if MESH_SPLITTING:
        #Generates first mesh from bump0.geo and the other by splitting of the first mesh
        if M == 0:
            os.system('gmsh -2 inputs/bump{}.geo -o inputs/bump{}.msh'.format(First_mesh, First_mesh))
            TG, vertex_labels, boundary_labels = fk.read_msh('inputs/bump{}.msh'.format(First_mesh))
            triangular_mesh = fk.TriangularMesh(TG, vertex_labels, boundary_labels)
            triangular_mesh_list.append(triangular_mesh)
            os.system('rm inputs/bump{}.msh'.format(First_mesh))
        else:
            triangular_mesh = triangular_mesh.refine_by_splitting()
            triangular_mesh_list.append(triangular_mesh)
    else:
        #Generates all meshes from bump#.geo files
        os.system('gmsh -2 inputs/bump{}.geo -o inputs/bump{}.msh'.format(M, M))
        TG, vertex_labels, boundary_labels = fk.read_msh('inputs/bump{}.msh'.format(M))
        triangular_mesh_list.append(fk.TriangularMesh(TG, vertex_labels, boundary_labels))
        os.system('rm inputs/bump{}.msh'.format(M))

    NT.append(triangular_mesh_list[M].NT)
    if PLOT_MESH: fk_plt.plot_mesh(triangular_mesh_list[M])

################################################################################
#
# Cases:
#--------------------
#
#Here we define cases based on a ``case`` class containing info such as space order 
#or time order for each simulation we want to run.

class case():
    def __init__(self, NL=1, mesh_id=0, time_order=False, space_order=False):
        self.NL = NL
        self.mesh_id = mesh_id
        self.time_order = time_order
        self.space_order = space_order
        self.ipres = False
        if space_order is True:
            self.order = 2
        else:
            self.order = 1

for M in range(N_mesh):
    cases.append(case(NL=NL[M], mesh_id=M, time_order=False, space_order=False))
    cases.append(case(NL=NL[M], mesh_id=M, time_order=True, space_order=True))

################################################################################
#
#Boundary conditions 
#--------------------
#
#Here we define boundary conditions, which are the same for every cases.

fluvial_flowrates = [fk.FluvialFlowRate(ref=4, flowrate=Q_IN,
                                        x_flux_direction=1.0,
                                        y_flux_direction=0.0)]
fluvial_heights = [fk.FluvialHeight(ref=2, height=H_OUT)]
torrential_outs = [fk.TorrentialOut(ref=2)]
slides = [fk.Slide(ref=3), fk.Slide(ref=1)]

################################################################################
#
# Solving (loop over all cases):
#-------------------------------

for I, case in enumerate(cases):
    print(" ")
    print(" ")
    print("                           SOLVING CASE {}                   ".format(I))
    print(" ")
    print(" ")

    mesh_id = case.mesh_id
    time_second_order = case.time_order
    numerical_params = {
        'space_second_order':case.space_order,
        'ipres':case.ipres}

    simutime_list.append(fk.SimuTime(
        final_time=FINAL_TIME,
        time_iteration_max=1000000,
        second_order=time_second_order))

    bump_analytic_list.append(fk.Bump(
        triangular_mesh_list[mesh_id],
        case=FLOW,
        q_in=Q_IN,
        h_out=H_OUT,
        free_surface_init=FREE_SURFACE_0,
        x_b = X_B,
        topo = topo_gaussian,
        scheduler=fk.schedules(times=WHEN),
        compute_error=True,
        error_type='L2',
        error_output='txt'))

    bump_analytic_list[I](0.)

    layer_list.append(fk.Layer(
        case.NL, triangular_mesh_list[mesh_id],
        topography=bump_analytic_list[I].topography))

    primitives_list.append(fk.Primitive(
        triangular_mesh_list[mesh_id],
        layer_list[I],
        free_surface=FREE_SURFACE_0,
        QXinit=Q_IN,
        QYinit=0.))

    if PLOT_SOL:
        create_figure = {'plot':fk_plt.plot_freesurface_3d_analytic}
        create_figure_scheduler = fk.schedules(times=[0.99*FINAL_TIME])
    else:
        create_figure = None
        create_figure_scheduler = None

    problem_list.append(fk.Problem(
        simutime_list[I], triangular_mesh_list[mesh_id],
        layer_list[I], primitives_list[I],
        analytic_sol=bump_analytic_list[I],
        numerical_parameters=numerical_params,
        fluvial_flowrates=fluvial_flowrates,
        fluvial_heights=fluvial_heights,
        slides=slides,
        custom_funct=create_figure,
        custom_funct_scheduler=create_figure_scheduler))

    problem_list[I].solve()

    if PLOT_SOL: plt.show()

################################################################################
#
# Errors:
#--------------------
# 
#Errors computed during solving loop are stored in ``error_*`` matrix.

error_H = np.zeros((N_mesh, 2))
error_QX = np.zeros((N_mesh, 2))
error_QY = np.zeros((N_mesh, 2))
for I, case in enumerate(cases):
    sol = problem_list[I].analytic_sol
    error_H[case.mesh_id, case.order-1] = sol.error_H
    error_QX[case.mesh_id, case.order-1] = sol.error_QX
    error_QY[case.mesh_id, case.order-1] = sol.error_QY

################################################################################
#
#Errors are save in h5 format in \data repertory. 

if SAVE_ERROR:
    os.system('rm data/bump_errors.h5')
    REF_FILE = "data/bump_errors.h5"
    with h5py.File(REF_FILE, 'w') as f:
        f.create_dataset('NT', data=NT)
        f.create_dataset('NL', data=NL)
        f.create_dataset('error_H', data=error_H)
        f.create_dataset('error_QX', data=error_QX)
        f.create_dataset('error_QY', data=error_QY)

################################################################################
#
# Errors plots:
#--------------------
#

def plot_error(ax, cases, error):
    err = np.zeros((N_mesh))
    ab = np.zeros((N_mesh))

    for order in range(2):
        for M in range(N_mesh):
            err[M] = np.log(error[M, order])
            ab[M] = 0.5*np.log(NT[M]/NT[0])

        ax.plot(ab, err, color=colors[order], marker=markers[order], label=labels[order])

def plot_reference(ax, error):
    xmax = 0.5*np.log(NT[N_mesh-1]/NT[0])
    ax.plot([0.0, xmax], [np.log(error[0, 0]), -1.0*xmax+np.log(error[0, 0])],\
            color='k', ls=':', lw=0.5)
    ax.plot([0.0, xmax], [np.log(error[0, 1]), -1.0*xmax+np.log(error[0, 1])],\
            color='k', ls=':', lw=0.5)
    ax.plot([0.0, xmax], [np.log(error[0, 1]), -2.0*xmax+np.log(error[0, 1])],\
            color='k', ls='-.', lw=0.5)

if PLOT_ERROR == True:
    plt.rcParams["figure.figsize"] = [14, 6]
    colors = ['blue','red','green','purple']
    markers = ['s','*','o','v']
    labels = ['$1^{st}$ order','$2^{nd}$ order']
    fig = plt.figure()

    ax0 = fig.add_subplot(111)
    plot_error(ax0, cases, error_H)
    plot_reference(ax0, error_H)
    ax0.set_xlabel('$log(l_0/l_i)$')
    ax0.set_ylabel('Error of $h$ in $L_2$ norm')
    ax0.set_title("Convergence of $h$")
    plt.legend(loc=1)
    plt.show()

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    plot_error(ax1, cases, error_QX)
    plot_reference(ax1, error_QX)
    ax1.set_xlabel('$log(l_0/l_i)$')
    ax1.set_ylabel('Error of $hu$ in $L_2$ norm')
    ax1.set_title("Convergence of $hv$")
    plt.legend(loc=1)
    #plt.show()
