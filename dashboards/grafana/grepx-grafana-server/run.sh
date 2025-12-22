#!/bin/bash

SERVICE_NAME="grafana-server"

case "$1" in
  start)
    echo "Starting Grafana..."
    sudo systemctl start $SERVICE_NAME
    ;;
  
  stop|kill)
    echo "Stopping Grafana..."
    sudo systemctl stop $SERVICE_NAME
    ;;
  
  restart)
    echo "Restarting Grafana..."
    sudo systemctl restart $SERVICE_NAME
    ;;
  
  status|monitor)
    echo "Grafana status:"
    sudo systemctl status $SERVICE_NAME --no-pager
    ;;
  
  *)
    echo "Usage: $0 {start|stop|restart|status|monitor|kill}"
    exit 1
    ;;
esac

