import numpy as np
import numpy_financial as npf
import pandas as pd
import time
import datetime
from dateutil.relativedelta import relativedelta
from pandas_profiling import ProfileReport
import dataset_generator

#Pull Current Date
current_date = datetime.datetime.today()

#Arbitrary principal assigned for amortization schedule loops
principal = 51420

#Deice whether to add a straighlight adjustment factor, the richard roll multiplier, or none
adjustment_input = input('Do you want to include an adjustment factor for seasonality (e.g.,"No","Richard", or "Straight")')


while True:
    if adjustment_input == 'Richard':
        adjustment_factor = {'January':.94,
                             'February':.76
                             ,'March': .74
                             ,'April':.95
                             ,'May':.98
                             ,'June':.92
                             ,'July':.98
                             ,'August':1.1
                             ,'September':1.18
                             ,'October':1.22
                             ,'November':1.23
                             ,'December':.98}
        print(f'Adjustment factor assigned to Richard Roll assumptions: {adjustment_factor}')
        break
    if adjustment_input =='Straight':
        
        straight_input = input('Pick a straight factor for all months:')

        while True:
            try:
                straight_input = float(straight_input)
            except:
                straight_input = input('Previous input not a float, pick another value that is an integer')
  
            else:
                print(f'Breaking loop with adjustment factor, {straight_input}')
                adjustment_factor = {'January':straight_input,
                             'February':straight_input
                             ,'March': straight_input
                             ,'April':straight_input
                             ,'May':straight_input
                             ,'June':straight_input
                             ,'July':straight_input
                             ,'August':straight_input
                             ,'September':straight_input
                             ,'October':straight_input
                             ,'November':straight_input
                             ,'December':straight_input}
                break
        break
    else:
        adjustment_factor = 1
        print(f'No adjustment picked, default of {adjustment_factor} assigned')
        break


#User assigned variables
security_list = ['Agency MBS',
                 'Treasuries',
                 'Corporate Bonds',
                 'HY Bonds']
yield_list = [.05,.0525,.0550,.0575,.06,.0625,.0650,.0675,.07]
speed_list = [.005,.0075,.01,.0125,.015,.0175,
              .02,.0225,.025,.0275,.03,.0325,.035]
term_list = [18,24,36,48,60,72,84,
             120,180,240,360]

#Import dataset_generator module to build dataframe to loop through WAL model
df = dataset_generator.DataFrame_Looper(security_list
                                        ,yield_list
                                        ,speed_list
                                        ,term_list)

#Define function for Calculating WAL
def calculate_WAL(principal, rate, n,SMM, adjustment_input,abs_rate):
    """
    principal: initial loan balance
    rate: annual interest rate
    n: total number of periods (months)
    SMM: single monthly mortality (prepayment rate)
    abs_rate: not turned on yet, just input 0 for now, curves look weird from 33-36 months+
    adjustment_input: variable to adjust based on seasonality and other factors
    """

    #Calculate monthly rate
    monthly_rate = rate/12

    #initialize arrays
    monthly_payment = npf.pmt(monthly_rate, n, -principal)
    interest = np.zeros(n)
    principal_remaining = np.zeros(n)
    principal_payment = np.zeros(n)
    WAL_weights = np.zeros(n)

    principal_remaining[0] = principal

    #iterate over each period
    for i in range(1,n):

        #calculate interset and pricnipal payment
        interest[i] = principal_remaining[i-1] * monthly_rate
        principal_payment[i] = monthly_payment - interest[i]

        #calculating adjustment factor
        if adjustment_input == 'Richard':
            adjustment_value = adjustment_factor[(current_date + relativedelta(months=i - 1)).strftime('%B')]
        elif adjustment_input == 'Straight':
            adjustment_value = adjustment_factor[(current_date + relativedelta(months=i - 1)).strftime('%B')]
        else:
            adjustment_value = adjustment_factor

        if abs_rate > 0:
            SMM = (abs_rate/1(1-(abs_rate)*(i-1)))

        else:
            SMM = SMM * adjustment_value

        #calculate prepayment, assuming we can't prepay on first month, starts on month 2
        if i>1:
            prepayment = SMM * (principal_remaining[i-1] - principal_payment[i])

        else:
            prepayment = 0

        #Calculate remaining pricnipal
        principal_remaining[i] = principal_remaining[i-1] - principal_payment[i] - prepayment

        #if enduing balance falls below payment, adjust final figures
        if principal_remaining[i] < principal_payment[i]:
            principal_payment[i] = principal_remaining[i]/(1+monthly_rate)
            interest[i] = principal_remaining[i] - principal_payment[i]

            if principal_remaining[i] >0:
                WAL_weights[i] = i * principal_payment[i]
            else:
                WAL_weights[i]=0

            principal_remaining[i] = 0
        
        else:
            #calculate weights
            WAL_weights[i] = (i * (principal_payment[i]+prepayment))

    #calculate WAL
    WAL = np.sum(WAL_weights)/principal

    return WAL
print(df)

def WAL_Consolidator(df):
    """The purpose of this function is to calculate the WAL across every
    row of the dataframe based on the the attributes"""

    #assigning constants
    counter = 0
    abs_value = 0

    #assigning arrays for faster computation
    term_array = df['Term'].to_numpy()
    rate_array = df['Yield'].to_numpy()
    security_array = df['Security'].to_numpy()
    speed_array = df['Speed'].to_numpy()
    wal_array = np.zeros(df.shape[0])

    for i in range(0,df.shape[0]):

        wal_array[i] = (calculate_WAL(principal,rate_array[i],term_array[i],speed_array[i],adjustment_input,abs_value))
        counter += 1

    