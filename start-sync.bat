@echo off
title Beauty Wiki — Auto Sync
echo Dang theo doi thu muc note\ ...
echo Chinh sua file .md bat ky, HTML se tu dong cap nhat.
echo Dong cua so nay de dung.
echo.
python "%~dp0sync.py" --watch
pause
