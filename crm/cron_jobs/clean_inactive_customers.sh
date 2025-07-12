#!/bin/bash

# Timestamp for logging
timestamp=$(date "+%Y-%m-%d %H:%M:%S")

# Navigate to your Django project directory
cd "$(dirname "$0")"/../..

# Run Django shell command to delete inactive customers
deleted_count=$(echo "
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer

cutoff_date = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(order__isnull=True, created_at__lt=cutoff_date)
count = inactive_customers.count()
inactive_customers.delete()
print(count)
" | python3 manage.py shell)

# Log the result
echo "$timestamp - Deleted $deleted_count inactive customers" >> /tmp/customer_cleanup_log.txt