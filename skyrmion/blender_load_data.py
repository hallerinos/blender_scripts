import numpy as np
import mathutils as mu

def str2cplx(string):
    if "im" not in string:
        num = float(string)
    else:
        num = complex(string.replace("im","j").replace(" ", ""))
    return num

# import the local magnetization profile
fn = "/Users/andreashaller/ITensors_applications/observables/saves/largeJ/Lx20Ly20B0-0.25K0.0J-2graphtriangular_diskmps_obs.txt"
header = np.loadtxt(fn, skiprows=1, delimiter=', ', max_rows=1, dtype=str)
data = np.loadtxt(fn, skiprows=2, delimiter=', ', dtype=str)
data = np.asarray([[str2cplx(e) for e in elem] for elem in data])
data_loc = data[data[:,0] == data[:,1], :]
nsites = len(data_loc)
x = data_loc[:,2]  # separate location array
y = data_loc[:,3]  # separate location array
z = data_loc[:,4]  # separate location array
Sx = np.real(data_loc[:,9])  # separate expectation values
Sy = np.real(data_loc[:,10])  # separate expectation values
Sz = np.real(data_loc[:,11])  # separate expectation values
locations = np.asarray([x,y,z]).T  # construct locations array
locations = np.reshape(locations, (nsites, 3))  # construct location array
rotations = np.asarray([Sx,Sy,Sz]).T  # construct rotation array
rotations = [mu.Vector(elem).to_track_quat('Z','X') for elem in rotations]
#rotations = np.reshape(rotations, (nsites, 4))
colblend = (Sz-np.min(Sz))/np.ptp(Sz)