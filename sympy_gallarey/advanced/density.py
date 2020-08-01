#!/usr/bin/env python
# coding: utf-8

# # Density operator and matrix 

# In[59]:


from sympy import *
from sympy.physics.quantum import *
from sympy.physics.quantum.density import *
from sympy.physics.quantum.spin import (
    Jx, Jy, Jz, Jplus, Jminus, J2,
    JxBra, JyBra, JzBra,
    JxKet, JyKet, JzKet,
)
from IPython.core.display import display_pretty


# In[60]:


get_ipython().run_line_magic('load_ext', 'sympyprinting')


# Create n density matrix using symbolic states

# In[61]:


psi = Ket('psi')
phi = Ket('phi')


# In[62]:


d = Density((psi,0.5),(phi,0.5)); d


# In[63]:


display_pretty(d)


# In[64]:


d.states()


# In[65]:


d.probs()


# In[66]:


d.doit()


# In[67]:


Dagger(d)


# In[68]:


A = Operator('A')


# In[69]:


d.apply_op(A)


# Now create a density matrix using spin states

# In[70]:


up = JzKet(S(1)/2,S(1)/2)
down = JzKet(S(1)/2,-S(1)/2)


# In[71]:


d2 = Density((up,0.5),(down,0.5)); d2


# In[72]:


represent(d2)


# In[73]:


d2.apply_op(Jz)


# In[74]:


qapply(_)


# In[75]:


qapply((Jy*d2).doit())


# ## Evaluate entropy of the density matrices

# In[76]:


entropy(d2)


# In[77]:


entropy(represent(d2))


# In[78]:


entropy(represent(d2,format="numpy"))


# In[79]:


entropy(represent(d2,format="scipy.sparse"))


# ## Density operators with Tensor Products as args

# In[80]:


from sympy.core.trace import Tr

A, B, C, D = symbols('A B C D',commutative=False)

t1 = TensorProduct(A,B,C)

d = Density([t1, 1.0])
d.doit()

t2 = TensorProduct(A,B)
t3 = TensorProduct(C,D)

d = Density([t2, 0.5], [t3, 0.5])
d.doit() 


# In[81]:


#mixed states
d = Density([t2+t3, 1.0])
d.doit() 


# ## Trace operators on Density Operators with Spin States

# In[82]:


from sympy.physics.quantum.density import Density
from sympy.physics.quantum.spin import (
    Jx, Jy, Jz, Jplus, Jminus, J2,
    JxBra, JyBra, JzBra,
    JxKet, JyKet, JzKet,
)
from sympy.core.trace import Tr

d = Density([JzKet(1,1),0.5],[JzKet(1,-1),0.5]);
t = Tr(d); 

display_pretty(t)
print t.doit()


# ## Partial Trace on Density Operators with Mixed State

# In[83]:


#Partial trace on mixed state
from sympy.core.trace import Tr

A, B, C, D = symbols('A B C D',commutative=False)

t1 = TensorProduct(A,B,C)

d = Density([t1, 1.0])
d.doit()

t2 = TensorProduct(A,B)
t3 = TensorProduct(C,D)

d = Density([t2, 0.5], [t3, 0.5])


tr = Tr(d,[1])
tr.doit()


# ## Partial Trace on Density Operators with Spin states

# In[84]:


from sympy.physics.quantum.density import Density
from sympy.physics.quantum.spin import (
    Jx, Jy, Jz, Jplus, Jminus, J2,
    JxBra, JyBra, JzBra,
    JxKet, JyKet, JzKet,
)
from sympy.core.trace import Tr

tp1 = TensorProduct(JzKet(1,1), JzKet(1,-1))

#trace out 0 index
d = Density([tp1,1]);
t = Tr(d,[0]); 

display_pretty(t)
display_pretty(t.doit())

#trace out 1 index
t = Tr(d,[1])
display_pretty(t)
t.doit()


# ## Examples of qapply() on Density matrices with spin states

# In[85]:


psi = Ket('psi')
phi = Ket('phi')

u = UnitaryOperator()
d = Density((psi,0.5),(phi,0.5)); d

display_pretty(qapply(u*d))
 
# another example
up = JzKet(S(1)/2, S(1)/2)
down = JzKet(S(1)/2, -S(1)/2)
d = Density((up,0.5),(down,0.5))

uMat = Matrix([[0,1],[1,0]])
display_pretty(qapply(uMat*d))



# ## Example of qapply() on Density Matrices with qubits

# In[90]:


from sympy.physics.quantum.gate import UGate
from sympy.physics.quantum.qubit import Qubit

uMat = UGate((0,), Matrix([[0,1],[1,0]]))
d = Density([Qubit('0'),0.5],[Qubit('1'), 0.5])

display_pretty(d)

#after applying Not gate
display_pretty(qapply(uMat*d) )


# In[86]:




