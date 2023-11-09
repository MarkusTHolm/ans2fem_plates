# PROTOTYPE: ans2fem_plates

## Description 

This folder contains a PROTOTYPE version of ans2fem in Python (so it should be easy to modify). Note, the script is only tested for ANSYS 2022R2 in the gBar (using thinlinc).

The folder also contains two .cdb so you can test the script (e.g. by running the resulting .fem file in ANSYS and verify that it works).

## Modifying the script
If you make modifications to the file you need to rebuild the executatable (or run it directly as a python script):

To rebuild the executable follow these steps ($ means run in terminal/command window):
1. Install pyinstaller: \
    $ python -m pip install pyinstaller
2. Go to the path containing the python script \
    $ cd ./INSERT_YOUR_PATH_HERE/
3. Build the executable \
    $ python -m PyInstaller --onefile .\ans2fem_plates.py


One obvious drawback is that the code only supports one material and there are other hardcoded parameters. So, the intention is that YOU add the missing features. Note, the .cdb files are essentially plain .txt files so they are fairly easy to read and decipher.


