import numpy as np
import pandas as pd
from numba import njit

@njit
def wage(age = 10, edu = 5, 
        w_ag_j = 27.6, q = -0.983 , a1 = 0.066 , a2 = 0.0166, b_w_ag = 0.883):
    """
    
    This function aims to estimate the wage for the village where the child lives

    Args:
        age (int, optional): Child age  Defaults to 10.
        edu (int, optional): Child education. Defaults to 5.
        w_ag_j (float, optional): Adults wage in the village. Defaults to 27.6.
        q (float, optional): Intercept. Defaults to -0.983.
        a1 (float, optional): Age coefficient. Defaults to 0.066.
        a2 (float, optional): Education coefficient. Defaults to 0.0166.
        b_w_ag (float, optional): Adults wage coefficient. Defaults to 0.0166.

    Returns:
        w (float): This is the log wage base in the village where the child lives
    
    """
    
    w =  (q + a1*age + a2*edu + b_w_ag*np.log(w_ag_j))
    return w
  
@njit
def grant(edu = 5, gender = 'girl'):
    """
    
    This function aims to return the payment received by a child based on the payment schedule 
    defined for PROGRESSA (Table 1)
    
    Args:
        edu (int, optional): Child Education. Defaults to 5.
        gender (str, optional): Child gender. The program has different payment schedules by
                                gender, can be 'girl' or 'boy'. Defaults to 'girl'.

    Returns:
        g (int): The amount payed for the child
        
    """
    
    '''
    Defining the payment structure for boys and girl in 1998 1st semester
    '''
    grant_b = {
        3 : 130,        4 : 150,        5 : 190,    6 : 260,    
        7 : 380,        8 : 400,        9 : 420
    }
    
    grant_f = {  
        3 : 130,        4 : 150,        5 : 190,        6 : 260,
        7 : 400,        8 : 440,        9 : 480
    }
    '''
    Check the gender and define the structure to get the payment (g)
    '''
    if gender == 'girl':
        grant_payment = grant_f
    else:
        grant_payment = grant_b
    try:
        g = grant_payment[edu]
    except:
        g = 0
    return g

@njit
def budget_constraint(age, edu, school = 1, gender = 'girl', group = 'treatment',
           g = 3.334, b_progressa = 0.0605, hr_day = 7.9, days = 5.1, weeks = 1.7, days_weeks = 14):
    """
    
    This function returns the child budget constraint living in a village, conditional on working or 
    going to school

    Args:
        age (int): Child age.
        edu (int): Child education.
        school (int, optional): School or Work. Defaults to 1.
        gender (str, optional): _description_. Defaults to 'girl'.
        group (str, optional): In the treatment or control group. Defaults to 'treatment'.
        g (float, optional): Coefficient in the utility for the grant. Defaults to 3.334.
        b_progressa (float, optional): Progressa dummy coefficient. Defaults to 0.0605
        hr_day (float, optional): Average hours worked per day. Defaults to 7.9.
        days (float, optional): Average days worked. Defaults to 5.1.
        weeks (int, optional): Average weeks worked. Defaults to 2.
        days_weeks (int, optional): Days in the weeks worked. Defaults to 14.

    Returns:
        b (float): The budget constraint of the child in a particular village
    """
    
    if group == 'treatment':
        b = (1-school)*((np.exp(wage(age, edu) + b_progressa)*(hr_day*days*weeks))/(days_weeks)) + school*g*grant(edu,gender)/(days_weeks)
    else:
        b = ((1-school)*np.exp((wage(age, edu)))*(hr_day*days*weeks))/(days_weeks) 
    return b

@njit
def edu_cost(age = 10, edu = 5,  mom_edu = 1, cost_sec = 9.5,
             sec = 0, μ = -8.7060, b_age = 2.291, b_mom = -0.746, b_edu = -0.983, b_sec = 0.007):
    """
    
    This function returns the child cost of going to school     

    Args:
        age (int, optional): Child age. Defaults to 10.
        mom_edu (int, optional): Mother's education. Defaults to 1.
        edu (int, optional):  Child education. Defaults to 5.
        cost_sec (float, optional): Cost. Defaults to 9.5.
        sec (int, optional): If the child is attending secondary school. Defaults to 1.
        μ (float,optional): Shifter coefficient for the child. Defaults to -9.706.
        b_age (float, optional): Age coefficient. Defaults to 2.291.
        b_mom (float,optional): Mother background coefficient. Defaults to -0.746. 
        b_edu (float,optional): Education coefficient. Defaults to -0.983.
        b_sec (float,optional): Secondary education coefficient. Defaults to 0.007.

    Returns:
        cost (float): The cost of going to school for the child
    """
    if edu > 6:
        sec = 1
    cost = μ + b_mom*mom_edu + b_age*age + b_edu*edu + b_sec*cost_sec*sec
    return cost

@njit
def utility(age = 10, edu = 5, school = 1, ϵ = 0, δ = 0.134, μ = -8.706):
    """
    
    This function measures the utility gain for the child based on the choice of schooling or working

    Args:
        school (int, optional): School or Work. Defaults to 1.
        edu (int, optional): Child education. Defaults to 5.
        age (int, optional): Child age. Defaults to 10.
        g (float, optional): Coefficient in the utility for the grant. Defaults to 3.334.
        δ (float, optional): Coefficient in the utility for the grant. Defaults to 0.134.
        μ (float, optional): Coefficient in the utility for the grant. Defaults to -8.706.
        ϵ (float, optional): Shock for school taste
        
    Returns:
        u (float): Utility gain from the decision
    """
    u = ((δ*budget_constraint(age, edu, school)) - edu_cost(age, edu, μ = μ) + ϵ)*school + (δ*budget_constraint(age, edu, school))*(1 - school)
    return u

@njit
def terminal_v(α1 = 356.3809 , α2 = 0.2792, edu = 5):
    """

    This function measures the utility gain of completing a determined x years of education bt age 18

    Args:
        edu (int, optional): Child education. Defaults to 5.
        α1  (int, optional): Parameter 1. Defaults to 5.876
        α2  (int, optional): Parameter 2. Defaults to -1.276
    Returns:
        tv (float) : Terminal value 
    
    """
    
    tv = α1/(1 + np.exp(-α2*edu))
    return tv

@njit
def value_function(age = 10, edu = 5, school = 1, EV = np.nan, b = 0.9):
    """
    
    Value function

    Args:
        age (int, optional): age of child. Defaults to 10.
        edu (int, optional): education of child. Defaults to 5.
        school (int, optional): school choice. Defaults to 1.
        EV (float, optional): ev for next period. Defaults to np.nan.
        b (float, optional): discount. Defaults to 0.9.

    Returns:
        float: valu function value   
    """    
    v = utility(age, edu, school) + b*EV
    return v

@njit
def logistic(eps = 0.0):
    """
    
    Logistic function

    Args:
        eps (float, optional): epsilon value. Defaults to 0.0.

    Returns:
        float: value for cdf until eps
    """
    l = 1/(1+np.exp(-(eps)))
    return l

@njit
def trunc_change(eps = 0.0):
    """
    
    This function transforms the variable to do integration

    Args:
        eps (float, optional): epsilon value. Defaults to 0.

    Returns:
        float: variable transformed
        
    """
    x = (1+np.exp(-eps))**(-1)
    return x


@njit
def trunc_school(ϵ_threshold = 0.0, u_threshold = 5.0):
    """
    
    Truncated value from x threshold to +∞, where the child goes to school

    Args:
        ϵ_threshold (float, optional): 
        u_threshold (float, optional): _description_. Defaults to 5.
    
    Returns:
        float: truncated value calculated
        
    """
    t =  (u_threshold*np.log((1-u_threshold)/u_threshold) - np.log(1-u_threshold))\
        *(np.exp(-ϵ_threshold)/(1+np.exp(-ϵ_threshold)));
    return t

@njit
def prob_progress(edu=0):
    """
    
    Progress of education function

    Args:
        edu (int, optional): education level. Defaults to 0.

    Returns:
        float: probability of progress
    """
    if edu<=6:
        p = 0.9
    else:
        p = 0.75
    return p

@njit
def solution(age_max = 10): 
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
                    tv_s =  prob_progress(edu)*(terminal_v(edu = edu+1)) + (1 - prob_progress(edu))*(terminal_v(edu = edu)) 
                    tv_w =  terminal_v(edu = edu)
                    eps_t[age-1,edu] = value_function(age,edu,1, EV = tv_s) - value_function(age,edu,0, EV = tv_w)
                                    
                else:                #Other periods will take the difference between value functions
                    tv_s = prob_progress(edu)*(vf[age, edu+1]) + (1 - prob_progress(edu))*(vf[age,edu])
                    tv_w = vf[age, edu]
                    eps_t[age-1,edu] = value_function(age,edu,1, EV = tv_s) - value_function(age,edu,0, EV = tv_w)
                
                # Now we will calcute the probabilities of schooling and working based on the thresholds                     
                probs_s[age-1,edu] = logistic(eps = eps_t[age-1,edu])
                probs_w[age-1,edu] = 1 - probs_s[age-1,edu]
                
                # Using the thresholds we will calculate the EVs
                if age == age_max:
                    u_t = trunc_change(eps = eps_t[age-1,edu])
                    eve_s[age-1,edu] = value_function(age,edu,1, EV = tv_s) + trunc_school(ϵ_threshold = eps_t[age-1,edu], u_threshold = u_t)
                    eve_w[age-1,edu] = value_function(age,edu,0, EV = tv_w)
                else:
                    u_t = trunc_change(eps = eps_t[age-1,edu])
                    eve_s[age-1,edu] = value_function(age,edu,1, EV = tv_s) + trunc_school(ϵ_threshold = eps_t[age-1,edu], u_threshold = u_t)
                    eve_w[age-1,edu] = value_function(age,edu,0, EV = tv_w)
                
                vf[age-1,edu] = probs_s[age-1,edu]*eve_s[age-1,edu] + probs_w[age-1,edu]*eve_w[age-1,edu]
    return probs_w, probs_s, eps_t, eve_w, eve_s, vf

def simulation(sim = 100, age_start = 6, age_max = 10, ϵ_mean = 0, ϵ_sd = 1, β = 0.9):
    """
    
    This function simulates individuals using the AMS model solution as base

    Args:
        sim (int, optional): Number of individuals to be simulated. Defaults to 100.
        age_start (int, optional): Starting age. Defaults to 6.
        age_max (int, optional): Max number of years in adding to age_start (in this case 6 + 10 = 15)
                                 15 years old is the last year simulated. Defaults to 10.
        ϵ_mean (float, optional): Shock mean. Defaults to 0.
        ϵ_sd   (float, optional): Shock standart deviation. Defaults to 1.
        β      (float, optional): Discount factor. Defaults to 0.9
    
    Returns:
        DataFrame: Simulated dataframe
    """
    probs_w, probs_s, eps_t, eve_w, eve_s, vf = solution()

    # Creating matrices to store our results and create a dataframe with our individual
    
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
    
    # Now we will loop our simulated individuals using the probability matrices obtained using the model solution code.

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
                s_ev = prob_progress(edu)*terminal_v(edu=edu+1) + (1 - prob_progress(edu))*terminal_v(edu=edu)
                w_ev = terminal_v(edu=edu)
            else:
                s_ev = prob_progress(edu)*vf[age+1, edu+1] + (1 - prob_progress(edu))*vf[age+1,edu] 
                w_ev = vf[age+1, edu]
                
            # Utility for choices                          
            school = utility(age, edu, school=1, ϵ = e_shock) + β*s_ev
            work   = utility(age, edu, school=0, ϵ = e_shock) + β*w_ev
                    
            # Decision that max utility for individual
            dec = max(school, work)                                       
            u = dec
            if u == school:
                if e_sucess <= prob_progress(edu):
                    suc = 1
                else:
                    suc = 0
                ed_next[age,s] = edu + suc
                C[age,s] = budget_constraint(age, edu, school=1)
                U[age,s] = dec
                S_dec[age,s] = 1
            else:
                suc = 0
                ed_next[age,s] = edu + suc
                C[age,s] = budget_constraint(age, edu, school=0)
                U[age,s] = dec
                S_dec[age,s] = 0
            eps[age,s] = e_shock
            edu = edu + suc
        
    # Now we can use the data created to build our dataframe
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
    return simulated_data
