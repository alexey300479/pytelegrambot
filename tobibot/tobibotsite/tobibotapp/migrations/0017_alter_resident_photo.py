# Generated by Django 4.1.1 on 2022-09-17 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tobibotapp", "0016_alter_resident_email_confirm_code_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resident",
            name="photo",
            field=models.URLField(blank=True, default="", verbose_name="Фотография"),
        ),
    ]