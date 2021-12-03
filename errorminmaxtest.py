import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d 

## this has header files
cols = [0,1,2] ## 0 is temperatures 1 is max resistance 2 is min resistance 3 is voutlookuptable
df = pd.read_excel('erroranalysis.xlsx',sheet_name ="BCU_Aux_Copy",usecols=cols, header = 0,index_col=0) #excel data is dict 

def maxmindiff(Rup, Vsupply, tol, tstart, tend):    
    global object
    #Determine the min and max expected voltage given tolerances of pull up and supply voltage
    minVmeas = Vsupply/tol*(df['NTCminR']/(df['NTCminR']+Rup*tol))
    maxVmeas = Vsupply*tol*(df['NTCmaxR']/(df['NTCmaxR']+Rup/tol))
    #Create new dataframe of V measurements
    Vmeasdf = minVmeas.to_frame()
    Vmeasdf['Ave'] = Vmeasdf.mean(axis=1)
    
    #Create new dataframe of V measurements including minimum voltage, maximum and average. 
    Vmeasdf = minVmeas.to_frame()
    Vmeasdf = Vmeasdf.join(maxVmeas)
    Vmeasdf['Ave'] = Vmeasdf.mean(axis=1)
    
    #narrow down the dataframe being used for temperatures
    dfappmax = Vmeasdf['NTCmaxR'].loc[tstart:tend]
    dfappmin = Vmeasdf['NTCminR'].loc[tstart:tend]
    
    lut2 = interp1d(dfappmax, dfappmax.index , fill_value = "extrapolate") #input voltage output temperature
    test = dfappmax - (dfappmax - dfappmin)
    lutTemptest = lut2(test)
    
    object = plt.figure('Difference between VoutMax and Voutmin in Degrees C')
    plt.plot(dfappmax.index,dfappmax.index-lutTemptest, label = Rup)
    plt.legend(loc='lower right', ncol=1, shadow=True, fancybox=True)
    plt.title('Series Resistor Value')
    plt.xlabel('Actual Temperature (C)')
    plt.ylabel('Temperature Error (VoutMin vs VoutMax)')


maxmindiff(2200, 5, 1.01, -20, 103) ## first --> resistance, second --> voltage, third --> tolerance
maxmindiff(4000, 5, 1.01, -20, 103)
maxmindiff(6000, 5, 1.01, -20, 103)
maxmindiff(8000, 5, 1.01, -20, 103)
maxmindiff(10000, 5, 1.01, -20, 103)
maxmindiff(12000, 5, 1.01, -20, 103)

