#!/usr/bin/env bash
# Sets up the Flask app as a systemd service that starts on boot.
# Run once on the Raspberry Pi:  sudo bash setup_service.sh

set -euo pipefail

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_DIR="$(cd "$(dirname "$(realpath "$0")")" && pwd)"
PARENT_DIR="$(dirname "$PROJECT_DIR")"
PACKAGE_NAME="$(basename "$PROJECT_DIR")"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python"
SERVICE_NAME="security-system"
UNIT_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# ── Checks ─────────────────────────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    echo "ERROR: Run this script with sudo."
    exit 1
fi

# Python package names cannot contain spaces or hyphens.
# run.py contains: from security_system import create_app
# The import name must match the actual directory name on disk.
if [[ "$PACKAGE_NAME" =~ [\ \-] ]]; then
    echo "ERROR: Your project directory is named \"$PACKAGE_NAME\"."
    echo "       Python cannot import a package whose name contains spaces or hyphens."
    echo ""
    echo "       Rename the directory to 'security_system' and re-run this script:"
    echo "         mv \"$PROJECT_DIR\" \"$PARENT_DIR/security_system\""
    exit 1
fi

if [[ ! -x "$VENV_PYTHON" ]]; then
    echo "ERROR: Virtual environment not found at $PROJECT_DIR/venv"
    echo "       Create it first:"
    echo "         cd \"$PROJECT_DIR\""
    echo "         python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

CURRENT_USER="${SUDO_USER:-$USER}"

# ── Generate unit file ─────────────────────────────────────────────────────────
echo "Installing systemd unit → $UNIT_FILE"

sed \
    -e "s|__USER__|$CURRENT_USER|g" \
    -e "s|__PARENT_DIR__|$PARENT_DIR|g" \
    -e "s|__VENV_PYTHON__|$VENV_PYTHON|g" \
    -e "s|__PACKAGE_NAME__|$PACKAGE_NAME|g" \
    "$PROJECT_DIR/security-system.service" \
    > "$UNIT_FILE"

chmod 644 "$UNIT_FILE"

# ── Enable & start ─────────────────────────────────────────────────────────────
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

echo ""
echo "Done. Service status:"
systemctl status "$SERVICE_NAME" --no-pager -l
echo ""
echo "Useful commands:"
echo "  sudo systemctl status  $SERVICE_NAME   # check status"
echo "  sudo systemctl restart $SERVICE_NAME   # restart after code changes"
echo "  sudo systemctl stop    $SERVICE_NAME   # stop"
echo "  sudo journalctl -u     $SERVICE_NAME -f  # follow live logs"
