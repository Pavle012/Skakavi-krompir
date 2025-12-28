@echo off
setlocal

rem An updater script for Windows systems
rem works by downloading the latest version from github and replacing the current one
rem should only work for the compiled version of the game

rem This script takes one argument: the path to the game executable to update.

rem --- Configuration ---
rem GitHub repository in the format OWNER/REPO
set "REPO=Pavle012/Skakavi-krompir"
rem The name of the release asset to download. Must end with .exe for this script.
set "ASSET_NAME=Skakavi-Krompir-Windows.exe"
rem ---------------------

set "API_URL=https://api.github.com/repos/%REPO%/releases/latest"

rem Check for game path argument
if "%~1"=="" (
    echo Usage: %0 ^<path_to_game_executable^>
    exit /b 1
)

set "GAME_PATH=%~1"
for %%F in ("%GAME_PATH%") do set "GAME_FILENAME=%%~nxF"

if not exist "%GAME_PATH%" (
    echo Error: Game executable not found at "%GAME_PATH%"
    exit /b 1
)

echo Fetching latest release information from %REPO%...

rem Use PowerShell to get the download URL for the Windows asset.
rem This is more robust than parsing JSON with batch commands.
set "PS_CMD=(Invoke-RestMethod -Uri '%API_URL%').assets | Where-Object { $_.name -like '*%ASSET_NAME%' } | Select-Object -ExpandProperty browser_download_url"
for /f "delims=" %%i in ('powershell -NoProfile -Command "%PS_CMD%"') do set "DOWNLOAD_URL=%%i"

if not defined DOWNLOAD_URL (
    echo Could not find a download URL for the asset '%ASSET_NAME%'.
    echo There might be no new release, or the asset name has changed.
    echo Please check the releases page: https://github.com/%REPO%/releases
    exit /b 1
)

echo Found download URL: %DOWNLOAD_URL%
echo Downloading latest version...

rem Download to a temporary file to avoid corruption
set "TEMP_FILE=%TEMP%\%RANDOM%-%ASSET_NAME%"

rem Use PowerShell to download the file, as it's built-in on modern Windows.
powershell -NoProfile -Command "try { Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%TEMP_FILE%' } catch { Write-Host 'Download failed.'; exit 1 }"
if errorlevel 1 (
    echo Download failed. Please check your internet connection.
    if exist "%TEMP_FILE%" del "%TEMP_FILE%"
    exit /b 1
)


echo Download complete. Replacing the old version...

rem Replace the old game executable with the new one.
rem The /Y flag suppresses prompting to overwrite.
move /Y "%TEMP_FILE%" "%GAME_PATH%"

echo Update complete! '%GAME_FILENAME%' has been updated to the latest version.
echo Running the game now...
rem Run the updated game
start "" "%GAME_PATH%"

endlocal
