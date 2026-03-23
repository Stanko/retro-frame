@echo off
setlocal EnableExtensions EnableDelayedExpansion

pushd "%~dp0" >nul || exit /b 1

set "DEST=D:\"
set "ATTEMPTED=0"
set "COPIED=0"
set "FULL_MODE=0"

if /I "%~1"=="full" set "FULL_MODE=1"

call :copy_file "src\settings.py"

if "%FULL_MODE%"=="1" (
    call :copy_file "code.py"
    for /r "src" %%F in (*.py) do (
        call :copy_file "%%~fF"
    )
    goto :summary
)

for /f "delims=" %%L in ('git status --porcelain 2^>nul') do (
    set "LINE=%%L"
    set "STATUS=!LINE:~0,2!"
    set "PATHNAME=!LINE:~3!"
    set "ALLOWED="

    if not "!PATHNAME:* -> =!"=="!PATHNAME!" set "PATHNAME=!PATHNAME:* -> =!"
    set "PATHNAME=!PATHNAME:/=\!"

    if /I "!PATHNAME!"=="code.py" set "ALLOWED=1"
    if /I "!PATHNAME:~0,4!"=="src\" set "ALLOWED=1"
    if /I "!PATHNAME:~0,7!"=="assets\" set "ALLOWED=1"
    if /I "!PATHNAME:~0,4!"=="gif\" set "ALLOWED=1"

    if /I "!PATHNAME!"=="src\settings.py" set "ALLOWED="

    if defined ALLOWED (
        echo(!STATUS!| findstr /C:"D" >nul
        if errorlevel 1 (
            if exist "!PATHNAME!" (
                call :copy_file "!PATHNAME!"
            )
        )
    )
)

:summary
if "!ATTEMPTED!"=="0" (
    echo No modified or new files to copy.
) else if "!COPIED!"=="0" (
    echo No files were copied successfully.
)

popd >nul
exit /b 0

:copy_file
set "SOURCE=%~1"
if not exist "%SOURCE%" exit /b 0

set /a ATTEMPTED+=1

for %%F in ("%SOURCE%") do set "SOURCE_ABS=%%~fF"
set "SOURCE_REL=!SOURCE_ABS:%CD%\=!"
if /I "!SOURCE_REL!"=="!SOURCE_ABS!" set "SOURCE_REL=%SOURCE%"
set "SOURCE_REL=!SOURCE_REL:/=\!"

set "DEST_PATH=%DEST%!SOURCE_REL!"
for %%F in ("!DEST_PATH!") do set "DEST_DIR=%%~dpF"
if not exist "!DEST_DIR!" mkdir "!DEST_DIR!" >nul 2>&1

copy /Y "!SOURCE_ABS!" "!DEST_PATH!" >nul
if errorlevel 1 (
    echo Failed to copy !SOURCE_REL!
) else (
    echo Copied !SOURCE_REL!
    set /a COPIED+=1
)
exit /b 0
