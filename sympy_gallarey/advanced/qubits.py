#!/usr/bin/env python
# coding: utf-8

# In[4]:


from sympy import symbols
from sympy.core.trace import Tr
from sympy.matrices.matrices import Matrix
from IPython.core.display import display_pretty
from sympy.printing.latex import *
from sympy.physics.quantum.cartesian import *
from sympy.physics.quantum.qubit import *
from sympy.physics.quantum.density import *

get_ipython().run_line_magic('load_ext', 'sympyprinting')

#TODO: Add examples of simple qubit usage 


# ## Examples of Tr operations on Qubits

# In[2]:


q1 = Qubit('10110')
q2 = Qubit('01010')
d = Density( [q1, 0.6], [q2, 0.4] )

# Trace one bit 
t = Tr(d,[0])

display_pretty(t.doit())


# Partial trace of 3 qubits
# the 0th bit is the right-most bit
t = Tr(d,[2, 1, 3])
display_pretty(t.doit())


# ## Partial Tr of mixed state

# In[3]:


from sympy import *
q = (1/sqrt(2)) * (Qubit('00') + Qubit('11'))

d = Density ( [q, 1.0] )
t = Tr(d, [0])
display_pretty(t.doit())


# In[3]:




