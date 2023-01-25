#!bin/bash
blender=/Applications/Blender.app/Contents/MacOS/Blender

script=install_packages.py

echo "plot..."
$blender --background --python $script -- -data_csv $data
echo "done."