# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 13:09:44 2021

@author: venusb
"""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d 
import scipy.optimize as spo



cols = [0,1,2] ## 0 is temperatures 1 is max resistance 2 is min resistance 3 is voutlookuptable
df = pd.read_excel('erroranalysis.xlsx',sheet_name ="BCU_Aux_Copy",usecols=cols, header = 0,index_col=0) #excel data is dict 


#Current lookup table will be used as initial guess for optimization
x0 = [-40, 0, 20, 70, 110, 150, 4.9688630104064941, 4.6877126693725586, 4.2523789405822754, 2.2073507308959961, 0.9325964450836182, 0.3815633654594421 ]

Rup = 2200
Vsupply = 5

tol = 1.01 #1% tolerance on voltage supply rail and pull up resistor

#Determine the min and max expected voltage given tolerances of pull up and supply voltage
minVmeas = Vsupply/tol*(df['NTCminR']/(df['NTCminR']+Rup*tol))
maxVmeas = Vsupply*tol*(df['NTCmaxR']/(df['NTCmaxR']+Rup/tol))

#Create new dataframe of V measurements
Vmeasdf = minVmeas.to_frame()
Vmeasdf = Vmeasdf.join(maxVmeas)
Vmeasdf['Ave'] = Vmeasdf.mean(axis=1)







#only look at temperatures from -20 to 103C

def cost(x0):
    tstart = -20
    tend = 103
    yinit=x0[:int(len(x0)/2)]
    xinit=x0[int(len(x0)/2):] #make the x voltage, so that we are comparing temperatures for error
    
    #narrow down the dataframe being used for temperatures
    dfapp = Vmeasdf['Ave'].loc[tstart:tend]
    dfappmax = Vmeasdf['NTCmaxR'].loc[tstart:tend]
    dfappmin = Vmeasdf['NTCminR'].loc[tstart:tend]
    
    lut = interp1d(xinit, yinit, fill_value = "extrapolate") #input voltage output temperature
    lutxy = interp1d(yinit, xinit, fill_value = "extrapolate") #input voltage output temperature    
    #Resulting temperature using the lookup tables
    Vmeasdf.index
    lookuptable = lutxy(Vmeasdf.index) ## should be -40 to 140
    lutTemp = lut(dfapp)
    lutTempmax = lut(dfappmax)
    lutTempmin = lut(dfappmin)
    
    #measured - actual error for max
    errormax = lutTempmax - dfapp.index
    ## measured - actual error for min
    errormin = lutTempmin - dfapp.index
    #measured - actual error
    error = lutTemp - dfapp.index
    
    #weight the error so that negative errors at hot temperatures, and postive errors at cold temperatures are worse  
    idx = (error<0) & (dfapp.index.values>55)
    hoterror = idx * error * 5
    idx = (error>0) & (dfapp.index.values<0)
    colderror = idx * error * 5
    
    newerror = error + hoterror + colderror
    
    #return a single value for RMS error
    RMS = np.sqrt(np.average(newerror**2))
    
    return RMS


result = spo.minimize(cost,x0, method = 'Nelder-Mead')

#Need to have a function to plot the results
def eval_plot(x0, legendlabel, legendregion):
    
    tstart = -20
    tend = 103
    yinit=x0[:int(len(x0)/2)]
    xinit=x0[int(len(x0)/2):] #make the x voltage, so that we are comparing temperatures for error
    
    #narrow down the dataframe being used for temperatures
    dfapp = Vmeasdf['Ave'].loc[tstart:tend]
    
    lut = interp1d(xinit, yinit, fill_value = "extrapolate") #input voltage output temperature
       
    #Resulting temperature using the lookup tables
    lutTemp = lut(dfapp)
    
    #measured - actual error
    error = lutTemp - dfapp.index   
    
    plt.figure()
    plt.plot(dfapp.index,error, label = legendlabel)
    plt.xlabel('Actual Temperature (C)')
    plt.ylabel('Temperature Error (Measured - Actual)')
    plt.legend(loc=legendregion, ncol=1, shadow=True, fancybox=True)
    
    #return a single value for RMS error
    RMS = np.sqrt(np.average(error**2))
    
    return RMS

eval_plot(x0,'original from AVL','lower right')

eval_plot(result.x,'optimized', 'lower right')