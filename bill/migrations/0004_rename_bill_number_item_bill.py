# Generated by Django 5.1.2 on 2024-10-31 18:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bill', '0003_rename_bill_item_bill_number'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='bill_number',
            new_name='bill',
        ),
    ]