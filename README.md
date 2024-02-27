# Usage:   
- install requirements (`py -m pip install -r requirements.txt`)
- run programm (`py main.py`)

# Simplified usage:   
- download project (download setup.bat and double-click it)
- install requirements (double-tap `install_reqirements.bat`)
- create launcher (double-tap `create_launcher.bat`)
- run programm (double-tap `start.bat` created in the previous step, you can move wherever)

## What do the .bats do?
- `install_reqirements.bat` creates virtual environment (to avoid cluttering your system with random libraries) in the folder it was launched from and installs all dependencies there
- `create_launcher.bat` creates `start.bat` in the folder it was launched from
- `start.bat` activates virtual environment and launches main.py in it
