#!/bin/bash

SERVICE_LINUX="grafana-server"
SERVICE_WINDOWS="grafana"
OS="$(uname -s)"

case "$1" in
  kill|stop)
    echo "Stopping Grafana..."

    # -------- Linux --------
    if [[ "$OS" == "Linux" ]]; then
      sudo systemctl stop "$SERVICE_LINUX" || true
    fi

    # -------- Windows --------
    if [[ "$OS" =~ MINGW|MSYS|CYGWIN ]]; then
      powershell.exe -NoProfile -Command "
        Stop-Service -Name '$SERVICE_WINDOWS' -ErrorAction SilentlyContinue
        Stop-Process -Name msiexec -Force -ErrorAction SilentlyContinue
      "
    fi
    ;;

  start)
    echo "Starting Grafana..."

    if [[ "$OS" == "Linux" ]]; then
      sudo systemctl start "$SERVICE_LINUX"
      echo "Waiting for Grafana to initialize (Linux)..."
      sleep 10
      echo "Grafana started. Access at: http://localhost:3001"
    else
      powershell.exe -NoProfile -Command "
        Write-Host 'Starting Grafana service...' -ForegroundColor Cyan
        Start-Service -Name '$SERVICE_WINDOWS' -ErrorAction Stop
        Write-Host 'Grafana service started.' -ForegroundColor Green
        Write-Host ''
        Write-Host 'Waiting for Grafana to initialize (10 seconds)...' -ForegroundColor Yellow
        Start-Sleep -Seconds 10
        Write-Host ''
        Write-Host 'Grafana is ready!' -ForegroundColor Green
        Write-Host 'Access Grafana at: http://localhost:3001 or http://127.0.0.1:3001' -ForegroundColor Cyan
        Write-Host 'Default login: admin / admin' -ForegroundColor Cyan
        Write-Host ''
        Write-Host 'Provisioning files:' -ForegroundColor Yellow
        Write-Host '  - Datasources: C:\Program Files\GrafanaLabs\grafana\conf\provisioning\datasources' -ForegroundColor Gray
        Write-Host '  - Dashboards: C:\Program Files\GrafanaLabs\grafana\data\dashboards' -ForegroundColor Gray
      "
    fi
    ;;

  restart)
    $0 stop
    sleep 2
    $0 start
    ;;

  status|monitor)
    echo "Grafana status:"

    if [[ "$OS" == "Linux" ]]; then
      sudo systemctl status "$SERVICE_LINUX" --no-pager
    else
      powershell.exe -NoProfile -Command "
        Get-Service -Name '$SERVICE_WINDOWS'
      "
    fi
    ;;

  *)
    echo "Usage: $0 {start|stop|kill|restart|status}"
    exit 1
    ;;
esac
