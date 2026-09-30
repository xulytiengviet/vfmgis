$ErrorActionPreference = 'Stop'
$report = Join-Path $PWD 'runtime-test.txt'
$p = Start-Process dist/VFMGIS-Windows.exe -ArgumentList @('--test-archive', (Join-Path $PWD 'runtime.zip'), $report) -Wait -PassThru
if ($p.ExitCode -ne 0) { throw 'Runtime preparation failed' }
$end = (Get-Date).AddMinutes(5)
while ((Get-Date) -lt $end -and -not (Test-Path $report)) { Start-Sleep -Seconds 3 }
if (-not (Test-Path $report)) {
    if (Test-Path ($report + '.progress')) { Get-Content ($report + '.progress') }
    Get-ChildItem 'runtime*' -Recurse -Filter '*.log' | ForEach-Object { Write-Host $_.FullName; Get-Content $_.FullName -Tail 60 }
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
    $bounds = [Windows.Forms.SystemInformation]::VirtualScreen
    $shot = [Drawing.Bitmap]::new($bounds.Width, $bounds.Height)
    $graphics = [Drawing.Graphics]::FromImage($shot)
    $graphics.CopyFromScreen($bounds.Left, $bounds.Top, 0, 0, $bounds.Size)
    $shot.Save((Join-Path $PWD 'dist/windows-timeout.png'))
    $graphics.Dispose(); $shot.Dispose()
    Get-Process | Where-Object { $_.ProcessName -match 'java|gvsig' } | Format-Table Id,ProcessName,MainWindowTitle
    throw 'gvSIG did not report integration results within 5 minutes'
}
Get-Content $report
if ((Get-Content $report -Raw) -notmatch '^PASS') { throw 'gvSIG integration test failed' }
