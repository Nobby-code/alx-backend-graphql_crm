#!/usr/bin/env python3

from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import logging

# Configure logging
log_path = "/tmp/order_reminders_log.txt"
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
)

# Setup GraphQL client
transport = RequestsHTTPTransport(
    url='http://localhost:8000/graphql',
    verify=False,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=False)

# Compute the date range (last 7 days)
seven_days_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
today = datetime.now().date().isoformat()

# GraphQL query
query = gql(
    """
    query GetRecentPendingOrders($start: Date, $end: Date) {
      orders(orderDate_Gte: $start, orderDate_Lte: $end, status: "PENDING") {
        id
        customer {
          email
        }
      }
    }
    """
)

# Execute query
try:
    result = client.execute(query, variable_values={"start": seven_days_ago, "end": today})
    orders = result.get("orders", [])
    for order in orders:
        order_id = order["id"]
        email = order["customer"]["email"]
        logging.info(f"Reminder: Order ID {order_id}, Customer Email: {email}")
except Exception as e:
    logging.error(f"Error fetching orders: {e}")

print("Order reminders processed!")