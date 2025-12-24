#!/bin/bash
set -e

# =============================================================================
# Grafana Installation Script
# =============================================================================

# --------------------
# Configuration
# --------------------
source ./grafana.conf
OS="$(uname -s)"

# --------------------
# Utility Functions
# --------------------
log() {
    echo "[INFO] $1"
}

log_error() {
    echo "[ERROR] $1" >&2
    exit 1
}

# --------------------
# Linux Functions
# --------------------
install_grafana_linux() {
    log "Installing Grafana on Linux..."
    sudo apt update -y
    sudo apt install -y wget software-properties-common
    wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
    echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
    sudo apt update -y
    sudo apt install -y grafana
}

install_plugins_linux() {
    log "Installing Infinity plugin..."
    sudo grafana-cli plugins install yesoreyeram-infinity-datasource
}

provision_linux() {
    log "Setting up provisioning..."
    
    # Datasources
    sudo mkdir -p /etc/grafana/provisioning/datasources
    sudo cp provisioning/datasources/infinity.yaml /etc/grafana/provisioning/datasources/

    # Dashboards
    sudo mkdir -p /etc/grafana/provisioning/dashboards
    sudo cp provisioning/dashboards/dashboards.yaml /etc/grafana/provisioning/dashboards/

    # Dashboard JSON files
    sudo mkdir -p /var/lib/grafana/dashboards
    sudo cp dashboards/*.json /var/lib/grafana/dashboards/
}

configure_linux() {
    log "Configuring Grafana (HOST=$HOST, PORT=$PORT)..."
    sudo sed -i "s/^;http_addr =.*/http_addr = $HOST/" /etc/grafana/grafana.ini
    sudo sed -i "s/^;http_port =.*/http_port = $PORT/" /etc/grafana/grafana.ini
}

start_grafana_linux() {
    log "Starting Grafana service..."
    sudo systemctl enable grafana-server
    sudo systemctl restart grafana-server
}

# --------------------
# Windows Functions
# --------------------
install_grafana_windows() {
    log "Installing Grafana on Windows..."
    
    powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "
        \$ErrorActionPreference = 'Stop'
        \$grafanaHome = 'C:\Program Files\GrafanaLabs\grafana'
        \$cli = \"\$grafanaHome\bin\grafana-cli.exe\"

        Write-Host 'Downloading Grafana...'
        Invoke-WebRequest 'https://dl.grafana.com/oss/release/grafana-10.2.3.windows-amd64.msi' -OutFile 'grafana.msi'
        
        Write-Host 'Installing Grafana...'
        Start-Process msiexec.exe -Wait -ArgumentList '/i', 'grafana.msi', '/qn'

        Write-Host 'Installing Infinity plugin...'
        & \$cli --homepath \$grafanaHome plugins install yesoreyeram-infinity-datasource

        Write-Host 'Provisioning datasources...'
        New-Item -ItemType Directory -Force \"\$grafanaHome\conf\provisioning\datasources\" | Out-Null
        Copy-Item provisioning\datasources\infinity.yaml \"\$grafanaHome\conf\provisioning\datasources\" -Force

        Write-Host 'Provisioning dashboards...'
        New-Item -ItemType Directory -Force \"\$grafanaHome\conf\provisioning\dashboards\" | Out-Null
        Copy-Item provisioning\dashboards\dashboards.yaml \"\$grafanaHome\conf\provisioning\dashboards\" -Force
        New-Item -ItemType Directory -Force \"\$grafanaHome\data\dashboards\" | Out-Null
        Copy-Item \"..\grafana-fastapi-middleware\dashboard_exports\*.json\" \"\$grafanaHome\data\dashboards\" -Force
        Write-Host 'Restarting Grafana service...'
        Restart-Service grafana
    "
}

# --------------------
# Main
# --------------------
main() {
    log "=========================================="
    log "Starting Grafana Installation"
    log "=========================================="
    log "HOST: $HOST"
    log "PORT: $PORT"
    log "OS: $OS"
    log "=========================================="

    if [[ "$OS" == "Linux" ]]; then
        install_grafana_linux
        install_plugins_linux
        provision_linux
        configure_linux
        start_grafana_linux
    else
        install_grafana_windows
    fi

    log "=========================================="
    log "Installation Complete!"
    log "=========================================="
    log "Access Grafana at: http://$HOST:$PORT"
    log "Default login: admin / admin"
    log "=========================================="
}

main