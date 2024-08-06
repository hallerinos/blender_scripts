#!bin/bash
blender=/Applications/Blender.app/Contents/MacOS/Blender

script=particle_trajectory.py
data=data/trajectories/lensing_example.csv

echo "plot..."
$blender --background --python $script -- -data_csv $data
echo "done."