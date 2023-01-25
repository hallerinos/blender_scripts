import sys
import pandas as pd
import bpy
import os

sys.path.append('.')

from aux.delete_scene import delete_scene
from aux.parse_args import parse_args
from aux.create_trajectory import create_trajectory
from aux.create_camera import create_camera
from aux.set_scene import set_scene
from aux.load_hdri import load_hdri
from aux.render_scene import render_scene

if __name__ == "__main__":
    home = os.getenv('HOME')
    args = parse_args()
    trajectory_data = pd.read_csv(args.data_csv)

    delete_scene()
    traj = create_trajectory(trajectory_data)
    set_scene()
    load_hdri('aux/hdri_studio.exr')
    create_camera()
    render_scene(args.output)
    bpy.ops.wm.save_as_mainfile(filepath=f'{home}/blender_scripts/test.blend')