# .\run-powershell.ps1
$ErrorActionPreference = "Stop"

& python -c "import importlib.util as u, sys; sys.exit(0 if u.find_spec('pika') else 1)"
if ($LASTEXITCODE -ne 0) {
  Write-Host "Installing pika..." -ForegroundColor Yellow
  python -m pip install --user pika==1.3.2
}

# replace credientials as needed 
if (-not $env:AMQP_HOST)  { $env:AMQP_HOST  = "localhost" }
if (-not $env:AMQP_PORT)  { $env:AMQP_PORT  = "5672" }
if (-not $env:AMQP_VHOST) { $env:AMQP_VHOST = "/" }
if (-not $env:AMQP_USER)  { $env:AMQP_USER  = "jack" }
if (-not $env:AMQP_PASS)  { $env:AMQP_PASS  = "jack" }

# replace filename with python filename 
python filename.py
