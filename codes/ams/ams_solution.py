import numpy as np
import ams_functions as ams

'''

Parameters

'''
age_start = 6
age_max   = 10


'''
Creating the matrices
    - Probability
    - EV matrix (age,edu)
'''

# Probabilities of working
probs_w = np.empty((age_max,age_max)) 
probs_w[:] = np.nan         

# Probabilities of school
probs_s = np.empty((age_max,age_max)) 
probs_s[:] = np.nan   

# Threshold matrix
eps_t = np.empty((age_max,age_max)) 
eps_t[:] = np.nan         

# Expected values matrix for L = 1 
eve_w  = np.empty((age_max,age_max)) 
eve_w[:] = np.nan              

# Expected values matrix for L = 0 
eve_s = np.empty((age_max,age_max)) 
eve_s[:] = np.nan   

# Value function matrix
vf = np.empty((age_max,age_max)) 
vf[:] = np.nan  

#  SOLVING THE MODEL
for age in range(age_max,-1,-1):
    for edu in range(0,age_max):
        if edu >= age:
            pass
        else:       
            # For the threshold we will use the terminal value to capture the value of an specifiy education level in terms of utility  
               
            if age == age_max: #last period situation
                tv_s =  ams.prob_progress(edu)*(ams.terminal_v(edu = edu+1)) + (1 - ams.prob_progress(edu))*(ams.terminal_v(edu = edu)) 
                tv_w =  ams.terminal_v(edu = edu)
                eps_t[age-1,edu] = ams.value_function(age,edu,1, EV = tv_s) - ams.value_function(age,edu,0, EV = tv_w)
                                   
            else:                #Other periods will take the difference between value functions
                tv_s = ams.prob_progress(edu)*(vf[age, edu+1]) + (1 - ams.prob_progress(edu))*(vf[age,edu])
                tv_w = vf[age, edu]
                eps_t[age-1,edu] = ams.value_function(age,edu,1, EV = tv_s) - ams.value_function(age,edu,0, EV = tv_w)
            
            # Now we will calcute the probabilities of schooling and working based on the thresholds                     
            probs_s[age-1,edu] = ams.logistic(eps = eps_t[age-1,edu])
            probs_w[age-1,edu] = 1 - probs_s[age-1,edu]
            
            # Using the thresholds we will calculate the EVs
            if age == age_max:
                u_t = ams.trunc_change(eps = eps_t[age-1,edu])
                eve_s[age-1,edu] = ams.value_function(age,edu,1, EV = tv_s) + ams.trunc_school(ϵ_threshold = eps_t[age-1,edu], u_threshold = u_t)
                eve_w[age-1,edu] = ams.value_function(age,edu,0, EV = tv_w)
            else:
                u_t = ams.trunc_change(eps = eps_t[age-1,edu])
                eve_s[age-1,edu] = ams.value_function(age,edu,1, EV = tv_s) + ams.trunc_school(ϵ_threshold = eps_t[age-1,edu], u_threshold = u_t)
                eve_w[age-1,edu] = ams.value_function(age,edu,0, EV = tv_w)
            
            vf[age-1,edu] = probs_s[age-1,edu]*eve_s[age-1,edu] + probs_w[age-1,edu]*eve_w[age-1,edu]

ams.ams_solution()