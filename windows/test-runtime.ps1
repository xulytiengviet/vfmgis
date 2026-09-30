$ErrorActionPreference = 'Stop'
$report = Join-Path $PWD 'runtime-test.txt'
$p = Start-Process dist/VFMGIS-Windows.exe -ArgumentList @('--test-runtime', (Join-Path $PWD 'runtime'), $report) -Wait -PassThru
if ($p.ExitCode -ne 0) { throw 'Runtime preparation failed' }
$end = (Get-Date).AddMinutes(5)
while ((Get-Date) -lt $end -and -not (Test-Path $report)) { Start-Sleep -Seconds 3 }
if (-not (Test-Path $report)) {
    Get-ChildItem runtime -Recurse -Filter '*.log' | ForEach-Object { Write-Host $_.FullName; Get-Content $_.FullName -Tail 60 }
    Get-Process | Where-Object { $_.ProcessName -match 'java|gvsig' } | Format-Table Id,ProcessName,MainWindowTitle
    throw 'gvSIG did not report integration results within 5 minutes'
}
Get-Content $report
if ((Get-Content $report -Raw) -notmatch '^PASS') { throw 'gvSIG integration test failed' }
