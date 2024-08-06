import matplotlib.pyplot as plt

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Helvetica"
})

def plot_spatial_coords(dataframe):
    plt.plot(dataframe['t'], dataframe['x'])
    plt.plot(dataframe['t'], dataframe['y'])
    plt.plot(dataframe['t'], dataframe['z'])
    plt.xlabel('$r$')
    plt.show()
    plt.close()
    ax = plt.axes(projection='3d')
    ax.plot3D(dataframe['x'], dataframe['y'], dataframe['z'])
    plt.show()