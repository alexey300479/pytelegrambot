# Generated by Django 4.1.1 on 2022-09-14 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tobibotapp", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="resident",
            name="description",
            field=models.CharField(default="", max_length=500),
        ),
    ]