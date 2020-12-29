# encoding: utf-8
import matplotlib.pyplot as plt

from pyGDM2 import fields

from pyGDM2 import tools
from pyGDM2 import visu






## --- Setup incident field: Oblique plane wave with reflection at lossy interface
field_generator = fields.evanescent_planewave
kwargs = dict(theta_inc=45, polar='p', returnField='E')






n3 = 1.0            # vacuum
n2 = 1.05 + 1.8j    # lossy interface layer (metallic)
spacing = 40.0      # thickness of interface layer
n1 = 1.5            # dielectric substrate

wavelength = 500
## --- 2D evaluation volume (plane)
projection = 'XZ'
r_probe = tools.generate_NF_map(-500,500,30, -400,600,30,0, projection=projection)

NF = tools.evaluate_incident_field(field_generator, wavelength, kwargs, r_probe, 
                            n1=n1,n2=n2,n3=n3, spacing=spacing)





#%%
#==============================================================================
# visualization 
#==============================================================================
## -- helper function to plot the interface layer
def plot_layer():
    plt.axhline(0, color='w',lw=1); plt.axhline(0, dashes=[2,2], color='k',lw=1)
    plt.axhspan(0,spacing, color='k', ls='--', fc='orange', alpha=0.35)
    plt.axhline(spacing, color='w',lw=1); plt.axhline(spacing, dashes=[2,2], color='k',lw=1)
    plt.arrow(350, -350, -150, 150, head_width=50, head_length=80, fc='k', ec='k')

            


plt.figure(figsize=(6,3.6))

plt.suptitle("oblique plane wave, reflected at glass/gold interface", fontsize=13)

plt.subplot(121, aspect='equal')
v = visu.vectorfield(NF, complex_part='real', projection=projection, tit=projection+' real part', show=0)
plt.xlabel("X (nm)")
plt.ylabel("Z (nm)")
plot_layer()

plt.subplot(122, aspect='equal')
v = visu.vectorfield(NF, complex_part='imag', cmap=plt.cm.Reds, projection=projection, tit=projection+' imag part',  show=0)
plt.xlabel("X (nm)")
plot_layer()

plt.tight_layout()
plt.savefig("incident_field.png", dpi=150)
plt.show()


