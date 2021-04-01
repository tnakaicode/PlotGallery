import argiope as ag
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

mesh = ag.mesh.read_msh("demo.msh")
"""
mesh = ag.mesh.read_msh("sample_mesh_2D.msh")
mesh.elements = mesh.elements.loc[mesh.space() == 2]
"""
edge_color = "black"
face_color = "blue"
edge_width = .2
"""
nodes, elements = mesh.nodes.data, mesh.elements.data
#NODES
nodes_map = np.arange(nodes.index.max()+1)
nodes_map[nodes.index] = np.arange(len(nodes.index))
nodes_map[0] = -1
coords = nodes.as_matrix()
#ELEMENTS
cols = mesh.elements._connectivity_keys()
connectivities  = elements[cols].as_matrix()
connectivities[np.isnan(connectivities)] = 0
connectivities = connectivities.astype(np.int32)
connectivities = nodes_map[connectivities]
#labels          = np.array(elements.index)
etype           = np.array(elements.etype)
#FACES

 
  
#CENTROIDS & VOLUME
centroids, volumes = [], []
for i in xrange(len(etype)):
  simplices = connectivities[i][ag.mesh.ELEMENTS[etype[i]]["simplex"]]
  simplices = np.array([ [coords[n] for n in simp] for simp in simplices])
  v = np.array([ag.mesh.tri_area(simp) for simp in simplices])
  g = np.array([simp.mean(axis=0) for simp in simplices])
  vol = v.sum()
  centroids.append((g.transpose()*v).sum(axis=1) / vol)
  volumes.append(vol)
centroids = np.array(centroids)
volumes   = np.array(volumes)
"""
tri = mesh.to_triangulation()
patches = mesh.to_polycollection(facecolor = "none",
                                 edgecolor = "black",
                                 linewidth = .5)
def field(x, y):
  r = ((y-.5)**2 +(x-.5)**2)**.5
  return np.cos(4. * np.pi *r) + 4 * x 
v = field(tri.x, tri.y) 




fig = plt.figure()
ax = fig.add_subplot(1,1,1)
ax.set_aspect("equal")
ax.set_xlim(-.1, 1.)
ax.set_ylim(-.1, 1.)

grad = ax.tricontourf(tri, v, 10,  cmap = mpl.cm.jet)
ax.tricontour(tri, v, 10, colors = "white", linewidth = 4.)
ax.add_collection(patches)
cbar = plt.colorbar(grad)
cbar.set_label("Some field, $f$")

#plt.plot(centroids[:,0], centroids[:,1], ",k")
plt.axis('off')
plt.xticks([0.,.5,  1.])
plt.yticks([0.,.5,  1.])
plt.xlabel("$x$")
plt.ylabel("$y$")
plt.grid()
path = "Mesh-to_triangulation.pdf"
plt.savefig(path)



        
                        
