@echo off
title 파괴형 암호화툴 빌드
echo PyInstaller로 EXE 파일을 빌드합니다...

:: PyInstaller 설치 확인
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo pyinstaller가 설치되지 않았습니다. 설치를 시작합니다...
    pip install pyinstaller
)

:: 빌드 실행
pyinstaller --noconfirm --onefile --windowed main.py

echo.
echo 빌드 완료: dist\main.exe
pause
