# Generated by Django 3.1.3 on 2020-11-24 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20201124_2009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='type',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
