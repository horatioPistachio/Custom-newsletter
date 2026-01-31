#!/bin/bash

# Create the log file to be able to run tail
touch /var/log/cron.log

# Set default cron schedule if not provided (6:00 AM daily)
CRON_SCHEDULE="${CRON_SCHEDULE:-0 6 * * *}"

echo "Setting up cron job with schedule: $CRON_SCHEDULE"

# Create cron job file with the schedule from environment variable
echo "$CRON_SCHEDULE cd /app && /usr/local/bin/python /app/main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/newsletter-cron

# Give execution rights on the cron job
chmod 0644 /etc/cron.d/newsletter-cron

# Apply cron job
crontab /etc/cron.d/newsletter-cron

# Display the installed cron job
echo "Installed cron job:"
crontab -l

# Add environment variables to cron
printenv | grep -v "no_proxy" >> /etc/environment

# Start cron in the foreground
cron && tail -f /var/log/cron.log
