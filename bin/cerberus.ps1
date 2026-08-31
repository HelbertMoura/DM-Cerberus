Push-Location -LiteralPath "C:\DevManiacs\DM-Cerebro"
try { & "C:\Python314\python.exe" -m engine.cli @args; exit $LASTEXITCODE } finally { Pop-Location }
