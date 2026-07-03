echo cd %cd%> start.bat
echo call venv\Scripts\activate>> start.bat
echo py main.py>> start.bat

echo cd %cd%> start_gui.bat
echo call venv\Scripts\activate>> start_gui.bat
echo py main.py gui>> start_gui.bat

echo cd %cd%> update.bat
echo git pull https://github.com/Svovoniks/sparrow.git>> update.bat
echo call install_reqirements.bat>> update.bat

echo cd %cd%> update_all.bat
echo call venv\Scripts\activate>> update_all.bat
echo py main.py update>> update_all.bat
