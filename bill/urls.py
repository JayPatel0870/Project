from django.urls import path
from . import views

urlpatterns = [
    path('', views.bill_view, name='bill'),
    path('my_company/', views.my_company_view, name='my_company'),
    path('delete_company/', views.delete_company, name='delete_company'),
    path('add_customer/', views.add_customer_view, name='add_customer'),
    path('delete_customer/<int:customer_id>/', views.delete_customer_view, name='delete_customer'),
    path('generated_bill/', views.generated_bill_view, name='generated_bill'),  # Ensure this matches your view
    path('bills/', views.bill_list_view, name='bill_list'),  # URL for bill list
    path('bills/delete/<int:bill_id>/', views.delete_bill_view, name='delete_bill'),  # URL for delete action
    path('generate_pdf/', views.generate_pdf, name='generate_pdf'),  # For latest bill
    path('generate_pdf/<str:bill_number>/', views.generate_pdf, name='generate_pdf'),
    path('update_bill/<int:bill_id>/', views.update_bill, name='update_bill'),

]
