from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    gst_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class Customer(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    gst_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class Bill(models.Model):
    bill_number = models.PositiveIntegerField(unique=True)  # Unique bill number
    customer_name = models.CharField(max_length=255)  # Customer's name
    date_of_bill = models.DateField()  # Date of the bill
    net_total = models.DecimalField(max_digits=10, decimal_places=2)  # Total amount of the bill

    def __str__(self):
        return f"Bill {self.bill_number} for {self.customer_name}"

class Item(models.Model):
    bill = models.ForeignKey(Bill, related_name='items', on_delete=models.CASCADE)  # Link to the Bill
    description = models.TextField()  # Description of the item
    batch_number = models.CharField(max_length=50, blank=True)  # Batch number of the item
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)  # Price per unit of the item
    units_purchased = models.IntegerField()  # Number of units purchased
    date_of_purchase = models.DateField()  # Date of purchase for the item
    gst = models.DecimalField(max_digits=5, decimal_places=2)  # GST applicable
    total_including_gst = models.DecimalField(max_digits=10, decimal_places=2)  # Total amount including GST

    def __str__(self):
        return f"{self.description} (Bill {self.bill.bill_number})"