#!/usr/bin/env python
# coding: utf-8

# In[2]:


from sympy import *
from sympy.physics.quantum import *
from sympy.physics.quantum.density import *
from sympy.physics.quantum.spin import (
    Jx, Jy, Jz, Jplus, Jminus, J2,
    JxBra, JyBra, JzBra,
    JxKet, JyKet, JzKet,
)
from IPython.core.display import display_pretty
from sympy.physics.quantum.operator import *

get_ipython().run_line_magic('load_ext', 'sympyprinting')


# ##Fidelity using some kets

# In[7]:


up = JzKet(S(1)/2,S(1)/2)
down = JzKet(S(1)/2,-S(1)/2)
amp = 1/sqrt(2)
updown = (amp * up ) + (amp * down)

# represent turns Kets into matrices
up_dm = represent(up * Dagger(up))
down_dm = represent(down * Dagger(down)) 
updown_dm = represent(updown * Dagger(updown))
updown2 = (sqrt(3)/2 )* up + (1/2)*down


display_pretty(fidelity(up_dm, up_dm))
display_pretty(fidelity(up_dm, down_dm)) #orthogonal states
display_pretty(fidelity(up_dm, updown_dm).evalf())


# alternatively, puts Kets into Density object and compute fidelity
d1 = Density( [updown, 0.25], [updown2, 0.75])
d2 = Density( [updown, 0.75], [updown2, 0.25])
display_pretty(fidelity(d1, d2))


# ## Fidelity on states as Qubits

# In[9]:



from sympy.physics.quantum.qubit import Qubit
state1 = Qubit('0')
state2 = Qubit('1')
state3 = (1/sqrt(2))*state1 + (1/sqrt(2))*state2
state4 = (sqrt(S(2)/3))*state1 + (1/sqrt(3))*state2

state1_dm = Density([state1, 1])
state2_dm = Density([state2, 1])
state3_dm = Density([state3, 1])

# mixed qubit states in density
d1 = Density([state3, 0.70], [state4, 0.30])
d2 = Density([state3, 0.20], [state4, 0.80])


display_pretty(fidelity(d1, d2))


# In[ ]:




