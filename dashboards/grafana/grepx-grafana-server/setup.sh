#!/bin/bash
set -e

CONFIG_FILE="./grafana.conf"

# -----------------------------
# Validate config file
# -----------------------------
if [ ! -f "$CONFIG_FILE" ]; then
  echo "ERROR: Config file $CONFIG_FILE not found"
  exit 1
fi

# Load config
source "$CONFIG_FILE"

if [ -z "$HOST" ] || [ -z "$PORT" ]; then
  echo "ERROR: HOST or PORT not set in config file"
  exit 1
fi

echo "Installing Grafana with HOST=$HOST and PORT=$PORT"

# -----------------------------
# Install dependencies
# -----------------------------
apt update -y
apt install -y apt-transport-https software-properties-common wget

# -----------------------------
# Add Grafana repository
# -----------------------------
wget -q -O - https://packages.grafana.com/gpg.key | apt-key add -

echo "deb https://packages.grafana.com/oss/deb stable main" \
  > /etc/apt/sources.list.d/grafana.list

apt update -y
apt install -y grafana

# -----------------------------
# Configure Grafana server
# -----------------------------
GRAFANA_INI="/etc/grafana/grafana.ini"

sed -i "s/^;http_addr =.*/http_addr = $HOST/" $GRAFANA_INI
sed -i "s/^;http_port =.*/http_port = $PORT/" $GRAFANA_INI

# -----------------------------
# Start & enable service
# -----------------------------
systemctl daemon-reload
systemctl enable grafana-server
systemctl restart grafana-server

# -----------------------------
# Verify
# -----------------------------
systemctl status grafana-server --no-pager

echo "Grafana installed successfully"
echo "Access URL: http://$HOST:$PORT"

