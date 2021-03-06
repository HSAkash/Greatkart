# Generated by Django 4.0.3 on 2022-03-11 01:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_order_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Accepted', 'Accepted'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='New', max_length=30),
        ),
        migrations.AlterField(
            model_name='order',
            name='state',
            field=models.CharField(max_length=50),
        ),
    ]
