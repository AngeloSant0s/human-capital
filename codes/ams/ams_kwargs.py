import numpy as np
import pandas as pd
from numba import njit
import seaborn as sns
from matplotlib import pyplot as plt


def wage(age = 10, edu = 5, w_ag_j = 27.6, q = -0.983 , a1 = 0.066 , a2 = 0.0166, b_w_ag = 0.883):
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

def budget_constraint(school = 1, group = 'treatment', g = 3.334, b_progressa = 0.0605, hr_day = 7.9, days = 5.1, weeks = 1.7, days_weeks = 14, **kwargs):
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
        b = (1-school)*((np.exp(wage(**kwargs) + b_progressa)*(hr_day*days*weeks))/(days_weeks)) + school*g*grant(kwargs.edu, kwargs.gender)/(days_weeks)
    else:
        b = ((1-school)*np.exp((wage(**kwargs)))*(hr_day*days*weeks))/(days_weeks) 
    return b

@njit
def edu_cost(age = 10, edu = 5,  mom_edu = 1, cost_sec = 9.5, sec = 0, μ = -8.7060, b_age = 2.291, b_mom = -0.746, b_edu = -0.983, b_sec = 0.007):
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
def utility(age = 10, edu = 5, school = 1, g = 3.334, b_mom = -0.746, ϵ = 0, δ = 0.134, μ = -8.706):
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
    u = ((δ*budget_constraint(age, edu, school, g=g)) - edu_cost(age, edu, μ = μ, b_mom = b_mom) + ϵ)*school + \
        (δ*budget_constraint(age, edu, school, g=g))*(1 - school)
    return u