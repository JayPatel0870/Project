from django.urls import reverse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
import json
from django.http import JsonResponse
import logging
from decimal import Decimal
from django.http import FileResponse, HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io

from .models import Company, Customer, Bill, Item  # Import your models

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


def generate_pdf(request):
    # Fetch the latest data from the database
    company = Company.objects.last()  # Assuming you want the latest company details
    customer = Customer.objects.last()  # Assuming you want the latest customer details
    latest_bill = Bill.objects.last()  # Retrieve the latest bill
    added_products = Item.objects.filter(bill=latest_bill)  # Get items related to the latest bill
    grand_total = sum(item.total_including_gst for item in added_products)  # Calculate the grand total

    # Check if data is present
    if not company or not customer or not latest_bill or not added_products:
        return HttpResponse("Required data is missing to generate the PDF.", status=400)

    # Create a buffer for the PDF
    buffer = io.BytesIO()
    # Set the PDF filename to "<customer_name>_<bill_number>.pdf"
    pdf_filename = f"{customer.name}_{latest_bill.bill_number}.pdf"
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1

    # Add Title
    elements.append(Paragraph("Invoice", title_style))
    elements.append(Spacer(1, 12))

    # Company Info Table
    company_data = [
        ["Company Name:", company.name],
        ["Address:", company.address],
        ["Phone:", company.phone],
        ["GST Number:", company.gst_number],
    ]
    company_table = Table(company_data, colWidths=[120, 300])
    company_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT')]))
    elements.append(company_table)
    elements.append(Spacer(1, 12))

    # Customer Info Table
    customer_data = [
        ["Customer Name:", customer.name],
        ["Address:", customer.address],
        ["Phone:", customer.phone],
        ["GST Number:", customer.gst_number],
    ]
    customer_table = Table(customer_data, colWidths=[120, 300])
    customer_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT')]))
    elements.append(customer_table)
    elements.append(Spacer(1, 12))

    # Bill Details
    elements.append(Paragraph(f"Date of Bill: {latest_bill.date_of_bill.strftime('%Y-%m-%d')}", styles['Normal']))
    elements.append(Paragraph(f"Bill Number: {latest_bill.bill_number}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Add table heading for clarity
    elements.append(Paragraph("Product Details", styles['Heading2']))
    elements.append(Spacer(1, 12))

    # Products Table
    product_data = [
        ["Description", "Royalty Number", "Date", "Price", "Units", "GST (%)",
         "Total (Including GST)"]]
    for product in added_products:
        product_data.append([
            product.description,
            product.batch_number,
            product.date_of_purchase.strftime('%Y-%m-%d'),
            product.price_per_unit,
            product.units_purchased,
            product.gst,
            product.total_including_gst
        ])

    # Set up the table with padding and center alignment
    product_table = Table(product_data, colWidths=[90, 90, 90, 70, 70, 50, 100])
    product_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),  # Add left padding
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),  # Add right padding
    ]))

    # Add some space and then add the table
    elements.append(Spacer(1, 12))
    elements.append(product_table)
    elements.append(Spacer(1, 12))

    # Grand Total
    elements.append(Paragraph(f"Grand Total: {grand_total}", styles['Heading2']))

    # Build PDF
    doc.build(elements)

    # Return PDF as a response
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=pdf_filename)


def update_bill(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    items = Item.objects.filter(bill=bill)  # Get all items associated with this bill
    customers = Customer.objects.all()  # Get all customers for dropdown

    if request.method == 'POST':
        bill.customer_id = request.POST['customer']
        bill.date_of_bill = request.POST['date_of_bill']
        bill.save()

        # Initialize net total
        net_total = Decimal(0)

        # Update the items based on the posted data
        for item in items:
            # Update item description and batch number
            item.description = request.POST.get(f'description_{item.id}', item.description)
            item.batch_number = request.POST.get(f'batch_number_{item.id}', item.batch_number)

            # Get the price and units, ensuring proper conversion
            item.price_per_unit = Decimal(request.POST.get(f'price_{item.id}', item.price_per_unit))
            try:
                item.units_purchased = int(request.POST.get(f'units_{item.id}', item.units_purchased))
            except ValueError:
                item.units_purchased = item.units_purchased  # Keep the old value if error occurs

            # Calculate total including GST
            item.total_including_gst = item.price_per_unit * Decimal(item.units_purchased)

            # Save the item with updated values
            item.save()

            # Update the net total
            net_total += item.total_including_gst

        # Update the net total for the bill
        bill.net_total = net_total
        bill.save()

        return redirect('bill')  # Redirect to the bill list after saving

    return render(request, 'update_bill.html', {
        'bill': bill,
        'items': items,
        'customers': customers,
    })