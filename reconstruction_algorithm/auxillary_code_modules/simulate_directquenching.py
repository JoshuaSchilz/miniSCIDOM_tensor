import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from Birkmodel import letcorrection
from readcsv import read_tof
from readcsv import read_data_mini
from readnpy import read_dose
from readnpy import read_doserr

#################################################
"""TOF SIMULATED DATA """
path1 = "../pictures/2020-09-25/lowdose/ToF_FUKA_sims_dose_quench_miniSCI_25_09_20_shot_93.csv"
path2 = "../pictures/2020-09-25/lowdose/ToF_FUKA_sims_dose_quench_miniSCI_25_09_20_shot_92.csv"
path3 = "../pictures/2020-09-25/lowdose/ToF_FUKA_sims_dose_quench_miniSCI_25_09_20_shot_91.csv"

depth_sim, realdose1, quenchedose1, ys1 = read_data_mini(path1)
depth_sim, realdose2, quenchedose2, ys2 = read_data_mini(path2)
depth_sim, realdose3, quenchedose3, ys3 = read_data_mini(path3)


"TOF PREDICTED  DATA IN SCINTILLATOR and  RCF MEASUREMENTS analitical "
path1 = "../pictures/2020-09-25/lowdose/TOFinscintillator_93_ana.csv"
path2 = "../pictures/2020-09-25/lowdose/TOFinscintillator_92_ana.csv"
path3 = "../pictures/2020-09-25/lowdose/TOFinscintillator_91_ana.csv"

(
    depth_sci1,
    dose_sci1,
    dose_sci_upper1,
    dose_sci_lower1,
    ys_ana_mini1,
    ys_ana_upper_mini1,
    ys_ana_lower_mini1,
) = read_tof(path1)
(
    depth_sci2,
    dose_sci2,
    dose_sci_upper2,
    dose_sci_lower2,
    ys_ana_mini2,
    ys_ana_upper_mini2,
    ys_ana_lower_mini2,
) = read_tof(path2)
(
    depth_sci3,
    dose_sci3,
    dose_sci_upper3,
    dose_sci_lower3,
    ys_ana_mini3,
    ys_ana_upper_mini3,
    ys_ana_lower_mini3,
) = read_tof(path3)

# low dose September
s = 0.0634
directory = "../pictures/2020-09-25/lowdose/notnormalized/"
dose1, depth1, tof1, number1 = read_dose(directory, "notnormalizedmean_array93.npy", s)
err1 = read_doserr(directory, "notnormalizederr93.npy")
area1 = np.trapz(dose1[3 : len(dose1)], depth1[3 : len(depth1)])

dose2, depth2, tof2, number2 = read_dose(directory, "notnormalizedmean_array92.npy", s)
err2 = read_doserr(directory, "notnormalizederr92.npy")
area2 = np.trapz(dose2[3 : len(dose2)], depth2[3 : len(depth2)])


dose3, depth3, tof3, number3 = read_dose(directory, "notnormalizedmean_array91.npy", s)
err3 = read_doserr(directory, "notnormalizederr91.npy")
area3 = np.trapz(dose3[3 : len(dose3)], depth3[3 : len(depth3)])
###############################################################################
"""NORMALIZATION"""
norm1 = 1 / dose1.max()
norm2 = 1 / dose2.max()
norm3 = 1 / dose3.max()


normquen1 = 1 / quenchedose1.max()
normquen2 = 1 / quenchedose2.max()
normquen3 = 1 / quenchedose3.max()
normreal1 = 1 / realdose1.max()

###############################################################################
"""LET CORRECTION"""
D_a_mini1, D_a_up_mini1, D_a_low_mini1, area_corrected1, S_a_mini1 = letcorrection(
    depth_sci1, dose1, ys_ana_mini1, ys_ana_lower_mini1, ys_ana_upper_mini1, s
)
D_a_mini2, D_a_up_mini2, D_a_low_mini2, area_corrected2, S_a_mini2 = letcorrection(
    depth_sci2, dose2, ys_ana_mini2, ys_ana_lower_mini2, ys_ana_upper_mini2, s
)
(
    D_a_mini_quenched,
    D_a_up_mini_quenched,
    D_a_low_mini_quenched,
    area_corrected_quenched,
    S_a_mini_quenched,
) = letcorrection(depth_sim, quenchedose1, ys1, ys1, ys1, s)


##################################################################################



fig, ax = plt.subplots(figsize=[9,7])
ax2 = ax.twinx()

ax2.plot(
    depth_sci1,
    ys_ana_mini1,
    "-",
    drawstyle="steps-mid",
    linewidth=3,
    color=sns.color_palette("Paired")[4],
    #label="$LET_{fluence}$",
        zorder=0,
)

ax.plot(
    np.arange(0, len(dose1), 1) * 0.0634,
    dose1 * norm1,
    ".",
    markersize=12,
    color='cornflowerblue',
    label='MS',
    zorder=2,
)


ax.plot(
    depth_sim,
    quenchedose1 * normquen1,
    "r-",
    drawstyle="steps-mid",
    linewidth=3,
    label="Simulated, quenched",
    zorder=3,
)

ax.plot(
    depth_sci1,
    dose_sci1 / dose_sci1.max(),
    "-",
    drawstyle="steps-mid",
    linewidth=3,
    color="blue",
    label="ToF pred.",
    zorder=2,
)

ax.plot(
    np.arange(0, len(dose1), 1) * s,
    D_a_mini1 / D_a_mini1.max(),
    ".",
    markersize=12,
    color="orange",
    label="MS, LET corr.",
    zorder=2,
)
plt.text(0.1,8,' Bunch 3',fontsize=21, weight='bold')
ax2.set_ylim([0,20])
ax.set_xlabel("Depth [mm]", fontsize=22)
ax.set_ylabel(" Relative Dose", fontsize=22)
ax2.set_ylabel(r" $LET_t$ [keV/$\mu$m]", color=sns.color_palette("Paired")[4], fontsize=22)
ax.legend(title="", fontsize=20, loc=1, markerscale=2).set_zorder(4)
ax.tick_params(axis="x", which="major", labelsize=22)
ax.tick_params(axis="y", which="major", labelsize=22)
ax2.tick_params(axis="y", which="major", colors=sns.color_palette("Paired")[4], labelsize=22)
plt.savefig(f"../plots/2020-09-25/Shot3_direc_quenching_simulation.svg")
#plt.show()
