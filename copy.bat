@echo off
setlocal EnableExtensions EnableDelayedExpansion

pushd "%~dp0" >nul || exit /b 1

set "DEST=D:\"
set "ATTEMPTED=0"
set "COPIED=0"

for /f "delims=" %%L in ('git status --porcelain 2^>nul') do (
    set "LINE=%%L"
    set "STATUS=!LINE:~0,2!"
    set "PATHNAME=!LINE:~3!"
    set "ALLOWED="

    rem For renames, copy the new path on the right-hand side of "old -> new".
    if not "!PATHNAME:* -> =!"=="!PATHNAME!" set "PATHNAME=!PATHNAME:* -> =!"

    rem Convert git-style separators to Windows paths for cmd copy/mkdir.
    set "PATHNAME=!PATHNAME:/=\!"

    rem Only allow code.py and files under src\, assets\, or gif\.
    if /I "!PATHNAME!"=="code.py" set "ALLOWED=1"
    if /I "!PATHNAME:~0,4!"=="src\" set "ALLOWED=1"
    if /I "!PATHNAME:~0,7!"=="assets\" set "ALLOWED=1"
    if /I "!PATHNAME:~0,4!"=="gif\" set "ALLOWED=1"

    rem settings.py is copied explicitly below, so skip it here.
    if /I "!PATHNAME!"=="src\settings.py" set "ALLOWED="

    rem Skip deleted entries.
    if defined ALLOWED (
        echo(!STATUS!| findstr /C:"D" >nul
        if errorlevel 1 (
            if exist "!PATHNAME!" (
                set /a ATTEMPTED+=1
                for %%F in ("!PATHNAME!") do if not exist "%DEST%%%~dpF" mkdir "%DEST%%%~dpF" >nul 2>&1
                copy /Y "!PATHNAME!" "%DEST%!PATHNAME!" >nul
                if errorlevel 1 (
                    echo Failed to copy !PATHNAME!
                ) else (
                    echo Copied !PATHNAME!
                    set /a COPIED+=1
                )
            )
        )
    )
)

if exist "src\settings.py" (
    set /a ATTEMPTED+=1
    if not exist "%DEST%src\" mkdir "%DEST%src\" >nul 2>&1
    copy /Y "src\settings.py" "%DEST%src\settings.py" >nul
    if errorlevel 1 (
        echo Failed to copy src\settings.py
    ) else (
        echo Copied src\settings.py
        set /a COPIED+=1
    )
)

if "!ATTEMPTED!"=="0" (
    echo No modified or new files to copy.
) else if "!COPIED!"=="0" (
    echo No files were copied successfully.
)

popd >nul
