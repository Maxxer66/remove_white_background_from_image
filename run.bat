@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ============================================
echo   Удаление фона с изображений
echo ============================================
echo.

REM ---- Поиск Python ----
set "PY="
where python >nul 2>&1 && set "PY=python"
if not defined PY (
    where py >nul 2>&1 && set "PY=py"
)
if not defined PY (
    echo [ОШИБКА] Python не найден в PATH.
    echo Установи Python с https://www.python.org/downloads/
    echo При установке отметь "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('%PY% --version 2^>^&1') do echo Используется: %%v

REM ---- Проверка Pillow ----
%PY% -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Pillow не установлен — устанавливаю...
    %PY% -m pip install --upgrade pip
    %PY% -m pip install Pillow
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось установить Pillow.
        pause
        exit /b 1
    )
)

REM ---- Если в remove.py выбран режим rembg, ставим его ----
findstr /r /c:"^MODE *= *\"rembg\"" remove.py >nul 2>&1
if not errorlevel 1 (
    %PY% -c "import rembg" >nul 2>&1
    if errorlevel 1 (
        echo [INFO] Обнаружен режим rembg — устанавливаю библиотеку...
        echo       Это может занять несколько минут и скачать модель.
        %PY% -m pip install rembg onnxruntime
    )
)

REM ---- Запуск скрипта ----
echo.
%PY% remove.py
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
    echo [ГОТОВО] Код возврата: %RC%
) else (
    echo [ОШИБКА] Скрипт завершился с кодом %RC%
)
echo.
pause
endlocal
