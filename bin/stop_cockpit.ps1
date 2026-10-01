$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$cockpitPort = 8765
if ($env:CERBERUS_UI_PORT) { $cockpitPort = [int]$env:CERBERUS_UI_PORT }
if ($cockpitPort -lt 1 -or $cockpitPort -gt 65535) { throw 'Porta inválida.' }
$listeners = @(Get-NetTCPConnection -State Listen -LocalPort $cockpitPort -ErrorAction SilentlyContinue)
$stopped = $false
foreach ($listener in $listeners) {
    $candidate = Get-CimInstance Win32_Process -Filter "ProcessId = $($listener.OwningProcess)"
    $command = $candidate.CommandLine
    if ($command -and $command.Contains($projectRoot) -and
        ($command -match 'launch_cockpit\.pyw' -or $command -match '(?:^|\s)-m\s+engine\.server(?:\s|$)')) {
        Stop-Process -Id $candidate.ProcessId
        $stopped = $true
    } elseif ($candidate) {
        Write-Host 'A porta está ocupada por outro processo; ele foi preservado.'
    }
}
if ($stopped) { Write-Host 'Painel encerrado.' }
elseif (-not $listeners.Count) { Write-Host 'Painel já estava inativo.' }
