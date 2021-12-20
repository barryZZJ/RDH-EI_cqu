call venv\Scripts\activate.bat
python -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Finish!
pause