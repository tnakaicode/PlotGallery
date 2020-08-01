#!/usr/bin/env python
# coding: utf-8

# In[2]:


from sympy import symbols
from sympy.core.trace import Tr
from sympy.matrices.matrices import Matrix
from IPython.core.display import display_pretty
from sympy.printing.latex import *

get_ipython().run_line_magic('load_ext', 'sympyprinting')


# ###Basic Examples

# In[3]:


a, b, c, d = symbols('a b c d'); 
A, B = symbols('A B', commutative=False)
t = Tr(A*B)


# In[4]:


t


# In[5]:


latex(t)


# In[14]:


display_pretty(t)


# ### Using Matrices

# In[15]:


t = Tr ( Matrix([ [2,3], [3,4] ]))


# In[16]:


t


# ### Example using modules in physics.quantum

# In[7]:


from sympy.physics.quantum.density import Density
from sympy.physics.quantum.spin import (
    Jx, Jy, Jz, Jplus, Jminus, J2,
    JxBra, JyBra, JzBra,
    JxKet, JyKet, JzKet,
)


# In[8]:


d = Density([JzKet(1,1),0.5],[JzKet(1,-1),0.5]); d


# In[9]:


t = Tr(d)


# In[10]:


t


# In[11]:


latex(t)


# In[12]:


t.doit()


# In[12]:




