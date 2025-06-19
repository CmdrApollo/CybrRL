@echo off

pyinstaller --onefile --clean --upx-dir=upx/ --exclude-module=tkinter --exclude-module=test --exclude-module=pydoc --name="Aether Collapse" main.py