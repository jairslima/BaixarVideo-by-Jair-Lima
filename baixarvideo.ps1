param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Url
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
& "$ScriptDir\venv\Scripts\python.exe" "$ScriptDir\baixarvideo.py" $Url
