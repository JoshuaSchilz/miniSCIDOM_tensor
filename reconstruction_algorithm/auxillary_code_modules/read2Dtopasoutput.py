""" Read 2D output from TOPAS simulation"""
import numpy as np
from getprofile import Get_profile
import pandas as pd
s = 0.073825  # [mm/pixel ]


def readtopasoutput(
    directory, filename, filenameLETdose, filenameLETfluence, nz, nx, unit
):
    outputfile_topas = directory + filename
    header = pd.read_csv(outputfile_topas, nrows=7)
    df = pd.read_csv(outputfile_topas, comment="#", header=None)
    topas_datamatrix = np.array(df)  # convert dataframe df to array
    doseprofile = Get_profile(topas_datamatrix, nz, nx)
    zdoseprofile = doseprofile.zmeanprofile
    zdoseprofile = zdoseprofile[::-1]
    (_, energy, _, PC, _) = outputfile_topas.split("_")
    (energy, _) = energy.split(unit)
    depth_sci = np.arange(0, len(zdoseprofile), 1) * s
    area_sim = np.trapz(
        zdoseprofile[3 : len(zdoseprofile) - 3], depth_sci[3 : len(depth_sci) - 3]
    )
    norm_sim = 1 / zdoseprofile.max()
    # norm_sim=1/area_sim

    outputfile_topasLET = directory + filenameLETdose
    header = pd.read_csv(outputfile_topasLET, nrows=7)
    df = pd.read_csv(outputfile_topasLET, comment="#", header=None)
    topas_datamatrix = np.array(df)  # convert dataframe df to array
    LET_doseprofile = Get_profile(topas_datamatrix, 149, 1)
    LET_zdoseprofile = LET_doseprofile.zmeanprofile
    LET_zdoseprofile = LET_zdoseprofile[::-1]
    LET_zdoseprofile[0] = LET_zdoseprofile[1]
    area_LET = np.trapz(LET_zdoseprofile, depth_sci)

    outputfile_topasLETfluence = directory + filenameLETfluence
    header = pd.read_csv(outputfile_topasLETfluence, nrows=7)
    df = pd.read_csv(outputfile_topasLETfluence, comment="#", header=None)
    topas_datamatrix = np.array(df)  # convert dataframe df to array
    LET_fluenceprofile = Get_profile(topas_datamatrix, 149, 1)
    LET_zfluenceprofile = LET_fluenceprofile.zmeanprofile
    LET_zfluenceprofile = LET_zfluenceprofile[::-1]
    LET_zfluenceprofile[0] = LET_zfluenceprofile[1]
    area_f_LET = np.trapz(LET_zfluenceprofile, depth_sci)

    return (
        depth_sci,
        zdoseprofile,
        LET_zdoseprofile,
        LET_zfluenceprofile,
        area_LET,
        area_f_LET,
        norm_sim,
        energy,
        PC,
    )
