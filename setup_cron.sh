#!/usr/bin/env bash
# Sets up a cron job to run mac_mini_monitor.py every 4 hours until June 30 2026.
# Usage: bash setup_cron.sh [--remove]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITOR="$SCRIPT_DIR/mac_mini_monitor.py"
CRON_LOG="$SCRIPT_DIR/cron.log"
PYTHON="$(which python3)"
MARKER="mac_mini_monitor"

if [[ "$1" == "--remove" ]]; then
  crontab -l 2>/dev/null | grep -v "$MARKER" | crontab -
  echo "Cron job removed."
  exit 0
fi

# Ensure script is executable
chmod +x "$MONITOR"

# Build the cron line: run at minutes 0, every 4 hours, every day, until Jun 30 2026
# The script self-terminates after END_DATE, but we add an end-date guard here too
CRON_LINE="0 */4 * * * [ \"\$(date +\%Y-\%m-\%d)\" \\<= \"2026-06-30\" ] && $PYTHON $MONITOR >> $CRON_LOG 2>&1  # $MARKER"

# Remove any existing entry, then add the new one
( crontab -l 2>/dev/null | grep -v "$MARKER"; echo "$CRON_LINE" ) | crontab -

echo "Cron job installed. Schedule: every 4 hours (00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC)."
echo "Monitor script : $MONITOR"
echo "Price history  : $SCRIPT_DIR/price_history.json"
echo "Cron log       : $CRON_LOG"
echo "Monitor log    : $SCRIPT_DIR/price_monitor.log"
echo ""
echo "Optional — set these env vars for email alerts on price drops:"
echo "  export SMTP_HOST=smtp.gmail.com"
echo "  export SMTP_PORT=587"
echo "  export SMTP_USER=your-address@gmail.com"
echo "  export SMTP_PASS=your-app-password"
echo ""
echo "To remove the job: bash $0 --remove"
echo "To run manually:   python3 $MONITOR"
