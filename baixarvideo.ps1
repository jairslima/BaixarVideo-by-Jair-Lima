$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
& "$ScriptDir\venv\Scripts\python.exe" "$ScriptDir\baixarvideo.py" $args
exit $LASTEXITCODE
