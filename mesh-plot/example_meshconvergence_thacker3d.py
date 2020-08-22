"""
================================================================================
Thacker3d mesh convergence
================================================================================

In this example mesh convergence is carried out in the case of the thacker3d with
variable density. 

"""
import os
import h5py
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.image as mpimg
from mpl_toolkits.axes_grid1 import make_axes_locatable, axes_size
import freshkiss3d as fk
import freshkiss3d.extra.plots as fk_plt

#sphinx_gallery_thumbnail_number = 6

os.system('rm -r outputs')

################################################################################
#
#Mesh parameters:
#--------------------

N_mesh = 5 #Number of mesh for mesh convergence
First_mesh = 2
NL_start = 10
NL = [NL_start+2*r for r in range(N_mesh)]

################################################################################
#
#Case parameters:
#--------------------

H0 = 0.1
ETA = 0.1
ALPHA = 1.
A = 10.
L = 4.
OMEGA = np.sqrt(ALPHA*9.81)
PERIOD = 2.*np.pi/OMEGA
RHO_0 = 998.
FINAL_TIME = 1.*PERIOD

#Mesh options:
MESH_SPLITTING = False

#Plot options:
PLOT_MESH = True
PLOT_ERROR = True

#Error options:
DATA_REP = "data"
ERROR_TYPE = 'L2'
SAVE_ERROR = True
SECOND_ORDER = True

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
thacker3d_analytic_list = []
CPUTime_list = []

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
x *= 0.12
y *= 0.12
x -= 0.6
y -= 0.6
triangular_mesh_list.append( fk.TriangularMesh(TG, vertex_labels, boundary_labels) )
NT.append(triangular_mesh_list[0].NT)
if PLOT_MESH: fk_plt.plot_mesh(triangular_mesh_list[0])

for M in range(1, N_mesh):
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
        x *= 0.12
        y *= 0.12
        x -= 0.6
        y -= 0.6
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
        if space_order is True or time_order is True:
            self.order = 2
        else:
            self.order = 1

for M in range(N_mesh):
    cases.append(case(NL=NL[M], mesh_id=M, time_order=False, space_order=False))
    if SECOND_ORDER:
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
    start = time.time()
    print(" ")
    print(" ")
    print("                           SOLVING CASE {}                   ".format(I))
    print(" ")
    print(" ")

    mesh_id = case.mesh_id    
    time_second_order = case.time_order

    NUM_PARAMS={'ipres':case.ipres,
                'space_second_order':case.space_order,
                'velocity_correction':False,
                'rho_correction':True,
                'flux_type':2}

    PHY_PARAMS={'variable_density':True,
                'variable_density_model':'ns-fourier'} #'ns-fourier' or 'boussinesq'

    simutime_list.append(fk.SimuTime(
        final_time=FINAL_TIME, 
        time_iteration_max=10000,
        second_order=time_second_order))

    if PHY_PARAMS['variable_density_model'] == 'boussinesq':
        HAS_TRACER = True
        HAS_DENSITY = False
    elif PHY_PARAMS['variable_density_model'] == 'ns-fourier':
        HAS_TRACER = False
        HAS_DENSITY = True

    thacker3d_analytic_list.append(fk.Thacker3DVariableDensity(
        triangular_mesh_list[mesh_id], NL=case.NL,
        a=ALPHA, h0=H0, eta=ETA, L=L, b=A,
        density = HAS_DENSITY, tracer = HAS_TRACER,
        compute_error=True,
        error_type=ERROR_TYPE,
        error_output='none'))

    thacker3d_analytic_list[I](0.)

    layer_list.append(fk.Layer(
        case.NL,
        triangular_mesh_list[mesh_id],
        topography=thacker3d_analytic_list[I].topography))

    primitives_list.append(fk.Primitive(
        triangular_mesh_list[mesh_id],
        layer_list[I],
        height=thacker3d_analytic_list[I].H,
        Uinit=thacker3d_analytic_list[I].U,
        Vinit=thacker3d_analytic_list[I].V,
        HRhoinit=thacker3d_analytic_list[I].HRho))

    problem_list.append(fk.Problem(
        simutime_list[I], triangular_mesh_list[mesh_id],
        layer_list[I], primitives_list[I],
        analytic_sol=thacker3d_analytic_list[I],
        numerical_parameters=NUM_PARAMS,
        physical_parameters=PHY_PARAMS,
        fluvial_heights=fluvial_heights))

    problem_list[I].solve()

    CPUTime_list.append(time.time()-start)

error_H = np.zeros((N_mesh, 2))
error_QX = np.zeros((N_mesh, 2))
error_QY = np.zeros((N_mesh, 2))
error_Rho = np.zeros((N_mesh, 2))
error_H_cumul = np.zeros((N_mesh, 2))
error_QX_cumul = np.zeros((N_mesh, 2))
error_QY_cumul = np.zeros((N_mesh, 2))
error_Rho_cumul = np.zeros((N_mesh, 2))
CPUTime = np.zeros((N_mesh, 2))

for I, case in enumerate(cases):
    CPUTime[case.mesh_id, case.order-1] = CPUTime_list[I]
    sol = problem_list[I].analytic_sol
    error_H[case.mesh_id, case.order-1] = sol.error_H
    error_QX[case.mesh_id, case.order-1] = sol.error_QX
    error_QY[case.mesh_id, case.order-1] = sol.error_QY
    error_Rho[case.mesh_id, case.order-1] = sol.error_HRho
    error_H_cumul[case.mesh_id, case.order-1] = sol.error_H_cumul/FINAL_TIME
    error_QX_cumul[case.mesh_id, case.order-1] = sol.error_QX_cumul/FINAL_TIME
    error_QY_cumul[case.mesh_id, case.order-1] = sol.error_QY_cumul/FINAL_TIME
    error_Rho_cumul[case.mesh_id, case.order-1] = sol.error_HRho_cumul/FINAL_TIME

if SAVE_ERROR:
    os.system('mkdir {}'.format(DATA_REP))
    os.system('rm {}/thacker3d_errors.h5'.format(DATA_REP))
    REF_FILE = DATA_REP+"/thacker3d_errors.h5"
    with h5py.File(REF_FILE, 'w') as f:
        f.create_dataset('CPUTime', data=CPUTime)
        f.create_dataset('NT', data=NT)
        f.create_dataset('NL', data=NL)
        f.create_dataset('error_H', data=error_H)
        f.create_dataset('error_QX', data=error_QX)
        f.create_dataset('error_QY', data=error_QY)
        f.create_dataset('error_Rho', data=error_Rho)
        f.create_dataset('error_H_cumul', data=error_H_cumul)
        f.create_dataset('error_QX_cumul', data=error_QX_cumul)
        f.create_dataset('error_QY_cumul', data=error_QY_cumul)
        f.create_dataset('error_Rho_cumul', data=error_Rho_cumul)

################################################################################
#
# Errors plots:
#--------------------
#

def plot_error(ax, error):
    err = np.zeros((N_mesh))
    ab = np.zeros((N_mesh))
    if SECOND_ORDER:
        ORD = 2
    else:
        ORD = 1
    for order in range(ORD):
        for M in range(N_mesh):
            err[M] = np.log(error[M, order])
            #ab[M] = 0.5*np.log(NT[M]/NT[0])
            ab[M] = 0.5*np.log((NT[M]*NL[M])/(NT[0]*NL[0]))

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

    ax3 = fig.add_subplot(111)
    plot_error(ax3, error_Rho_cumul)
    plot_reference(ax3, error_Rho_cumul)
    ax3.set_xlabel('$log(l_0/l_i)$')
    ax3.set_ylabel('Error of $\\rho h$ in $L_2$ norm')
    ax3.set_title("Convergence of $\\rho h$")
    plt.legend(loc=1)
    plt.show()

    fig = plt.figure()

    ax0 = fig.add_subplot(111)
    plot_error(ax0, error_H_cumul)
    plot_reference(ax0, error_H_cumul)
    ax0.set_xlabel('$log(l_0/l_i)$')
    ax0.set_ylabel('Error of $h$ in $L_2$ norm')
    ax0.set_title("Convergence of $h$")
    plt.legend(loc=1)
    plt.show()
