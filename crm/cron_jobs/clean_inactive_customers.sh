#!/bin/bash

# Get the directory of the current script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$PROJECT_ROOT" || exit 1

# Set the Django settings module
export DJANGO_SETTINGS_MODULE=your_project_name.settings

# Timestamp
timestamp=$(date "+%Y-%m-%d %H:%M:%S")

# Run the Django shell command
deleted_count=$(echo "
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer

cutoff_date = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(order__isnull=True, created_at__lt=cutoff_date)
count = inactive_customers.count()
inactive_customers.delete()
print(count)
" | python3 manage.py shell 2>/dev/null)

# Check if deletion ran correctly
if [ $? -eq 0 ]; then
  echo "$timestamp - Deleted $deleted_count inactive customers" >> /tmp/customer_cleanup_log.txt
else
  echo "$timestamp - ERROR: Failed to run customer cleanup" >> /tmp/customer_cleanup_log.txt
fi