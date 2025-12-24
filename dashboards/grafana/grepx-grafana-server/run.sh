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
    else
      powershell.exe -NoProfile -Command "
        Start-Service -Name '$SERVICE_WINDOWS'
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
