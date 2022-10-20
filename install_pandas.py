import sys
import subprocess
import os

try:
   from pandas import DataFrame
except:
   python_exe = os.path.join(sys.prefix, 'bin/python3.10')
   # upgrade pip
   subprocess.call([python_exe, "-m", "ensurepip"])
   subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
   # install pandas
   subprocess.call([python_exe, "-m", "pip", "install", "pandas"])