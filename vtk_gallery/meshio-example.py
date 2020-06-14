import numpy as np
import matplotlib.pyplot as plt
import meshio
reader = meshio.read("pep1_7_OmegaV.vtu")

print(reader.points)
print(reader.cells)

x = reader.points
triangles = reader.cells['triangle']
print(reader.point_data)

u = reader.point_data['abs_term_u']

fig, axs = plt.subplots()
axs.set_aspect("equal")
axs.triplot(x[:, 0], x[:, 1], triangles)

fig, axs = plt.subplots()
axs.set_aspect("equal")
axs.tricontour(x[:, 0], x[:, 1], triangles, u, 16)

fig, axs = plt.subplots()
axs.set_aspect("equal")
axs.tricontourf(x[:, 0], x[:, 1], triangles, u, 16)
plt.show()
