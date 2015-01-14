cd ..
pyinstaller --log-level=WARN ^
--onefile ^
--clean ^
--icon=icon\icon.ico ^
colorview2d.spec
cd win\