from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    # Step 1: Log heartbeat timestamp
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{timestamp} CRM is alive\n"
    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(log_message)

    # Step 2: GraphQL health check using gql
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=False,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        query = gql("{ hello }")
        result = client.execute(query)
        print("GraphQL check passed:", result.get("hello"))
    except Exception as e:
        print("GraphQL health check failed:", e)

def update_low_stock():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_path = "/tmp/low_stock_updates_log.txt"

    # Set up GraphQL client
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=False,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)

    # Define mutation query
    mutation = gql("""
        mutation {
            updateLowStockProducts {
                updatedProducts {
                    name
                    stock
                }
                message
            }
        }
    """)

    # Run mutation and log results
    try:
        response = client.execute(mutation)
        products = response["updateLowStockProducts"]["updatedProducts"]
        message = response["updateLowStockProducts"]["message"]

        with open(log_path, "a") as log:
            log.write(f"{timestamp} - {message}\n")
            for product in products:
                log.write(f"  - {product['name']}: {product['stock']}\n")
    except Exception as e:
        with open(log_path, "a") as log:
            log.write(f"{timestamp} - ERROR: {e}\n")