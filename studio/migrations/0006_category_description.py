# Generated by Django 5.1.3 on 2024-11-23 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studio', '0005_request_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]