echo cd %cd%> start.bat
echo call venv\Scripts\activate>> start.bat
echo py main.py>> start.bat

echo cd %cd%> update.bat
echo git pull https://github.com/Svovoniks/sparrow.git>> update.bat