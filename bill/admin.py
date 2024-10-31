from django.contrib import admin

# Register your models here.

from .models import Customer, Company, Bill, Item  # Import your models

admin.site.register(Customer)
admin.site.register(Company)
admin.site.register(Bill)
admin.site.register(Item)