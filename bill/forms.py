from django import forms
from .models import Customer, Company, Bill, Item

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'address', 'phone', 'gst_number']

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'address', 'phone', 'gst_number']

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['bill_number', 'customer_name', 'date_of_bill', 'net_total']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['bill', 'description', 'batch_number', 'price_per_unit', 'units_purchased', 'date_of_purchase', 'gst', 'total_including_gst']