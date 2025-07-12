#!/bin/bash

# Get the absolute path to the directory of this script
cwd="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
project_root="$(dirname "$(dirname "$cwd")")"

# Change to the root of the Django project
cd "$project_root" || exit 1

# Set the Django settings module
export DJANGO_SETTINGS_MODULE=alx_backend_graphql_crm.settings

# Timestamp for logging
timestamp=$(date "+%Y-%m-%d %H:%M:%S")

# Run the Django shell command to delete inactive customers
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

# Log output depending on success or failure
if [ $? -eq 0 ]; then
  echo "$timestamp - Deleted $deleted_count inactive customers" >> /tmp/customer_cleanup_log.txt
else
  echo "$timestamp - ERROR: Failed to run customer cleanup" >> /tmp/customer_cleanup_log.txt
fi