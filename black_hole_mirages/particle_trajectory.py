import sys
import pandas as pd
import bpy
import os
import numpy as np

sys.path.append('.')

from aux.delete_scene import delete_scene
from aux.set_scene import set_scene
from aux.load_hdri import load_hdri
from aux.render import *

from trajectory_aux.parse_args import parse_args
from trajectory_aux.create_trajectory import create_trajectory
from trajectory_aux.create_camera import create_camera
from trajectory_aux.create_particlesystem import create_particlesystem
from trajectory_aux.add_particle_object import add_particle_object
from trajectory_aux.create_horizon import create_horizon
from trajectory_aux.create_separatrix import create_separatrix

import matplotlib.pyplot as plt

if __name__ == "__main__":
    home = os.getenv('HOME')
    args = parse_args()
    trajectory_data = pd.read_csv(args.data_csv)

    # t = np.linspace(0,2*np.pi,101)
    # x = 3/2*np.cos(t)
    # y = 3/2*np.sin(t)

    # plt.plot(trajectory_data['x'], trajectory_data['y'])
    # plt.plot(x, y)
    # plt.show()

    # exit()
    delete_scene()
    set_scene(fend=500)
    load_hdri(f'{home}/blender_scripts/aux/hdri_studio.exr')
    create_camera()

    traj = create_trajectory(trajectory_data)

    horizon = create_horizon(rt=np.unique(trajectory_data["\\rho_t"])[0])
    separatrix = create_separatrix(rs=1.5*np.unique(trajectory_data["\\rho_t"])[0])

    particle = add_particle_object(pos=(100,0,0))
    particle_system = create_particlesystem(pos=trajectory_data[['x','y','z']].iloc[0], obj=particle)
    
    # bake physics
    bpy.ops.ptcache.bake_all()

    # render_frame(args.output, frame=80)
    render_animation('video/')
    bpy.ops.wm.save_as_mainfile(filepath=f'{home}/blender_scripts/test.blend')