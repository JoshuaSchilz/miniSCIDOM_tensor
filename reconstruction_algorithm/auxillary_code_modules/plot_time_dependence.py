"""This module has been written for Python 2.7"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.patheffects as path_effects
from matplotlib import gridspec
import matplotlib as mpl



############################ Function for read in dose data ############################
                                                                                       #
def read_data(path):
                                                                                       #
    data = pd.read_csv(path,delimiter=',',header=None,skiprows=1)
                                                                                       #
    return data
                                                                                       #
########################################################################################




##################################### Program ##########################################
                                                                                       #
shot_number=93
                                                                                       #
depth_array = np.array([0.1964,
                        0.5892,
                        0.982,
                        1.3748,
                        1.7676,
                        2.1604,
                        2.5532,
                        2.946,
                        3.3388,
                        3.7316,
                        4.1244,
                        4.5172,
                        4.91,
                        5.3028,
                        5.6956,
                        6.0884,
                        6.4812,
                        6.874,
                        7.2668,
                        7.6596,
                        8.0524,
                        8.4452,
                        8.838,
                        9.2308,
                        9.6236,
                        10.0164,
                        10.802,
                        10.4092])
                                                                                       #
dose_rate=np.zeros((28))
c = np.arange(depth_array[0],depth_array[-1],2*(depth_array[1]-depth_array[0]))
norm = mpl.colors.Normalize(vmin=c.min(), vmax=c.max())
cmap = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.jet)
cmap.set_array([])
                                                                                       #
fig, ax = plt.subplots(figsize=(8, 6))


                                                                                       #
for i in range(len(depth_array)):
        time_dose_path='../pictures/time_dependence_2020-09-25/scinti_shot_{}_25_09_20/time_dose_application_miniSCI_2020_09_25_shot_{}_depth_{}_mm.csv'.format(shot_number,shot_number,str(depth_array[i]))
        data=read_data(time_dose_path)
        time = np.array(data[0])
        dose = np.array(data[1])
        mask = dose/dose.max()<0.996
        ax.plot(time[mask],dose[mask],c=cmap.to_rgba(depth_array[i]))
        index_90 = np.where(dose>=0.9*dose.max())[0][0]
        index_10 = np.where(dose>=0.1*dose.max())[0][0]
        dose_rate[i] = (dose[index_90]-dose[index_10])/(time[index_90]-time[index_10])
                                                                                       #
ax.set_xlabel('Time [ns]',size=22)
ax.set_ylabel('Dose [Gy]',size=22)
ax.yaxis.offsetText.set_fontsize(15)
cb = fig.colorbar(cmap, ticks=c)
cb.ax.tick_params(labelsize=15,size=7,width=2)
ax.tick_params(axis='both',labelsize=22,size=7,width=2)
cb.set_label('Depth [mm]', fontsize=22)
cb.ax.tick_params(labelsize=22)
plt.tight_layout()
plt.show()

fig = plt.figure(figsize=(7, 6))                                                                                       #
plt.plot(depth_array,dose_rate*10**9/10**8)
plt.xlabel('Depth [mm]',size=22)
plt.ylabel(r'Dose rate $\left[10^8 \frac{Gy}{s}\right]$',size=22)
plt.tick_params(axis='both',labelsize=22,size=7,width=2)
plt.tight_layout()
plt.show()
                                                                                       #
current_values=np.zeros((28))
c = np.arange(depth_array[0],depth_array[-1],2*(depth_array[1]-depth_array[0]))
norm = mpl.colors.Normalize(vmin=c.min(), vmax=c.max())
cmap = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.jet)
cmap.set_array([])
                                                                                       #
fig, ax = plt.subplots(figsize=(8, 6))
                                                                                       #
for i in range(len(depth_array)):
        time_dose_path='../pictures/time_dependence_2020-09-25/scinti_shot_{}_25_09_20/time_proton_fluence_application_miniSCI_2020_09_25_shot_{}_depth_{}_mm.csv'.format(shot_number,shot_number,str(depth_array[i]))
        data=read_data(time_dose_path)
        time = np.array(data[0])
        prot_fluence = np.array(data[1])
        mask = prot_fluence/prot_fluence.max()<0.996
        Fax.plot(time[mask],prot_fluence[mask]/10**6,c=cmap.to_rgba(depth_array[i]))
        index_90 = np.where(prot_fluence>=0.9*prot_fluence.max())[0][0]
        index_10 = np.where(prot_fluence>=0.1*prot_fluence.max())[0][0]
        current_values[i] = (prot_fluence[index_90]-prot_fluence[index_10])/(time[index_90]-time[index_10])
                                                                                       #
ax.set_xlabel('Time [ns]',size=22)
ax.set_ylabel(r'Proton fluence $\left[\frac{10^6}{mm^2}\right]$',size=22)
ax.yaxis.offsetText.set_fontsize(15)
cb = fig.colorbar(cmap, ticks=c)
cb.ax.tick_params(labelsize=15,size=7,width=2)
ax.tick_params(axis='both',labelsize=22,size=7,width=2)
cb.set_label('Depth [mm]', fontsize=22)
cb.ax.tick_params(labelsize=22)
plt.tight_layout()
plt.show()
                                                                                       #
elementary_charge = 1.602176634*10**(-19) #in C
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111)
ax2 = ax.twinx()
ax.plot(depth_array,current_values*10**9/10**14)
ax2.plot(depth_array,current_values*10**9*elementary_charge*10**6)
ax2.set_ylabel(r'Current density $\left[\frac{{\mu}A}{mm^2}\right]$',size=22)
ax.set_xlabel('Depth [mm]',size=22)
ax.set_ylabel(r'Proton flux $\left[\frac{10^{14}}{s*mm^2}\right]$',size=22)
ax.tick_params(axis='both',labelsize=22,size=7,width=2)
ax2.tick_params(axis='both',labelsize=22,size=7,width=2)
ax.set_ylim(0)
ax2.set_ylim(0)
plt.tight_layout()
plt.show()
                                                                                       #
########################################################################################
