




import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d 



def initialplotfunction(x0,label1,label2):

    cols = [0,1,2] ## 0 is temperatures 1 is max resistance 2 is min resistance 3 is voutlookuptable
    df = pd.read_excel('erroranalysis.xlsx',sheet_name ="BCU_Aux_Copy",usecols=cols, header = 0,index_col=0) #excel data is dict 
    
    #Current lookup table will be used as initial guess for optimization
    ##x0 = [-40, 0, 20, 70, 110, 150, 4.9688630104064941, 4.6877126693725586, 4.2523789405822754, 2.2073507308959961, 0.9325964450836182, 0.3815633654594421 ]
    
    Rup = 2200
    ##Rup = 2200
    Vsupply = 5
    
    tol = 1.01 #1% tolerance on voltage supply rail and pull up resistor
    
    #Determine the min and max expected voltage given tolerances of pull up and supply voltage
    maxVmeas = (Vsupply*tol)*(df['NTCmaxR']/(df['NTCmaxR']+Rup/tol)) ## correct
    minVmeas = (Vsupply/tol)*(df['NTCminR']/(df['NTCminR']+Rup*tol)) ## correct 
    
    
    #Create new dataframe of V measurements including minimum voltage, maximum and average. 
    Vmeasdf = minVmeas.to_frame()
    Vmeasdf = Vmeasdf.join(maxVmeas)
    Vmeasdf['Ave'] = Vmeasdf.mean(axis=1)
    
    tstart = -30
    tend = 105
    yinit=x0[:int(len(x0)/2)]
    xinit=x0[int(len(x0)/2):] #make the x voltage, so that we are comparing temperatures for error
    
    #narrow down the dataframe being used for temperatures
    dfapp = Vmeasdf['Ave'].loc[tstart:tend]
    dfappmax = Vmeasdf['NTCmaxR'].loc[tstart:tend]
    dfappmin = Vmeasdf['NTCminR'].loc[tstart:tend]
    
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
