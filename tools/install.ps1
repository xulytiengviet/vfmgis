# VFMGIS installer. Run after closing gvSIG.
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$AddonsDirectory)
$ErrorActionPreference = 'Stop'
$source = Join-Path $PSScriptRoot '..\addons\VFMGIS'
$root = [IO.Path]::GetFullPath($AddonsDirectory)
if ((Split-Path $root -Leaf) -ne 'addons') {
    throw 'Choose the existing gvSIG scripting addons folder, not the gvSIG installation root.'
}
if (-not (Test-Path $root -PathType Container)) {
    throw 'The addons directory does not exist. Open gvSIG Scripting Composer and check its scripts location.'
}
$destination = Join-Path $root 'VFMGIS'
if (Test-Path $destination) {
    $backup = $destination + '.backup-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
    Move-Item -LiteralPath $destination -Destination $backup
    Write-Host "Previous version saved: $backup"
}
Copy-Item -LiteralPath $source -Destination $destination -Recurse
Write-Host "Installed: $destination"
Write-Host 'Restart gvSIG, then select VFMGIS > Mo VFMGIS.'
