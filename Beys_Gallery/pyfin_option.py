#!/usr/bin/env python
# coding: utf-8

# In[1]:


#%% NumPyの読み込み
import numpy as np
#   SciPyのstatsモジュールの読み込み
import scipy.stats as st


# In[2]:


#   原資産価格の二項木の生成
def Binomial_Price_Tree(CurrentPrice, Uptick, NumberOfPeriods):
    #     CurrentPrice: 現時点の原資産価格
    #           Uptick: 原資産価格の上昇率（この逆数が下落率）
    #  NumberOfPeriods: 満期までの期間数
    #           Output: 原資産価格の二項木
    Price = np.array([CurrentPrice])
    yield Price
    for i in range(NumberOfPeriods):
        Price = np.hstack((Price * Uptick, Price[-1] / Uptick))
        yield Price


# In[3]:


#   ヨーロピアン・オプション価格の計算
def European_Option_Pricing(Payoff, DiscountFactor, RiskNeutralProb):
    #           Payoff: 利得の二項木
    #   DiscountFactor: 割引係数
    #  RiskNeutralProb: リスク中立確率
    #           Output: オプション価格の二項木
    Premium = Payoff[-1]
    yield Premium
    for i in range(len(Payoff) - 1):
        Premium = (RiskNeutralProb * Premium[:-1] +
                   (1.0 - RiskNeutralProb) * Premium[1:]) * DiscountFactor
        yield Premium


# In[4]:


#   アメリカン・オプション価格の計算
def American_Option_Pricing(Payoff, DiscountFactor, RiskNeutralProb):
    #           Payoff: 利得の二項木
    #   DiscountFactor: 割引係数
    #  RiskNeutralProb: リスク中立確率
    #           Output: オプション価格の二項木
    Premium = Payoff[-1]
    yield Premium
    for i in range(2, len(Payoff) + 1):
        Premium = np.maximum(Payoff[-i],
                             (RiskNeutralProb * Premium[:-1]
                              + (1.0 - RiskNeutralProb) * Premium[1:])
                             * DiscountFactor)
        yield Premium


# In[5]:


#%% オプション価格の計算
S = 100.0
K = 100.0
u = 1.05
d = 1.0/u
f = 1.02
N = 3
q = (f - d) / (u - d)
Price = [S for S in Binomial_Price_Tree(S, u, N)]
Payoff_Call = [np.maximum(S - K, 0.0) for S in Price]
European_Call = [C for C in European_Option_Pricing(Payoff_Call, 1.0/f, q)]
Payoff_Put = [np.maximum(K - S, 0.0) for S in Price]
European_Put = [P for P in European_Option_Pricing(Payoff_Put, 1.0/f, q)]
American_Put = [P for P in American_Option_Pricing(Payoff_Put, 1.0/f, q)]


# In[6]:


Price


# In[7]:


Payoff_Call


# In[8]:


European_Call


# In[9]:


Payoff_Put


# In[10]:


European_Put


# In[11]:


American_Put


# In[12]:


#%% Black-Scholeの公式によるヨーロピアン・コールオプション価格の計算
S = 100.0
K = 100.0
r = 0.05
v = 0.15
T = 0.50
d1 = (np.log(S / K) + (r + 0.5 * v ** 2) * T) / (v * np.sqrt(T))
d2 = d1 - v * np.sqrt(T)
BS_Formula = S * st.norm.cdf(d1) - K * np.exp(-r * T) * st.norm.cdf(d2)


# In[13]:


print(BS_Formula)


# In[14]:


#%% 二項木によるヨーロピアン・コールオプション価格の計算
S = 100.0
K = 100.0
r = 0.05
v = 0.15
T = 0.50
N = 10000
u = np.exp(v*np.sqrt(T/N))
d = 1.0/u
f = np.exp(r*T/N)
q = (f - d) / (u - d)
Price = [S for S in Binomial_Price_Tree(S, u, N)]
Payoff_Call = [np.maximum(S - K, 0.0) for S in Price]
European_Call = [C for C in European_Option_Pricing(Payoff_Call, 1.0/f, q)][-1].item(0)


# In[15]:


print(European_Call)

