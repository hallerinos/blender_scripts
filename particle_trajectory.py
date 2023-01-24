import sys
import argparse
import uuid
import pandas as pd

from aux.delete_scene import delete_scene
from aux.parse_args import parse_args
from aux.create_trajectory import create_trajectory
from aux.create_camera import create_camera
from aux.set_scene import set_scene
from aux.load_hdri import load_hdri
from aux.render_scene import render_scene

if __name__ == "__main__":
    args = parse_args()
    trajectory_data = pd.read_csv(args.data_csv)

    delete_scene()
    create_trajectory(trajectory_data)
    set_scene()
    load_hdri('hdri_studio.exr')
    create_camera()
    render_scene(args.output)