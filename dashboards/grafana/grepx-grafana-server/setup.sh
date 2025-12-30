#!/bin/bash
set -e

# =============================================================================
# Grafana Installation Script with Dynamic IP Detection
# =============================================================================
# This script automatically installs Grafana OSS with Infinity datasource
# and provisions a stock analysis dashboard.
# Features:
#   - Hardcoded Grafana version 12.3.1
#   - Automatic local IP detection for network accessibility
#   - Cross-platform support (Linux & Windows)
#   - Dashboard auto-loading with IP placeholder replacement
# =============================================================================

# --------------------
# Configuration
# --------------------
source ./grafana.conf
OS="$(uname -s)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Hardcoded Grafana version
GRAFANA_VERSION="12.3.1"
API_PORT="${API_PORT:-5000}"

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

log_warn() {
    echo "[WARN] $1" >&2
}

# --------------------
# IP Detection Functions
# --------------------
detect_local_ip_linux() {
    local ip=""

    # Try hostname -I first (most common)
    if command -v hostname &> /dev/null; then
        ip=$(hostname -I | awk '{print $1}' 2>/dev/null | grep -v "127.0.0.1")
        if [[ ! -z "$ip" ]]; then
            echo "$ip"
            return 0
        fi
    fi

    # Try ip command
    if command -v ip &> /dev/null; then
        ip=$(ip addr show 2>/dev/null | grep "inet " | grep -v "127.0.0.1" | awk '{print $2}' | cut -d/ -f1 | head -1)
        if [[ ! -z "$ip" ]]; then
            echo "$ip"
            return 0
        fi
    fi

    # Last resort: ifconfig
    if command -v ifconfig &> /dev/null; then
        ip=$(ifconfig 2>/dev/null | grep "inet " | grep -v "127.0.0.1" | awk '{print $2}' | head -1)
        if [[ ! -z "$ip" ]]; then
            echo "$ip"
            return 0
        fi
    fi

    log_warn "Could not auto-detect local IP, using fallback"
    echo "127.0.0.1"
}

detect_local_ip_windows() {
    log "Detecting local IP on Windows via PowerShell..."

    # This function will be called from within the PowerShell block
    # and will use PowerShell's native IP detection
    # Returns IP through PowerShell variable
    :
}

get_local_ip() {
    if [[ "$OS" == "Linux" ]]; then
        detect_local_ip_linux
    else
        # For Windows/MinGW, this will be called from PowerShell
        # Return placeholder; actual detection happens in PowerShell
        echo "DETECT_IN_POWERSHELL"
    fi
}

# --------------------
# Linux Functions
# --------------------
install_grafana_linux() {
    log "Installing Grafana $GRAFANA_VERSION on Linux..."

    sudo apt update -y
    sudo apt install -y wget software-properties-common
    wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
    echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
    sudo apt update -y
    sudo apt install -y grafana=$GRAFANA_VERSION
}

install_plugins_linux() {
    log "Installing Infinity plugin on Linux..."
    sudo grafana-cli plugins install yesoreyeram-infinity-datasource
}

provision_datasources_linux() {
    local local_ip="$1"

    log "Provisioning Infinity datasource with IP: $local_ip"

    sudo mkdir -p /etc/grafana/provisioning/datasources

    # Create datasource configuration with detected IP
    sudo tee /etc/grafana/provisioning/datasources/infinity.yaml > /dev/null << EOF
apiVersion: 1

datasources:
  - name: Infinity
    uid: DS_INFINITY
    type: yesoreyeram-infinity-datasource
    access: proxy
    editable: true
    isDefault: true
    jsonData:
      baseUrl: http://$local_ip:$API_PORT
EOF

    log "Infinity datasource provisioned"
}

provision_dashboards_linux() {
    local local_ip="$1"

    log "Provisioning dashboard configuration and JSON files with IP: $local_ip"

    # Dashboard provisioning config
    sudo mkdir -p /etc/grafana/provisioning/dashboards
    sudo cp "$SCRIPT_DIR/provisioning/dashboards/dashboards.yaml" /etc/grafana/provisioning/dashboards/

    # Create dashboards directory
    sudo mkdir -p /var/lib/grafana/dashboards

    # Copy and process dashboard JSON files
    if [[ -d "$SCRIPT_DIR/dashboard_exports" ]]; then
        for dashboard in "$SCRIPT_DIR/dashboard_exports"/*.json; do
            if [[ -f "$dashboard" ]]; then
                sudo cp "$dashboard" /var/lib/grafana/dashboards/

                # Replace IP placeholders
                filename=$(basename "$dashboard")
                sudo sed -i "s|\${GRAFANA_HOST}|$local_ip|g" "/var/lib/grafana/dashboards/$filename"
                sudo sed -i "s|http://192\.168\.142\.1|http://$local_ip|g" "/var/lib/grafana/dashboards/$filename"

                log "Processed: $filename"
            fi
        done
    else
        log_warn "Dashboard exports directory not found at: $SCRIPT_DIR/dashboard_exports"
    fi
}

configure_linux() {
    log "Configuring Grafana to run on port 3001..."

    GRAFANA_INI="/etc/grafana/grafana.ini"

    # Force http_addr
    # sudo sed -i -E \
    #   "s|^[#;]?[[:space:]]*http_addr[[:space:]]*=.*|http_addr = 0.0.0.0|" \
    #   "$GRAFANA_INI"

    # Force http_port = 3001
    sudo sed -i -E \
      "s|^[#;]?[[:space:]]*http_port[[:space:]]*=.*|http_port = 3001|" \
      "$GRAFANA_INI"

    log "Grafana port successfully set to 3001"
}

start_grafana_linux() {
    log "Starting Grafana service..."
    sudo systemctl enable grafana-server
    sudo systemctl restart grafana-server

    sleep 5
    log "Grafana service status:"
    sudo systemctl status grafana-server --no-pager
}

# --------------------
# Windows Functions
# --------------------
install_grafana_windows() {
    log "Installing Grafana $GRAFANA_VERSION on Windows..."

    # Get local IP first (will be done in PowerShell)
    local_ip=$(get_local_ip)

    powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "
        \$ErrorActionPreference = 'Stop'
        \$grafanaHome = 'C:\Program Files\GrafanaLabs\grafana'
        \$cli = \"\$grafanaHome\bin\grafana-cli.exe\"
        \$dashboardDataPath = \"\$grafanaHome\data\dashboards\"
        \$datasourcePath = \"\$grafanaHome\conf\provisioning\datasources\"

        # Hardcoded Grafana version
        \$grafanaVersion = '12.3.1'

        # ==================== STEP 0: Detect Local IP ====================
        Write-Host '===========================================' -ForegroundColor Cyan
        Write-Host 'STEP 0: Detecting Local IP Address' -ForegroundColor Cyan
        Write-Host '===========================================' -ForegroundColor Cyan

        try {
            Write-Host \"Detecting network adapters...\" -ForegroundColor Gray

            # Get all network adapters with their IPs
            \$adapters = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { \$_.IPAddress -notmatch '^127\.' -and \$_.IPAddress -notmatch '^169\.254\.' }

            # Try to find primary interface by checking connection status
            \$primaryIP = \$null

            # First, try to get the adapter with a default route (most likely the main network adapter)
            \$primaryInterface = Get-NetRoute -DestinationPrefix 0.0.0.0/0 -ErrorAction SilentlyContinue | Select-Object -First 1 | Select-Object -ExpandProperty ifIndex
            if (\$primaryInterface) {
                \$primaryIP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceIndex \$primaryInterface | Where-Object { \$_.IPAddress -notmatch '^127\.' -and \$_.IPAddress -notmatch '^169\.254\.' } | Select-Object -First 1).IPAddress
            }

            # If no primary interface found, exclude virtual adapters and pick the first valid one
            if (-not \$primaryIP) {
                Write-Host \"No primary route found, searching for non-virtual adapters...\" -ForegroundColor Gray

                \$nonVirtualIPs = @()
                foreach (\$addr in \$adapters) {
                    \$ifaceAlias = (Get-NetAdapter -InterfaceIndex \$addr.InterfaceIndex -ErrorAction SilentlyContinue).InterfaceDescription

                    # Exclude VMware, Hyper-V, VirtualBox, and other virtual adapters
                    if (\$ifaceAlias -notmatch 'VMware|Hyper-V|VirtualBox|Virtual|Adapter|ISATAP' -and \$ifaceAlias -match 'Ethernet|Wi-Fi|Wireless|LAN') {
                        Write-Host \"  Found: \$(\$addr.IPAddress) on \$ifaceAlias\" -ForegroundColor Gray
                        \$nonVirtualIPs += \$addr.IPAddress
                    }
                }

                if (\$nonVirtualIPs.Count -gt 0) {
                    \$primaryIP = \$nonVirtualIPs[0]
                }
            }

            # Last resort: use first non-loopback IP
            if (-not \$primaryIP) {
                \$primaryIP = (\$adapters | Select-Object -First 1).IPAddress
            }

            if (\$primaryIP) {
                Write-Host \"Local IP detected: \$primaryIP\" -ForegroundColor Green
                \$localIP = \$primaryIP
            } else {
                Write-Host \"Warning: Could not detect local IP, using localhost\" -ForegroundColor Yellow
                \$localIP = '127.0.0.1'
            }
        } catch {
            Write-Host \"Error detecting IP: \$_\" -ForegroundColor Yellow
            \$localIP = '127.0.0.1'
        }
        Write-Host \"\"

        # ==================== STEP 1: Admin Check ====================
        Write-Host '===========================================' -ForegroundColor Cyan
        Write-Host 'STEP 1: Checking Administrator Privileges' -ForegroundColor Cyan
        Write-Host '===========================================' -ForegroundColor Cyan

        \$isAdmin = [bool](([System.Security.Principal.WindowsIdentity]::GetCurrent()).groups -match 'S-1-5-32-544')
        if (-not \$isAdmin) {
            Write-Host 'ERROR: This script requires Administrator privileges!' -ForegroundColor Red
            Write-Host 'Please run PowerShell as Administrator and try again.' -ForegroundColor Yellow
            exit 1
        }
        Write-Host 'Running with Administrator privileges.' -ForegroundColor Green
        Write-Host \"\"

        # ==================== STEP 2: Download & Install ====================
        Write-Host '===========================================' -ForegroundColor Cyan
        Write-Host 'STEP 2: Downloading and Installing Grafana' -ForegroundColor Cyan
        Write-Host '===========================================' -ForegroundColor Cyan

        Write-Host \"Using Grafana version: \$grafanaVersion\" -ForegroundColor Green

        # Hardcoded download URL for version 12.3.1
        \$grafanaUrl = \"https://dl.grafana.com/oss/release/grafana-\$grafanaVersion.windows-amd64.msi\"

        if (-not (Test-Path 'grafana.msi')) {
            Write-Host \"Downloading Grafana v\$grafanaVersion from: \$grafanaUrl\" -ForegroundColor Cyan
            try {
                Invoke-WebRequest -Uri \$grafanaUrl -OutFile 'grafana.msi' -ErrorAction Stop
                Write-Host 'Download completed successfully.' -ForegroundColor Green
            } catch {
                Write-Host \"Failed to download from: \$grafanaUrl\" -ForegroundColor Red
                Write-Host \"Error: \$_\" -ForegroundColor Red
                exit 1
            }
        } else {
            Write-Host 'grafana.msi already exists locally, skipping download.' -ForegroundColor Yellow
        }

        Write-Host 'Stopping existing Grafana service...' -ForegroundColor Cyan
        Stop-Service grafana -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2

        Write-Host 'Installing Grafana MSI...'
        \$installResult = Start-Process msiexec.exe -Wait -PassThru -ArgumentList '/i', 'grafana.msi', '/qn', '/norestart'
        if (\$installResult.ExitCode -ne 0) {
            Write-Host \"Installation failed with exit code: \$(\$installResult.ExitCode)\" -ForegroundColor Red
            exit 1
        }
        Write-Host 'Grafana installed successfully.' -ForegroundColor Green
        Start-Sleep -Seconds 10
        Write-Host \"\"

        # ==================== STEP 3: Install Infinity Plugin ====================
        Write-Host '===========================================' -ForegroundColor Cyan
        Write-Host 'STEP 3: Installing Infinity Plugin' -ForegroundColor Cyan
        Write-Host '===========================================' -ForegroundColor Cyan

        Write-Host 'Creating plugins directory...'
        New-Item -ItemType Directory -Path \"\$grafanaHome\data\plugins\" -Force | Out-Null

        Write-Host 'Installing yesoreyeram-infinity-datasource plugin...'
        try {
            Push-Location \$grafanaHome
            & \$cli --homepath \$grafanaHome --pluginsDir \"\$grafanaHome\data\plugins\" plugins install yesoreyeram-infinity-datasource
            Pop-Location
            Write-Host 'Infinity plugin installed successfully.' -ForegroundColor Green
        } catch {
            Write-Host \"Warning: Plugin installation had issues. Continuing...\" -ForegroundColor Yellow
            Pop-Location
        }
        Write-Host \"\"

        # ==================== STEP 4: Provision Datasources ====================
        Write-Host '===========================================' -ForegroundColor Cyan
        Write-Host 'STEP 4: Provisioning Infinity Datasource' -ForegroundColor Cyan
        Write-Host '===========================================' -ForegroundColor Cyan

        Write-Host \"Creating datasource provisioning directory: \$datasourcePath\"
        New-Item -ItemType Directory -Force \$datasourcePath | Out-Null

        # Create the Infinity datasource YAML with detected IP
        Write-Host \"Creating Infinity datasource configuration with IP: \$localIP\"
        \$infinityYamlContent = @'
apiVersion: 1

datasources:
  - name: Infinity
    uid: DS_INFINITY
    type: yesoreyeram-infinity-datasource
    access: proxy
    editable: true
    isDefault: true
    jsonData:
      baseUrl: http://REPLACE_IP_HERE:5000
'@ -replace 'REPLACE_IP_HERE', \$localIP

        \$infinityYamlPath = \"\$datasourcePath\infinity.yaml\"
        Set-Content -Path \$infinityYamlPath -Value \$infinityYamlContent -Encoding UTF8
        Write-Host \"Infinity datasource provisioned at: \$infinityYamlPath\" -ForegroundColor Green
        Write-Host \"\"

        # ==================== STEP 5: Provision Dashboards ====================
        Write-Host '===========================================' -ForegroundColor Cyan
        Write-Host 'STEP 5: Provisioning Dashboard Configuration' -ForegroundColor Cyan
        Write-Host '===========================================' -ForegroundColor Cyan

        \$dashboardConfigPath = \"\$grafanaHome\conf\provisioning\dashboards\"
        Write-Host \"Creating dashboard provisioning directory: \$dashboardConfigPath\"
        New-Item -ItemType Directory -Force \$dashboardConfigPath | Out-Null

        if (Test-Path 'provisioning\dashboards\dashboards.yaml') {
            Copy-Item 'provisioning\dashboards\dashboards.yaml' \$dashboardConfigPath -Force
            Write-Host 'Dashboard provisioning config copied.' -ForegroundColor Green
        } else {
            Write-Host 'Warning: dashboards.yaml not found' -ForegroundColor Yellow
        }
        Write-Host \"\"

        # ==================== STEP 6: Copy & Process Dashboard JSON ====================
        Write-Host '===========================================' -ForegroundColor Cyan
        Write-Host 'STEP 6: Processing Dashboard JSON Files' -ForegroundColor Cyan
        Write-Host '===========================================' -ForegroundColor Cyan

        Write-Host \"Creating dashboard data directory: \$dashboardDataPath\"
        New-Item -ItemType Directory -Force \$dashboardDataPath | Out-Null

        # Get the current working directory for reference
        \$currentDir = Get-Location
        Write-Host \"Current working directory: \$currentDir\" -ForegroundColor Cyan

        # Try multiple locations for dashboard files
        \$dashboardSources = @(
            'dashboard_exports\*.json',
            '..\grafana-fastapi-middleware\dashboard_exports\*.json',
            '.\dashboard_exports\*.json'
        )

        \$dashboardsCopied = \$false
        foreach (\$source in \$dashboardSources) {
            Write-Host \"Checking for dashboards at: \$source\" -ForegroundColor Yellow

            if (Test-Path \$source) {
                Write-Host \"✓ Found dashboards at: \$source\" -ForegroundColor Green

                \$dashboardFiles = @(Get-ChildItem \$source -ErrorAction SilentlyContinue)
                if (\$dashboardFiles.Count -eq 0) {
                    Write-Host \"  No JSON files found in \$source\" -ForegroundColor Yellow
                    continue
                }

                Write-Host \"Processing \$(\$dashboardFiles.Count) dashboard file(s)...\" -ForegroundColor Green

                foreach (\$dashFile in \$dashboardFiles) {
                    Write-Host \"  Processing: \$(\$dashFile.Name)\" -ForegroundColor Cyan

                    try {
                        # Read the dashboard JSON
                        \$dashboardContent = Get-Content \$dashFile.FullName -Raw

                        # Replace IP placeholders using PowerShell -replace operator
                        Write-Host \"    Replacing IP placeholders with: \$localIP\" -ForegroundColor Gray
                        \$dashboardContent = \$dashboardContent -replace '\\\$\{GRAFANA_HOST\}', \$localIP
                        \$dashboardContent = \$dashboardContent -replace '192\.168\.142\.1', \$localIP

                        # Copy to Grafana dashboards directory with processed content
                        \$outputPath = \"\$dashboardDataPath\\\$(\$dashFile.Name)\"
                        Write-Host \"    Writing to: \$outputPath\" -ForegroundColor Gray
                        # Use UTF8Encoding(false) to avoid BOM
                        \$utf8NoBOM = New-Object System.Text.UTF8Encoding(\$false)
                        [System.IO.File]::WriteAllText(\$outputPath, \$dashboardContent, \$utf8NoBOM)

                        # Verify file was created
                        if (Test-Path \$outputPath) {
                            Write-Host \"  ✓ \$(\$dashFile.Name) copied and processed successfully\" -ForegroundColor Green
                            Write-Host \"    Size: \$((Get-Item \$outputPath).Length) bytes\" -ForegroundColor Gray
                        } else {
                            Write-Host \"  ✗ Failed to create: \$outputPath\" -ForegroundColor Red
                        }
                    } catch {
                        Write-Host \"  ✗ Error processing \$(\$dashFile.Name): \$_\" -ForegroundColor Red
                    }
                }

                \$dashboardsCopied = \$true
                break
            } else {
                Write-Host \"  Not found at this location\" -ForegroundColor Gray
            }
        }

        if (-not \$dashboardsCopied) {
            Write-Host 'ERROR: Dashboard files not found at expected locations!' -ForegroundColor Red
            Write-Host 'Expected to find dashboard_exports\*.json in current directory' -ForegroundColor Yellow
            Write-Host 'Listing current directory:' -ForegroundColor Yellow
            Get-ChildItem -Force | Where-Object { \$_.PSIsContainer -or \$_.Name -like '*.json' }
        } else {
            Write-Host \"Verifying copied files in: \$dashboardDataPath\" -ForegroundColor Green
            Get-ChildItem \$dashboardDataPath -Filter '*.json' | ForEach-Object {
                Write-Host \"  - \$(\$_.Name) (\$(\$_.Length) bytes)\" -ForegroundColor Green
            }
        }
        Write-Host \"\"

        # ==================== STEP 7: Final Configuration Verification ====================
        Write-Host '===========================================' -ForegroundColor Cyan
        Write-Host 'STEP 7: Final Configuration Verification' -ForegroundColor Cyan
        Write-Host '===========================================' -ForegroundColor Cyan
        Write-Host ''

        # Verify datasource file
        if (Test-Path \"\$datasourcePath\infinity.yaml\") {
            Write-Host '✓ Datasource configuration: OK' -ForegroundColor Green
        } else {
            Write-Host '✗ Datasource configuration: MISSING' -ForegroundColor Red
        }

        # Verify dashboard files
        \$dashboardCount = (Get-ChildItem \"\$dashboardDataPath\*.json\" -ErrorAction SilentlyContinue | Measure-Object).Count
        if (\$dashboardCount -gt 0) {
            Write-Host \"✓ Dashboard files: OK (\$dashboardCount file found)\" -ForegroundColor Green
        } else {
            Write-Host '✗ Dashboard files: MISSING' -ForegroundColor Red
        }

        # Verify provisioning config
        if (Test-Path \"\$grafanaHome\conf\provisioning\dashboards\dashboards.yaml\") {
            Write-Host '✓ Dashboard provisioning config: OK' -ForegroundColor Green
        } else {
            Write-Host '✗ Dashboard provisioning config: MISSING' -ForegroundColor Red
        }

        Write-Host \"\"
        Write-Host '=========================================' -ForegroundColor Green
        Write-Host 'Installation Complete!' -ForegroundColor Green
        Write-Host '=========================================' -ForegroundColor Green
        Write-Host \"\"
        Write-Host 'Installation Summary:' -ForegroundColor Green
        Write-Host \"  - Grafana Version: \$grafanaVersion\" -ForegroundColor Cyan
        Write-Host \"  - Installation Path: C:\Program Files\GrafanaLabs\grafana\" -ForegroundColor Cyan
        Write-Host \"  - Local Machine IP: \$localIP\" -ForegroundColor Cyan
        Write-Host \"  - Infinity Plugin: \$grafanaHome\data\plugins\" -ForegroundColor Cyan
        Write-Host \"  - Dashboards: \$dashboardDataPath\" -ForegroundColor Cyan
        Write-Host \"  - Datasources: \$datasourcePath\" -ForegroundColor Cyan
        Write-Host \"\"
        Write-Host 'Next Steps:' -ForegroundColor Yellow
        Write-Host \"  1. Run: ./run.sh start\" -ForegroundColor Yellow
        Write-Host \"  2. Access Grafana at: http://\$localIP:3000\" -ForegroundColor Yellow
        Write-Host \"  3. Login with: admin / admin\" -ForegroundColor Yellow
        Write-Host \"  4. Navigate to Stocks folder for Stock Analysis Dashboard\" -ForegroundColor Yellow
        Write-Host \"\"
        Write-Host 'Important: Service is NOT started by setup.sh' -ForegroundColor Yellow
        Write-Host '           Use ./run.sh to manage the Grafana service.' -ForegroundColor Yellow
        Write-Host \"\"
        Write-Host '=========================================' -ForegroundColor Green
    "
}

# --------------------
# Main
# --------------------
main() {
    log "=========================================="
    log "Starting Grafana Installation"
    log "=========================================="
    log "Grafana Version: $GRAFANA_VERSION"
    log "HOST: $HOST"
    log "PORT: $PORT"
    log "OS: $OS"
    log "=========================================="
    log ""

    if [[ "$OS" == "Linux" ]]; then
        local local_ip=$(detect_local_ip_linux)
        log "Detected local IP: $local_ip"

        install_grafana_linux
        install_plugins_linux
        provision_datasources_linux "$local_ip"
        provision_dashboards_linux "$local_ip"
        configure_linux
        start_grafana_linux

        log "=========================================="
        log "Installation Complete!"
        log "=========================================="
        log "Grafana Version: $GRAFANA_VERSION"
        log "Access Grafana at: http://$HOST:$PORT"
        log "API Server: http://$local_ip:5000"
        log "Default login: admin / admin"
        log "=========================================="
    else
        # Windows installation (all in PowerShell block)
        install_grafana_windows
    fi
}

main