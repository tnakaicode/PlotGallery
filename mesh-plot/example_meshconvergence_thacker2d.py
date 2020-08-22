"""
================================================================================
Thacker2d mesh convergence
================================================================================

In this example mesh convergence is carried out in the case of the thacker2d.
H, QX and QY errors are computed by comparison to single layer analytical solution.

"""
import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
import freshkiss3d as fk
import freshkiss3d.extra.plots as fk_plt

#sphinx_gallery_thumbnail_number = 7

################################################################################
#
#Mesh parameters:
#--------------------

N_mesh = 5 #Number of mesh for mesh convergence
First_mesh = 2
NL = [1 for r in range(N_mesh)]

################################################################################
#
#Case parameters:
#--------------------

PERIOD = 2.*np.pi/(np.sqrt(2.*9.81*0.1)) #une période: 4.485s
FINAL_TIME = 1.*PERIOD
MESH_SPLITTING = False
PLOT_MESH = True
PLOT_SOL = False
PLOT_ERROR = True
SAVE_ERROR = True

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
thacker2d_analytic_list = []

################################################################################
#
#Meshes:
#--------------------

os.system('gmsh -2 inputs/thacker2d{}.geo -o inputs/thacker2d{}.msh'.format(First_mesh, First_mesh))
TG, vertex_labels, boundary_labels = fk.read_msh('inputs/thacker2d{}.msh'.format(First_mesh))
os.system('rm inputs/thacker2d{}.msh'.format(First_mesh))
x = np.asarray(TG.x)
y = np.asarray(TG.y)
trivtx = np.asarray(TG.trivtx)
x *= 0.4
y *= 0.4
triangular_mesh_list.append( fk.TriangularMesh(TG, vertex_labels, boundary_labels) )
NT.append(triangular_mesh_list[0].NT)
if PLOT_MESH: fk_plt.plot_mesh(triangular_mesh_list[0])

for M in range(1, N_mesh):
    print(M)
    if MESH_SPLITTING:
        triangular_mesh_list.append( triangular_mesh_list[M-1].refine_by_splitting() )
        NT.append( triangular_mesh_list[M].NT)
        if PLOT_MESH: fk_plt.plot_mesh(triangular_mesh_list[M])
    else:
        mesh_id = First_mesh+M
        os.system('gmsh -2 inputs/thacker2d{}.geo -o inputs/thacker2d{}.msh'.format(mesh_id, mesh_id))
        TG, vertex_labels, boundary_labels = fk.read_msh('inputs/thacker2d{}.msh'.format(mesh_id))
        os.system('rm inputs/thacker2d{}.msh'.format(mesh_id))
        x = np.asarray(TG.x)
        y = np.asarray(TG.y)
        trivtx = np.asarray(TG.trivtx)
        x *= 0.4
        y *= 0.4
        triangular_mesh_list.append( fk.TriangularMesh(TG, vertex_labels, boundary_labels) )
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
        self.ipres = True
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

fluvial_heights = [ fk.FluvialHeight(ref=r, height=0.0) for r in [1,2,3,4] ]

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
        time_iteration_max=10000,
        second_order=time_second_order))

    thacker2d_analytic_list.append(fk.Thacker2D(
        triangular_mesh_list[mesh_id],
        a=1., h0=0.1,
        compute_error=True,
        error_type='L2',
        error_output='txt'))

    thacker2d_analytic_list[I](0.)

    layer_list.append(fk.Layer(
        case.NL,
        triangular_mesh_list[mesh_id], 
        topography=thacker2d_analytic_list[I].topography))

    primitives_list.append(fk.Primitive(
        triangular_mesh_list[mesh_id],
        layer_list[I],
        height=thacker2d_analytic_list[I].H,
        Uinit=thacker2d_analytic_list[I].U,
        Vinit=thacker2d_analytic_list[I].V)) 

    if PLOT_SOL:
        create_figure = {'plot':fk_plt.plot_freesurface_3d_analytic_2}
        create_figure_scheduler = fk.schedules(times=[0.99*FINAL_TIME])
    else:
        create_figure = None
        create_figure_scheduler = None

    problem_list.append(fk.Problem(
        simutime_list[I], triangular_mesh_list[mesh_id],
        layer_list[I], primitives_list[I],
        analytic_sol=thacker2d_analytic_list[I],
        numerical_parameters=numerical_params,
        fluvial_heights=fluvial_heights,
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
error_H_cumul = np.zeros((N_mesh, 2))
error_QX_cumul = np.zeros((N_mesh, 2))
error_QY_cumul = np.zeros((N_mesh, 2))

for I, case in enumerate(cases):
    sol = problem_list[I].analytic_sol
    error_H[case.mesh_id, case.order-1] = sol.error_H
    error_QX[case.mesh_id, case.order-1] = sol.error_QX
    error_QY[case.mesh_id, case.order-1] = sol.error_QY
    error_H_cumul[case.mesh_id, case.order-1] = sol.error_H_cumul/FINAL_TIME
    error_QX_cumul[case.mesh_id, case.order-1] = sol.error_QX_cumul/FINAL_TIME
    error_QY_cumul[case.mesh_id, case.order-1] = sol.error_QY_cumul/FINAL_TIME

################################################################################
#
#Errors are save in h5 format in \data repertory. 

if SAVE_ERROR:
    os.system('rm data/thacker2d_errors.h5')
    REF_FILE = "data/thacker2d_errors.h5"
    with h5py.File(REF_FILE, 'w') as f:
        f.create_dataset('NT', data=NT)
        f.create_dataset('NL', data=NL)
        f.create_dataset('error_H', data=error_H)
        f.create_dataset('error_QX', data=error_QX)
        f.create_dataset('error_QY', data=error_QY)
        f.create_dataset('error_H_cumul', data=error_H_cumul)
        f.create_dataset('error_QX_cumul', data=error_QX_cumul)
        f.create_dataset('error_QY_cumul', data=error_QY_cumul)

################################################################################
#
# Errors plots:
#--------------------
#

def plot_error(ax, error):
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
    ax.plot([0.0, xmax], [np.log(error[0, 1]), -2.0*xmax+np.log(error[0, 1])],\
            color='k', ls='-.', lw=0.5)

if PLOT_ERROR == True:
    plt.rcParams["figure.figsize"] = [10, 5]
    colors = ['blue','red','green','purple']
    markers = ['s','*','o','v']
    labels = ['$1^{st}$ order','$2^{nd}$ order']
    fig = plt.figure()

    ax0 = fig.add_subplot(111)
    plot_error(ax0, error_H_cumul)
    plot_reference(ax0, error_H_cumul)
    ax0.set_xlabel('$log(l_0/l_i)$')
    ax0.set_ylabel('Error of $h$ in $L_2$ norm')
    ax0.set_title("Convergence of $h$")
    plt.legend(loc=1)
    plt.show()

    fig = plt.figure()

    ax1 = fig.add_subplot(121)
    plot_error(ax1, error_QX_cumul)
    plot_reference(ax1, error_QX_cumul)
    ax1.set_xlabel('$log(l_0/l_i)$')
    ax1.set_ylabel('Error of $hu$ in $L_2$ norm')
    ax1.set_title("Convergence of $hu$")
    plt.legend(loc=3)

    ax2 = fig.add_subplot(122)
    plot_error(ax2, error_QY_cumul)
    plot_reference(ax2, error_QY_cumul)
    ax2.set_xlabel('$log(l_0/l_i)$')
    ax2.set_ylabel('Error of $hv$ in $L_2$ norm')
    ax2.set_title("Convergence of $hv$")
    plt.legend(loc=3)

    plt.show()

os.system('rm -r outputs')
