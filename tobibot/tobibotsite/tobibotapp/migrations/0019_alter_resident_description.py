# Generated by Django 4.1.1 on 2022-09-21 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tobibotapp", "0018_resident_reg_state"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resident",
            name="description",
            field=models.TextField(
                blank=True, default="", max_length=1000, verbose_name="Описание"
            ),
        ),
    ]
