$ErrorActionPreference = 'Stop'
New-Item dist -ItemType Directory -Force | Out-Null
Add-Type -AssemblyName System.IO.Compression.FileSystem
$bundle = Join-Path $PWD 'dist/addon.zip'
if (Test-Path $bundle) { Remove-Item $bundle }
[IO.Compression.ZipFile]::CreateFromDirectory((Join-Path $PWD 'addons/VFMGIS'), $bundle)
$compiler = Join-Path $env:WINDIR 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
& $compiler /nologo /target:winexe /platform:anycpu /optimize+ /out:dist/VFMGIS-Windows.exe /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /reference:System.IO.Compression.dll /reference:System.IO.Compression.FileSystem.dll /reference:System.Web.Extensions.dll /resource:dist/addon.zip,addon.zip /resource:windows/runtime.json,runtime.json windows/Launcher.cs
if ($LASTEXITCODE -ne 0) { throw 'C# compilation failed' }
$zip = Join-Path $PWD 'dist/VFMGIS-Windows.zip'
if (Test-Path $zip) { Remove-Item $zip }
Compress-Archive -Path dist/VFMGIS-Windows.exe, windows/RELEASE.md, LICENSE, THIRD_PARTY.md, windows/Launcher.cs, addons -DestinationPath $zip
Get-ChildItem dist -Include '*.exe','VFMGIS-Windows.zip' -File -Recurse | ForEach-Object {
    '{0}  {1}' -f (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower(), $_.Name
} | Set-Content dist/SHA256SUMS.txt
