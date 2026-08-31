@echo off
pushd "C:\DevManiacs\DM-Cerebro"
"C:\Python314\python.exe" -m engine.cli %*
set "CERBERUS_EXIT=%ERRORLEVEL%"
popd
exit /b %CERBERUS_EXIT%
