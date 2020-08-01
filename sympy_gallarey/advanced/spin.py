#!/usr/bin/env python
# coding: utf-8

# # Quantum Angular Momentum Module
# 
# This file will show how to use the various objects and methods in the `sympy.physics.quantum.spin` module, with some examples. Much of the work in this module is based off Varschalovich "Quantum Theory of Angular Momentum".

# In[1]:


from sympy.physics.quantum.spin import Jminus, Jx, Jz, J2, J2Op, JzKet, JzKetCoupled, Rotation, WignerD, couple, uncouple
from sympy.physics.quantum import Dagger, hbar, qapply, represent, TensorProduct
from sympy import factor, pi, S, Sum, symbols


# ## Basic spin states and operators
# 
# We can define simple spin states and operators and manipulate them with standard quantum machinery.

# Define a spin ket:

# In[2]:


jz = JzKet(1,1); jz


# Find the vector representation of the state:

# In[3]:


represent(jz)


# Create and evaluate an innerproduct of a bra and a ket:

# In[4]:


ip = Dagger(jz) * jz; ip


# In[5]:


ip.doit()


# Apply an angular momentum operator to the state:

# In[6]:


Jz * jz


# In[7]:


qapply(Jz * jz)


# In[8]:


Jminus * jz


# In[9]:


qapply(Jminus * jz)


# We can also do this for symbolic angular momentum states:

# In[10]:


j, m = symbols('j m')
jz = JzKet(j, m); jz


# In[11]:


J2 * jz


# In[12]:


qapply(J2 * jz)


# Find the matrix representation of a angular momentum operator:

# In[13]:


represent(Jz, j=1)


# ## Utilizing different bases
# 
# Angular momentum states and operators are able to go between different spin bases

# We can rewrite states as states in another basis:

# In[14]:


jz = JzKet(1, 1)
jz.rewrite("Jx")


# Vector representation can also be done into different bases:

# In[15]:


represent(jz, basis=Jx)


# When applying operators in another spin basis, any conversion necessary to apply the state is done, then the states are given back in the original basis. So in the following example, the state returned by `qapply` are in the $J_z$ basis:

# In[16]:


Jx * jz


# In[17]:


qapply(Jx * jz)


# Rewriting states and applying operators between bases can also be done symbolically. In this case, the result is given in terms of Wigner-D matrix elements (see the next section for more information on the `Rotation` operator).

# In[18]:


jz = JzKet(j, m)
jz.rewrite("Jx")


# ## Rotation Operator
# 
# Arbitrary rotations of spin states, written in terms of Euler angles, can be modeled using the rotation operator. These methods are utilized to go between spin bases, as seen in the section above.

# Define an arbitrary rotation operator. The given angles are Euler angles in the `z-y-z` convention.

# In[19]:


a, b, g = symbols('alpha beta gamma')
Rotation(a, b, g)


# Find the Wigner-D matrix elements of the rotation operator as given by $\langle j, m'|\mathcal{R}(\alpha, \beta, \gamma)|j,m\rangle$:

# In[20]:


mp = symbols('mp')
r = Rotation.D(j, m, mp, a, b, g); r


# Numerical matrix elements can be evaluated using the `.doit()` method:

# In[21]:


r = Rotation.D(1, 1, 0, pi, pi/2, 0); r


# In[22]:


r.doit()


# The Wigner small-d matrix elements give rotations when $\alpha=\gamma=0$. These matrix elements can be found in the same manner as above:

# In[23]:


r = Rotation.d(j, m, mp, b); r


# In[24]:


r = Rotation.d(1, 1, 0, pi/2); r


# In[25]:


r.doit()


# You can also directly create a Wigner-D matrix element:

# In[26]:


WignerD(j, m, mp, a, b, g)


# ## Coupled and Uncoupled States and Operators
# 
# States and operators can also written in terms of coupled or uncoupled angular momentum spaces.

# ### Coupled States and Operators

# Define a simple coupled state of two $j=1$ spin states:

# In[27]:


jzc = JzKetCoupled(1, 0, (1, 1)); jzc


# Note that the Hilbert space of coupled states is the direct sum of the coupled spin spaces. This can be seen in the matrix representation of coupled states:

# In[28]:


jzc.hilbert_space


# In[29]:


represent(jzc)


# We can also couple more than two spaces together. See the `JzKetCoupled` documentation for more complex coupling schemes involving more than 2 spaces.

# In[30]:


jzc = JzKetCoupled(1, 1, (S(1)/2, S(1)/2, 1)); jzc


# The normal operators are assumed to be diagonal in the corresponding coupled basis:

# In[31]:


qapply(Jz * jzc)


# ### Uncoupled States and Operators

# Uncoupled states are defined as tensor products of states:

# In[32]:


jzu = TensorProduct(JzKet(1, 1), JzKet(S(1)/2, -S(1)/2)); jzu


# Vector representation of tensor product states gives the vector in the direct product space:

# In[33]:


represent(jzu)


# Uncoupled operators are also defined as tensor products:

# In[34]:


jzopu = TensorProduct(Jz, 1); jzopu


# In[35]:


qapply(jzopu * jzu)


# Coupled operators which are diagonalized by uncoupled states (e.g. $J_z$ and uncoupled $J_z$ eigenstates) can also be applied:

# In[36]:


qapply(Jz * jzu)


# Rewriting states works as before:

# In[37]:


jzu.rewrite("Jx")


# ### Coulping and Uncoupling States

# The `couple` method will couple an uncoupled state:

# In[38]:


jzu = TensorProduct(JzKet(1, 1), JzKet(S(1)/2, -S(1)/2))
couple(jzu)


# Similarly, the uncouple method will uncouple a coupled state

# In[39]:


jzc = JzKetCoupled(2, 1, (1, S(1)/2, S(1)/2))
uncouple(jzc)


# Uncoupling can also be done with the `.rewrite` method:

# In[40]:


jzc.rewrite("Jz", coupled=False)


# The `uncouple` method can also uncouple normal states if given a set of spin bases to consider:

# In[41]:


jz = JzKet(2, 1)
uncouple(jz, (1, S(1)/2, S(1)/2))


# ## Example: Spin-orbit Coupling
# 
# If we start with a hydrogen atom, i.e. a nucleus of charge $Ze$ orbited by a single electron of charge $e$ with reduced mass $\mu$, ignoring energy from center-of-mass motion, we can write the Hamiltonian in terms of the relative momentum, $p$, and position, $r$, as:
# 
# $$H=\frac{p^2}{2\mu} - \frac{Ze^2}{r}$$
# 
# The resulting eigenfunctions have a separate radial and angular compents, $\psi=R_{n,l}(r)Y_{l,m}(\phi,\theta)$. While the radial component is a complicated function involving Laguere polynomials, the radial part is the familiar spherical harmonics with orbital angular momentum $\vec{L}$, where $l$ and $m$ give the orbital angular momentum quantum numbers. We represent this as a angular momentum state:

# In[42]:


l, ml = symbols('l m_l')
orbit = JzKet(l, ml); orbit


# Now, the spin orbit interaction arises from the electron experiencing a magnetic field as it orbits the electrically charged nucleus. This magnetic field is:
# 
# $$\vec{B} = \frac{1}{c}\frac{Ze\vec{v}\times\vec{r}}{r^3} = \frac{Ze\vec{p}\times\vec{r}}{mcr^3}=\frac{Ze\vec{L}}{mc\hbar r^3}$$
# 
# Then the spin-orbit Hamiltonian can be written, using the electron's magnetic dipole moment $\mu$, as:
# 
# $$H_{SO} = -\vec{\mu}\cdot\vec{B} = -\left(-\frac{g\mu_B \vec{S}}{\hbar}\right)\cdot\left(\frac{Ze\vec{L}}{mc\hbar r^3}\right)$$
# 
# Ignoring the radial term:
# 
# $$\propto \vec{L}\cdot\vec{S} = J^2 - L^2 - S^2$$
# 
# for $\vec{J}$, the coupled angular momentum.
# 
# The electron spin angular momentum is given as $\vec{S}$, where the spin wavefunction is:

# In[43]:


ms = symbols('m_s')
spin = JzKet(S(1)/2, ms); spin


# From this we build our uncoupled state:

# In[44]:


state = TensorProduct(orbit, spin); state


# For clarity we will define $L^2$ and $S^2$ operators. These behave the same as `J2`, they only display differently.

# In[45]:


L2 = J2Op('L')
S2 = J2Op('S')


# We also have the spin-orbit Hamiltonian:

# In[46]:


hso = J2 - TensorProduct(L2, 1) - TensorProduct(1, S2); hso


# Now we apply this to our state:

# In[47]:


apply1 = qapply(hso * state); apply1


# Note this has not applied the coupled $J^2$ operator to the states, so we couple the states and apply again:

# In[48]:


apply2 = qapply(couple(apply1)); apply2


# We now collect the terms of the sum, since they share the same limits, and factor the result:

# In[49]:


subs = []
for sum_term in apply2.atoms(Sum):
    subs.append((sum_term, sum_term.function))
    limits = sum_term.limits
final = Sum(factor(apply2.subs(subs)), limits)
final


# This gives us the modification of the angular part of the spin-orbit Hamiltonian. We see there is now the new $j$ quantum number in the coupled states, which we see from looking at the equation will have values $l\pm \frac{1}{2}$, and $m_j=m_l + m_s$. We still have the $l$ and $s$ quantum numbers.
