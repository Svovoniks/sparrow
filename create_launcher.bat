echo cd %cd%> start.bat
echo call venv\Scripts\activate>> start.bat
echo py main.py>> start.bat

echo cd %cd%> update.bat
echo git pull https://github.com/Svovoniks/sparrow.git>> update.bat
echo call install_requirements.bat>> update_all.bat

echo cd %cd%> update_all.bat
echo call venv\Scripts\activate>> update_all.bat
echo py main.py update>> update_all.bat
