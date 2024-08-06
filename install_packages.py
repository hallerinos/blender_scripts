import sys
import subprocess
import os

# this line might be adapted to actual installation folder
python_exe = sys.executable
print(f"executable is {python_exe}")

# install pandas
try:
   from pandas import DataFrame
except:
   # upgrade pip
   subprocess.call([python_exe, "-m", "ensurepip"])
   subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
   # install pandas
   subprocess.call([python_exe, "-m", "pip", "install", "pandas"])

# install matplotlib
try:
   import matplotlib.pyplot as plt
except:
   # upgrade pip
   subprocess.call([python_exe, "-m", "ensurepip"])
   subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
   # install matplotlib
   subprocess.call([python_exe, "-m", "pip", "install", "matplotlib"])

# install fake-bpy
# upgrade pip
subprocess.call([python_exe, "-m", "ensurepip"])
subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
# install fake-bpy
subprocess.call([python_exe, "-m", "pip", "install", "fake-bpy-module-latest"])