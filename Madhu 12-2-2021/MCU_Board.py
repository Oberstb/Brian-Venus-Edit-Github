import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d 
import scipy.optimize as spo



## this has header files
cols = [0,1,2] ## 0 is temperatures 1 is max resistance 2 is min resistance 3 is voutlookuptable
df = pd.read_excel('erroranalysis.xlsx',sheet_name ="MCU_Aux_Copy",usecols=cols, header = 0,index_col=0) #excel data is dict 


#Current lookup table will be used as initial guess for optimization
x0 = [-40, -20, 0, 50, 80, 140, 2.8500225543975830, 2.6158967018127441, 2.1962707042694092,  0.8811613917350769,  0.3371914327144623, 0.1101996451616287]


global Rup, Vsupply, tol
Rup = 10000
Vsupply = 3

tol = 1.01 #1% tolerance on voltage supply rail and pull up resistor

#Determine the min and max expected voltage given tolerances of pull up and supply voltage
minVmeas = Vsupply/tol*(df['NTCminR']/(df['NTCminR']+Rup*tol))
maxVmeas = Vsupply*tol*(df['NTCmaxR']/(df['NTCmaxR']+Rup/tol))

#Create new dataframe of V measurements
Vmeasdf = minVmeas.to_frame()
Vmeasdf = Vmeasdf.join(maxVmeas)
Vmeasdf['Ave'] = Vmeasdf.mean(axis=1)

tstart = -20
tend =103





#only look at temperatures from -20 to 103C

def cost(x0):

    yinit=x0[:int(len(x0)/2)]
    xinit=x0[int(len(x0)/2):] #make the x voltage, so that we are comparing temperatures for error
    
    #narrow down the dataframe being used for temperatures
    dfapp = Vmeasdf['Ave'].loc[tstart:tend]
    
    lut = interp1d(xinit, yinit, fill_value = "extrapolate") #input voltage output temperature  
    #Resulting temperature using the lookup tables
    Vmeasdf.index

    lutTemp = lut(dfapp)
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


def plotfunction(x0,label1,label2):

    
    
    #Determine the min and max expected voltage given tolerances of pull up and supply voltage
    maxVmeas = (Vsupply*tol)*(df['NTCmaxR']/(df['NTCmaxR']+Rup/tol)) ## correct
    minVmeas = (Vsupply/tol)*(df['NTCminR']/(df['NTCminR']+Rup*tol)) ## correct 
    
    
    #Create new dataframe of V measurements including minimum voltage, maximum and average. 
    Vmeasdf = minVmeas.to_frame()
    Vmeasdf = Vmeasdf.join(maxVmeas)
    Vmeasdf['Ave'] = Vmeasdf.mean(axis=1)
    
    yinit=x0[:int(len(x0)/2)]
    xinit=x0[int(len(x0)/2):] #make the x voltage, so that we are comparing temperatures for error
    
    #narrow down the dataframe being used for temperatures
    dfapp = Vmeasdf['Ave'].loc[tstart:tend]
    dfappmax = Vmeasdf['NTCmaxR'].loc[tstart:tend]
    dfappmin = Vmeasdf['NTCminR'].loc[tstart:tend]
    
    ##extrapolate lookup table as function of x,y and y,x
    lut = interp1d(xinit, yinit, fill_value = "extrapolate") #input voltage output temperature
    lutxy = interp1d(yinit, xinit, fill_value = "extrapolate") #input voltage output temperature
    
    Vmeasdf.index
    lookuptable = lutxy(Vmeasdf.index) ## should be -40 to 140
    
    
    #Resulting temperature using the lookup tables
    lutTemp = lut(dfapp)
    lutTempmax = lut(dfappmax)
    lutTempmin = lut(dfappmin)
    #measured - actual error for max
    errormax = lutTempmax - dfapp.index
    ## measured - actual error for min
    errormin = lutTempmin - dfapp.index
    #measured - actual error
    error = lutTemp - dfapp.index
    
    
    
    plt.figure(label1)
    plt.plot(Vmeasdf.index, Vmeasdf.loc[:,"NTCmaxR"], label = 'NTCmaxR')
    plt.plot(dfapp.index,dfapp, label = 'average')
    plt.plot(Vmeasdf.index, Vmeasdf.loc[:,"NTCminR"], label = 'NTCminR')
    plt.plot(Vmeasdf.index, lookuptable, label = 'extrapolated lookup table')
    plt.xlabel('Actual Temperature (C)')
    plt.ylabel('Temperature Error (Measured - Actual)')
    plt.legend(loc='upper right', ncol=1, shadow=True, fancybox=True)
    
    
    plt.figure(label2)
    plt.plot(dfapp.index,errormin, label = 'lookup table error vs error min')
    plt.plot(dfapp.index,error, label = 'lookup table error vs error ave')
    plt.plot(dfapp.index,errormax, label = 'lookup table error vs error max')
    plt.xlabel('Actual Temperature (C)')
    plt.ylabel('Temperature Error (lookuptable - Actual)')
    plt.legend(loc='lower right', ncol=1, shadow=True, fancybox=True)


result = spo.minimize(cost,x0, method = 'Nelder-Mead')

plotfunction(x0, 'initial lookup table', 'Original')

plotfunction(result.x,'optimized lookup table','Optimized')




