'''
   MFEM example 1p

   See c++ version in the MFEM library for more detail 
'''
import sys
import os
from os.path import expanduser, join
import numpy as np

from mpi4py import MPI

from mfem.common.arg_parser import ArgParser
from mfem import path
import mfem.par as mfem

def_meshfile = expanduser(join(path, 'data', 'star.mesh'))

num_proc = MPI.COMM_WORLD.size
myid     = MPI.COMM_WORLD.rank

def run(order = 1, static_cond = False,
        meshfile = def_meshfile, visualization = False,
        use_strumpack = False):

   mesh = mfem.Mesh(meshfile, 1,1)
   dim = mesh.Dimension()

   ref_levels = int(np.floor(np.log(10000./mesh.GetNE())/np.log(2.)/dim))
   for x in range(ref_levels):
      mesh.UniformRefinement();
   mesh.ReorientTetMesh();
   pmesh = mfem.ParMesh(MPI.COMM_WORLD, mesh)
   del mesh

   par_ref_levels = 2
   for l in range(par_ref_levels):
       pmesh.UniformRefinement();

   if order > 0:
       fec = mfem.H1_FECollection(order, dim)
   elif mesh.GetNodes():
       fec = mesh.GetNodes().OwnFEC()
       print( "Using isoparametric FEs: " + str(fec.Name()));
   else:
       order = 1
       fec = mfem.H1_FECollection(order, dim)

   fespace =mfem.ParFiniteElementSpace(pmesh, fec)
   fe_size = fespace.GlobalTrueVSize()

   if (myid == 0):
      print('Number of finite element unknowns: '+  str(fe_size))

   ess_tdof_list = mfem.intArray()
   if pmesh.bdr_attributes.Size()>0:
       ess_bdr = mfem.intArray(pmesh.bdr_attributes.Max())
       ess_bdr.Assign(1)
       fespace.GetEssentialTrueDofs(ess_bdr, ess_tdof_list)

   #   the basis functions in the finite element fespace.
   b = mfem.ParLinearForm(fespace)
   one = mfem.ConstantCoefficient(1.0)
   b.AddDomainIntegrator(mfem.DomainLFIntegrator(one))
   b.Assemble();

   x = mfem.ParGridFunction(fespace);
   x.Assign(0.0)

   a = mfem.ParBilinearForm(fespace);
   a.AddDomainIntegrator(mfem.DiffusionIntegrator(one))

   if static_cond: a.EnableStaticCondensation()
   a.Assemble();

   A = mfem.HypreParMatrix()
   B = mfem.Vector()
   X = mfem.Vector()
   a.FormLinearSystem(ess_tdof_list, x, b, A, X, B)

   if (myid == 0):
      print("Size of linear system: " + str(x.Size()))
      print("Size of linear system: " + str(A.GetGlobalNumRows()))

   if use_strumpack:
       import mfem.par.strumpack as strmpk
       Arow = strmpk.STRUMPACKRowLocMatrix(A)
       args = ["--sp_hss_min_sep_size", "128", "--sp_enable_hss"]
       strumpack = strmpk.STRUMPACKSolver(args, MPI.COMM_WORLD)
       strumpack.SetPrintFactorStatistics(True)
       strumpack.SetPrintSolveStatistics(False)
       strumpack.SetKrylovSolver(strmpk.KrylovSolver_DIRECT);
       strumpack.SetReorderingStrategy(strmpk.ReorderingStrategy_METIS)
       strumpack.SetMC64Job(strmpk.MC64Job_NONE)
       # strumpack.SetSymmetricPattern(True)
       strumpack.SetOperator(Arow)
       strumpack.SetFromCommandLine()
       strumpack.Mult(B, X);

   else:
       amg = mfem.HypreBoomerAMG(A)
       cg = mfem.CGSolver(MPI.COMM_WORLD)
       cg.SetRelTol(1e-12)
       cg.SetMaxIter(200)
       cg.SetPrintLevel(1)
       cg.SetPreconditioner(amg)
       cg.SetOperator(A)
       cg.Mult(B, X);


   a.RecoverFEMSolution(X, b, x)

   smyid = '{:0>6d}'.format(myid)
   mesh_name  =  "mesh."+smyid
   sol_name   =  "sol."+smyid

   pmesh.Print(mesh_name, 8)
   x.Save(sol_name, 8)

if __name__ == "__main__":
   parser = ArgParser(description='Ex1 (Laplace Problem)')
   parser.add_argument('-m', '--mesh',
                       default = 'star.mesh',
                       action = 'store', type = str,
                       help='Mesh file to use.')
   parser.add_argument('-vis', '--visualization',
                       action = 'store_true',
                       help='Enable GLVis visualization')
   parser.add_argument('-o', '--order',
                       action = 'store', default = 1, type=int,
                       help = "Finite element order (polynomial degree) or -1 for isoparametric space.");
   parser.add_argument('-sc', '--static-condensation',
                       action = 'store_true', 
                       help = "Enable static condensation.")
   parser.add_argument("-sp", "--strumpack",
                   action = 'store_true', default = False,
                   help =  "Use the STRUMPACK Solver.")
   
   args = parser.parse_args()

   if myid == 0: parser.print_options(args)

   order = args.order
   static_cond = args.static_condensation
   meshfile = expanduser(join(os.path.dirname(__file__), '..', 'data', args.mesh))   
   visualization = args.visualization
   use_strumpack = args.strumpack
   run(order = order, static_cond = static_cond,
       meshfile = meshfile, visualization = visualization,
       use_strumpack = use_strumpack)
   




