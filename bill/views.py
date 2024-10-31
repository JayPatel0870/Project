from django.urls import reverse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Max
from .models import Company, Customer, Bill, Item
import json
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


def bill_view(request):
    if request.method == "POST":
        customer_id = request.POST.get('customer')
        customer_name = request.POST.get('customer_name')
        date_of_bill = request.POST.get('date_of_bill')
        batch_number = request.POST.get('batch_number')

        # Get the product data from the request
        products_data = request.POST.get('products_data')
        products = json.loads(products_data)

        # Generate a unique bill number (implement your own logic here)
        bill_number = Bill.objects.count() + 1  # Simple example for generating bill number

        # Create a new bill entry
        bill = Bill.objects.create(
            bill_number=bill_number,
            customer_name=customer_name,
            date_of_bill=date_of_bill,
            net_total=sum(product['totalIncludingGST'] for product in products),  # Sum total amounts
        )

        # Create Item entries for each product
        for product in products:
            Item.objects.create(
                bill=bill,
                description=product['description'],
                batch_number=product['batchNumber'],
                date_of_purchase=product['dateOfPurchase'],
                price_per_unit=product['pricePerUnit'],
                units_purchased=product['unitsPurchased'],
                gst=product['gst'],
                total_including_gst=product['totalIncludingGST']
            )

        # Redirect to the generated bill page
        return JsonResponse({'redirect_url': reverse('generated_bill') + f'?bill_number={bill.bill_number}'})

    # Get the customers for the dropdown
    customers = list(Customer.objects.all())  # Convert QuerySet to a list for JSON serialization
    today = timezone.now()  # Get the current date and time
    return render(request, 'bill.html', {'customers': customers, 'today': today})

def my_company_view(request):
    company = Company.objects.first()  # Get the first Company instance, if it exists

    if request.method == "POST":
        new_company = Company(
            name=request.POST['name'],
            address=request.POST['address'],
            phone=request.POST['phone'],
            gst_number=request.POST['gst_number']
        )
        new_company.save()  # Save the new Company instance
        return redirect('my_company')  # Redirect to the same page to show updated info

    return render(request, 'my_company.html', {'company': company})

def delete_company(request):
    company = Company.objects.first()
    if company:
        company.delete()
    return redirect('my_company')

def add_customer_view(request):
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        gst_number = request.POST.get('gst_number')

        Customer.objects.create(
            name=customer_name,
            address=address,
            phone=phone,
            gst_number=gst_number
        )
        return redirect('add_customer')  # Redirect to the same page to show the updated list

    customers = Customer.objects.all()
    return render(request, 'add_customer.html', {'customers': customers})

def delete_customer_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    customer.delete()
    return redirect('add_customer')  # Redirect back to the add customer page


def generated_bill_view(request):
    bill_number = request.GET.get('bill_number')  # Get the bill number from the request
    latest_bill = get_object_or_404(Bill, bill_number=bill_number)  # Fetch the bill using the bill number
    company = get_object_or_404(Company)
    customer = get_object_or_404(Customer, name=latest_bill.customer_name)
    added_products = Item.objects.filter(bill=latest_bill)

    context = {
        'company': company,
        'customer': customer,
        'added_products': added_products,
        'grand_total': latest_bill.net_total,
        'date_of_bill': latest_bill.date_of_bill,
        'latest_bill': latest_bill,
    }

    return render(request, 'generated_bill.html', context)

def bill_list_view(request):
    bills = Bill.objects.all()  # Retrieve all bills
    return render(request, 'bill_list.html', {'bills': bills})

def delete_bill_view(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    bill.delete()  # Delete the bill
    return redirect('bill_list')  # Redirect to the bill list after deletion