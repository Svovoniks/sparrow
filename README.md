# Usage:   
- install requirements (`py -m pip install -r requirements.txt`)
- run programm (`py main.py`)

# Simplified usage:   
- download `setup.bat` (you can do it from releases) and double-click it
- go to the folder `sparrow` (it was created on the last step) there you will find `update.bat` and `start.bat` (move them wherever, rename if you want)
- to start the programm double-click `start.bat`, to update - `update.bat`

## What do the .bats do?
- `setup.bat` downloads project (action also known as `git clone`) and calls `install_reqirements.bat` and `create_launcher.bat`
- `install_reqirements.bat` creates virtual environment (to avoid cluttering your system with random libraries) in the folder it was launched from and installs all dependencies there
- `create_launcher.bat` creates `start.bat` and `update.bat`
- `start.bat` activates virtual environment and launches main.py in it
- `update.bat` updates project (it's just `git pull` inside)
