'''
 This example shows
   constructing HYPREParCSR in a distributed manner
     1) build scipy.sparse on each node
           each node has informaiton of small number of rows
     2) assemble it to HYPREParCSR
           scipy matries are concatenated vertical

   convert back ParCSR to scipy.sparse
     1) on each node, it produce scipy.sparse which contain
        only its own rows.


   example_2 tests
      concatenate 2 of 2x5 matrices and one 1x5 to form 5x5
      peform ParMMULTI, RAP, and ParAdd 
      works only for mpirun -np 3 (3 cpu)

'''
import mfem.par as par
from mfem.common.parcsr_extra import *

from scipy.sparse import csr_matrix, coo_matrix

from mpi4py import MPI
comm     = MPI.COMM_WORLD     
num_proc = MPI.COMM_WORLD.size
myid     = MPI.COMM_WORLD.rank

def print_hypre(M, txt):
    for i in range(num_proc):
       MPI.COMM_WORLD.Barrier()                              
       if myid == i:
          if myid == 0:
              print(txt)
              print('MyID: ', myid)
          else:
              print('MyID: ', myid)
          print(ToScipyCoo(M))

shape = (2, 5) if myid < 2 else (1, 5)
# make sample matrix
row  = np.array([0, 0, 0, 0])
col  = np.array([0, 3, 1, 4])
data = np.array([4, 5, 7, 9])
m = coo_matrix((data, (row, col)), shape=shape)
m = m.tocsr()
m = m*(myid+1)

M = ToHypreParCSR(m)
print_hypre(M, 'matrix M')

# make sample matrix
if True:
   row  = np.array([0, 0, 0, 0])
   col  = np.array([4, 3, 1, 2])
   data = np.array([4, 10,7, 2 ])
   m = coo_matrix((data, (row, col)), shape=shape).tocsr()
   M2 = ToHypreParCSR(m)
else:
   m2 = ToScipyCoo(M)
   M2 = ToHypreParCSR(m2.tocsr())
#print ToScipyCoo(M2)

# adding matrix
M3 = ParAdd(M, M2)


print_hypre(M3, 'summed matrix')
print_hypre(mfem.ParMult(M, M2.Transpose()), 'parmult (A*B)') #ok
print_hypre(mfem.RAP(M, M2.Transpose()), 'rap (B A Bt)')      #ok
print_hypre(mfem.ParMult(M, M2), 'parmult (A*Bt)')            #ok
print_hypre(mfem.RAP(M, M2), 'rap (Bt A B)')                  #ok



