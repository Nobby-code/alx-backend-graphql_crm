import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Product

Customer.objects.create(name="Test User", email="test@crm.com")
Product.objects.create(name="Phone", price=299.99, stock=5)
Product.objects.create(name="TV", price=899.99, stock=2)

print("Seeded DB.")