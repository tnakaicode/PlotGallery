import numpy as np
import argiope as ag

# NODE COORDINATES
coords =  np.array([[0., 0., 0.], #1
                    [1., 0., 0.], #2 
                    [2., 0., 0.], #3
                    [1., 1., 0.], #4
                    [0., 1., 0.], #5
                    [0., 0., 1.], #6
                    [1., 0., 1.], #7 
                    [2., 0., 1.], #8
                    [1., 1., 1.], #9
                    [0., 1., 1.], #10
                    [0., 0., 2.], #11
                    [1., 0., 2.], #12
                    [2., 0., 2.], #13
                    [1., 1., 2.], #14
                    [0., 1., 2.], #15
                    [1., 0., 3.], #16
                    ])

# NODE LABELS
nlabels = np.arange(len(coords)) +1                    

# NODE SETS
nsets = {"nset1": nlabels > 2}              

# CONNECTIVITY : 
# Warning = nothing, only used to ensure renctangularity of the table.
conn =  [[ 1,  2,  4,  5,  0,  0,  0,  0], #1 = QUAD4
         [ 2,  3,  4,  0,  0,  0,  0,  0], #2 = TRI3
         [ 6,  7,  9, 10, 11, 12, 14, 15], # 3 = HEXA8
         [ 7,  8,  9, 12, 13, 14,  0,  0], # 4 = PRISM6
         [12, 13, 14, 16,  0,  0,  0,  0], # 5 = TETRA4
        ]

elabels = np.arange(1, len(conn) + 1)

types =  np.array(["quad4", "tri3", "hexa8", "prism6", "tetra4"])         

stypes = np.array(["CPS4", "CAX3", "C3D8", 
                   "C3D6", "C3D4"]) # Abaqus element naming convention.

esets = {"eset1": elabels < 2}       

materials = np.array(["mat1", "mat2", "mat2", "mat2", "mat2"])

mesh = ag.mesh.Mesh(nlabels = nlabels,
                    coords  = coords,
                    nsets   = nsets,
                    conn    = conn,
                    elabels = elabels,
                    esets   = esets,
                    types   = types,
                    stypes  = stypes,
                    )
