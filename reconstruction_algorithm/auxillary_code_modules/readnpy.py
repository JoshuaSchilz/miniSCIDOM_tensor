""" Read  python output"""
import numpy as np



def read_dose(directory, filename, m):
    # data = pd.read_excel (path)
    """read reconstruction  data from npy document"""
    data = np.load(directory + filename)
    dose = data[0 : len(data)]  # this is usually the dose
    depth = np.arange(0, len(dose), 1) * m  # m = [mm/pixe]it depends on the camera
    tof = data[len(data) : len(data)]
    (_, shotname) = filename.split("_")
    (shotname, _) = shotname.split(".npy")
    (_, shotnumber) = shotname.split("array")
    return dose, depth, tof, shotnumber


def read_doserr(directory, filename):
    # data = pd.read_excel (path)
    """read reconstruction  data from npy document"""
    data = np.load(directory + filename)
    err = data[0 : len(data)]  # this is usually the dose

    return err
