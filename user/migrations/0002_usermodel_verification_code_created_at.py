# Generated by Django 4.2.16 on 2024-11-13 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermodel',
            name='verification_code_created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]