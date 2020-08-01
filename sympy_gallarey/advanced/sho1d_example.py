#!/usr/bin/env python
# coding: utf-8

# # Example Notebook for sho1d.py

# Import the sho1d.py file as well as the test_sho1d.py file

# In[1]:


get_ipython().run_line_magic('load_ext', 'sympy.interactive.ipythonprinting')
from sympy import *
from IPython.display import display_pretty
from sympy.physics.quantum import *
from sympy.physics.quantum.sho1d import *
from sympy.physics.quantum.tests.test_sho1d import *


# ### Printing Of Operators

# Create a raising and lowering operator and make sure they print correctly

# In[2]:


ad = RaisingOp('a')
a = LoweringOp('a')


# In[3]:


ad


# In[4]:


a


# In[5]:


print latex(ad)
print latex(a)


# In[6]:


display_pretty(ad)
display_pretty(a)


# In[7]:


print srepr(ad)
print srepr(a)


# In[8]:


print repr(ad)
print repr(a)


# ### Printing of States

# Create a simple harmonic state and check its printing

# In[9]:


k = SHOKet('k')
b = SHOBra('b')


# In[10]:


k


# In[11]:


b


# In[12]:


print pretty(k)
print pretty(b)


# In[13]:


print latex(k)
print latex(b)


# In[14]:


print srepr(k)
print srepr(b)


# ### Properties

# Take the dagger of the raising and lowering operators. They should return each other.

# In[15]:


Dagger(ad)


# In[16]:


Dagger(a)


# Check Commutators of the raising and lowering operators

# In[17]:


Commutator(ad,a).doit()


# In[18]:


Commutator(a,ad).doit()


# Take a look at the dual states of the bra and ket

# In[19]:


k.dual


# In[20]:


b.dual


# Taking the InnerProduct of the bra and ket will return the KroneckerDelta function

# In[21]:


InnerProduct(b,k).doit()


# Take a look at how the raising and lowering operators act on states. We use qapply to apply an operator to a state

# In[22]:


qapply(ad*k)


# In[23]:


qapply(a*k)


# But the states may have an explicit energy level. Let's look at the ground and first excited states

# In[24]:


kg = SHOKet(0)
kf = SHOKet(1)


# In[25]:


qapply(ad*kg)


# In[26]:


qapply(ad*kf)


# In[27]:


qapply(a*kg)


# In[28]:


qapply(a*kf)


# Notice that a*kg is 0 and a*kf is the |0> the ground state.

# ### NumberOp & Hamiltonian

# Let's look at the Number Operator and Hamiltonian Operator

# In[29]:


k = SHOKet('k')
ad = RaisingOp('a')
a = LoweringOp('a')
N = NumberOp('N')
H = Hamiltonian('H')


# The number operator is simply expressed as ad*a

# In[30]:


N().rewrite('a').doit()


# The number operator expressed in terms of the position and momentum operators

# In[31]:


N().rewrite('xp').doit()


# It can also be expressed in terms of the Hamiltonian operator

# In[32]:


N().rewrite('H').doit()


# The Hamiltonian operator can be expressed in terms of the raising and lowering operators, position and momentum operators, and the number operator

# In[33]:


H().rewrite('a').doit()


# In[34]:


H().rewrite('xp').doit()


# In[35]:


H().rewrite('N').doit()


# The raising and lowering operators can also be expressed in terms of the position and momentum operators

# In[36]:


ad().rewrite('xp').doit()


# In[37]:


a().rewrite('xp').doit()


# ### Properties

# Let's take a look at how the NumberOp and Hamiltonian act on states

# In[38]:


qapply(N*k)


# Apply the Number operator to a state returns the state times the ket

# In[39]:


ks = SHOKet(2)
qapply(N*ks)


# In[40]:


qapply(H*k)


# Let's see how the operators commute with each other

# In[41]:


Commutator(N,ad).doit()


# In[42]:


Commutator(N,a).doit()


# In[43]:


Commutator(N,H).doit()


# ### Representation

# We can express the operators in NumberOp basis. There are different ways to create a matrix in Python, we will use 3 different ways.

# #### Sympy

# In[44]:


represent(ad, basis=N, ndim=4, format='sympy')


# #### Numpy

# In[45]:


represent(ad, basis=N, ndim=5, format='numpy')


# #### Scipy.Sparse

# In[46]:


represent(ad, basis=N, ndim=4, format='scipy.sparse', spmatrix='lil')


# In[47]:


print represent(ad, basis=N, ndim=4, format='scipy.sparse', spmatrix='lil')


# The same can be done for the other operators

# In[48]:


represent(a, basis=N, ndim=4, format='sympy')


# In[49]:


represent(N, basis=N, ndim=4, format='sympy')


# In[50]:


represent(H, basis=N, ndim=4, format='sympy')


# #### Ket and Bra Representation

# In[51]:


k0 = SHOKet(0)
k1 = SHOKet(1)
b0 = SHOBra(0)
b1 = SHOBra(1)


# In[52]:


print represent(k0, basis=N, ndim=5, format='sympy')


# In[53]:


print represent(k1, basis=N, ndim=5, format='sympy')


# In[54]:


print represent(b0, basis=N, ndim=5, format='sympy')


# In[55]:


print represent(b1, basis=N, ndim=5, format='sympy')


# In[ ]:




