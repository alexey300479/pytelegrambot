# Generated by Django 4.1.1 on 2022-09-16 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tobibotapp", "0014_alter_resident_birthdate"),
    ]

    operations = [
        migrations.AddField(
            model_name="resident",
            name="email_confirm_code",
            field=models.CharField(
                default="", max_length=4, verbose_name="Код подтверждения email"
            ),
        ),
    ]
