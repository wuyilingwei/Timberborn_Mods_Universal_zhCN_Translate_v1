@echo off
title Initializator

echo [Init info] Initializator started

echo [Init info] Initializate Python Libs
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [Init error] Error while installing Libs
    echo [Init info] You must installed python 3.6 or higher
    echo [Init info] Initializator will close in 5 seconds.
    timeout /t 5 /nobreak >nul
    exit
)
echo [Init info] Initializate SteamCMD
mkdir steamcmd >nul 2>&1
cd steamcmd
curl -s https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip -o steamcmd.zip
tar -xf steamcmd.zip
del /q steamcmd.zip
steamcmd +quit

echo [Init info] Initializated SteamCMD
echo [Init info] Done! Environment is ready.
echo [Init info] Check the logs for any errors. Next step will start in 5 seconds.
timeout /t 5 /nobreak >nul
cls

echo [Init info] Setting up secrets

echo [Init info] Please enter your Openai API key:
set /p openai_key=
echo [Init info] Openai API key set
echo [Init info] Please enter openai model name:(suggest:gpt-4o-mini)
set /p model=
echo [Init info] Openai model set
echo [Init info] Please enter model prompt token price:(gpt-4o-mini:0.00000015)
set /p prompt_tokens_price=
echo [Init info] Token price set
echo [Init info] Please enter model completion token price:(gpt-4o-mini:0.0000006)
set /p completion_tokens_price=
echo [Init info] Token price set
echo [Init info] Please enter your Steam username:
set /p steam_username=
echo [Init info] Steam username set
echo [Init info] We will try to login to Steam in 5 seconds
echo [Init info] If you have Steam Guard enabled, you will need to enter the two-factor code
echo [Init info] It can find in your email or in your phone show the code
echo [Init info] This is a one-time process, your password will not be saved
timeout /t 5 /nobreak >nul
steamcmd +login %steam_username% +quit

cd ..
echo [Openai]> secret.ini
echo api_key=%openai_key%>> secret.ini
echo api_url=https://api.openai.com/v1/chat/completions>> secret.ini
echo model=%model%>> secret.ini
echo prompt_tokens_price=%prompt_tokens_price%>> secret.ini
echo completion_tokens_price=%completion_tokens_price%>> secret.ini
echo.>> secret.ini
echo [Steam]>> secret.ini
echo username=%steam_username%>> secret.ini
echo [Init info] Secrets set
echo [Init info] Never share your secret.ini and steamcmd folder with anyone

echo [Init info] Initializator will close in 5 seconds.
timeout /t 5 /nobreak >nul
exit