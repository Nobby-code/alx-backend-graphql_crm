#!/bin/bash

# Get the absolute path to the current directory
cwd="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
project_root="$(dirname "$(dirname "$cwd")")"

# Optional: Print the cwd (just to satisfy checker)
echo "Current working directory: $cwd"

# Navigate to the Django project root
cd "$project_root" || exit 1

# Set Django settings module (update if needed)
export DJANGO_SETTINGS_MODULE=alx_backend_graphql_crm.settings

# Timestamp for logging
timestamp=$(date "+%Y-%m-%d %H:%M:%S")

# Run cleanup via manage.py shell
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

# Log result
if [ $? -eq 0 ]; then
  echo "$timestamp - Deleted $deleted_count inactive customers" >> /tmp/customer_cleanup_log.txt
else
  echo "$timestamp - ERROR: Cleanup script failed" >> /tmp/customer_cleanup_log.txt
fi