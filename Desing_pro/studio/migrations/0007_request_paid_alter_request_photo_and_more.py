# Generated by Django 5.1.3 on 2024-11-25 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studio', '0006_category_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='request',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='request_photos/'),
        ),
        migrations.AlterField(
            model_name='request',
            name='status',
            field=models.CharField(choices=[('new', 'Новая'), ('in_progress', 'Принято в работу'), ('completed', 'Выполнено')], default='new', max_length=50),
        ),
        migrations.AlterField(
            model_name='request',
            name='title',
            field=models.CharField(max_length=255),
        ),
    ]