'''

Packages

'''
import numpy as np
import pandas as pd
import ams_functions as ams
'''

Using the model solution to get the probability matrices.

'''
probs_w, probs_s, eps_t, eve_w, eve_s, vf = ams.solution()
'''

We need to define how many individuals we are going to simulate and other parameters for our simulation.

'''
np.random.seed(1996)
ϵ_mean  = 0
ϵ_sd    = 1
age_start = 6
age_max   = 10
sim       = 100
β         = 0.9
'''

Creating matrices to store our results and create a dataframe with our individual.

'''
# School decision
S_dec = np.empty((age_max,sim))
S_dec[:] = np.nan   

# Education level (current period)
ed_cur = np.empty((age_max,sim))
ed_cur[:] = np.nan   

# Education level (next period)
ed_next = np.empty((age_max,sim))
ed_next[:] = np.nan   

# Age 
age_c = np.empty((age_max,sim))
age_c[:] = np.nan

# Shock
eps = np.empty((age_max,sim))
eps[:] = np.nan

# Utility 
U = np.empty((age_max,sim))
U[:] = np.nan  

# Comsumption
C = np.empty((age_max,sim))
C[:] = np.nan
'''

Now we will loop our simulated individuals using the probability matrices obtained using the model solution code.

'''


for s in range(sim):
    # All the individuals start with no education
    edu = 0          
    for age in range(age_max):
        # Actual child's age
        age_c[age,s] = age_start + age
        ed_cur[age,s] = edu
        
        # Random shock to education cost
        e_shock = np.random.logistic(loc = ϵ_mean, scale = ϵ_sd)
        
        # Random shock to primary education sucess  
        e_sucess = np.random.uniform()    
        
        if age == age_max - 1:
            s_ev = ams.prob_progress(edu)*ams.terminal_v(edu=edu+1) + (1 - ams.prob_progress(edu))*ams.terminal_v(edu=edu)
            w_ev = ams.terminal_v(edu=edu)
        else:
            s_ev = ams.prob_progress(edu)*vf[age+1, edu+1] + (1 - ams.prob_progress(edu))*vf[age+1,edu] 
            w_ev = vf[age+1, edu]
            
        # Utility for choices                          
        school = ams.utility(age, edu, school=1, ϵ = e_shock) + β*s_ev
        work   = ams.utility(age, edu, school=0, ϵ = e_shock) + β*w_ev
                
        # Decision that max utility for individual
        dec = max(school, work)                                       
        u = dec
        if u == school:
            if e_sucess <= ams.prob_progress(edu):
                suc = 1
            else:
                suc = 0
            ed_next[age,s] = edu + suc
            C[age,s] = ams.budget_constraint(age, edu, school=1)
            U[age,s] = dec
            S_dec[age,s] = 1
        else:
            suc = 0
            ed_next[age,s] = edu + suc
            C[age,s] = ams.budget_constraint(age, edu, school=0)
            U[age,s] = dec
            S_dec[age,s] = 0
        eps[age,s] = e_shock
        edu = edu + suc
        
'''

Now we can use the data created to build our dataframe

'''
simulated_data = []
for i in range(sim):
    s = {}
    s['id'] = i
    s['age']  = list(range(6,16))
    s['edu']  = list(ed_cur[:,i])
    s['edu_next'] = list(ed_next[:,i])
    s['School']  = list(S_dec[:,i])
    s['eps']  = list(eps[:,i])
    s['U']  = list(U[:,i])
    s['C']  = list(C[:,i])
    s = pd.DataFrame(s)
    simulated_data.append(s)
    
simulated_data = pd.concat(simulated_data, axis = 0).reset_index().drop('index', axis = 1)

'''

We also can replicate this using the function from the ams_functions file

'''

sim = ams.simulation()