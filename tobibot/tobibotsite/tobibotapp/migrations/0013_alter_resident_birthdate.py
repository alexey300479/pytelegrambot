# Generated by Django 4.1.1 on 2022-09-16 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tobibotapp", "0012_alter_resident_birthdate_alter_resident_branch_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resident",
            name="birthdate",
            field=models.DateField(
                blank=True, default="", verbose_name="Дата рождения"
            ),
        ),
    ]