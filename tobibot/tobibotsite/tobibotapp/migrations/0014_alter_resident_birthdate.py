# Generated by Django 4.1.1 on 2022-09-16 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tobibotapp", "0013_alter_resident_birthdate"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resident",
            name="birthdate",
            field=models.DateField(
                blank=True, default="1900-01-01", verbose_name="Дата рождения"
            ),
        ),
    ]
