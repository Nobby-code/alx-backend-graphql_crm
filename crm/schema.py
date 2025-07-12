import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.core.exceptions import ValidationError
from django.db import transaction

class Query(graphene.ObjectType):
    hello = graphene.String()

    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

    def resolve_hello(self, info):
        return "Hello, CRM GraphQL!"

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (graphene.relay.Node,)

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)
        

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (graphene.relay.Node,)

# class CustomerInput(graphene.InputObjectType):
#     name = graphene.String(required=True)
#     email = graphene.String(required=True)
#     phone = graphene.String()

class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists")

        customer = Customer(name=name, email=email, phone=phone)
        try:
            customer.full_clean()
            customer.save()
        except ValidationError as e:
            raise Exception(str(e))

        return CreateCustomer(customer=customer, message="Customer created successfully")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(graphene.JSONString)
        # input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    # def mutate(self, info, input):
    #     customers = []
    #     errors = []

    #     with transaction.atomic():
    #         for item in input:
    #             try:
    #                 if Customer.objects.filter(email=item.email).exists():
    #                     raise Exception(f"Email {item.email} already exists")

    #                 cust = Customer(
    #                     name=item.name,
    #                     email=item.email,
    #                     phone=item.phone
    #                 )
    #                 cust.full_clean()
    #                 cust.save()
    #                 customers.append(cust)
    #             except Exception as e:
    #                 errors.append(str(e))

    #     return BulkCreateCustomers(customers=customers, errors=errors)
    def mutate(self, info, input):
        customers = []
        errors = []

        with transaction.atomic():
            for item in input:
                try:
                    cust = Customer(
                        name=item.get('name'),
                        email=item.get('email'),
                        phone=item.get('phone')
                    )
                    cust.full_clean()
                    cust.save()
                    customers.append(cust)
                except Exception as e:
                    errors.append(str(e))
        return BulkCreateCustomers(customers=customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int()

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise Exception("Price must be greater than zero")
        if stock < 0:
            raise Exception("Stock cannot be negative")

        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids):
        if not product_ids:
            raise Exception("At least one product must be selected")

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")

        products = Product.objects.filter(id__in=product_ids)
        if len(products) != len(product_ids):
            raise Exception("One or more product IDs are invalid")

        order = Order.objects.create(customer=customer)
        order.products.set(products)
        order.save()

        return CreateOrder(order=order)

class UpdateLowStockProducts(graphene.Mutation):
    class Output(graphene.ObjectType):
        updated_products = graphene.List(ProductType)
        message = graphene.String()

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated = []

        for product in low_stock_products:
            product.stock += 10
            product.save()
            updated.append(product)

        return UpdateLowStockProducts.Output(
            updated_products=updated,
            message="Low stock products restocked successfully."
        )

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()  # updated field