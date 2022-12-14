# Generated by Django 4.1.1 on 2022-09-14 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tobibotapp", "0002_resident_description"),
    ]

    operations = [
        migrations.CreateModel(
            name="Building",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("address", models.CharField(max_length=100)),
            ],
            options={
                "verbose_name": "Здание",
                "verbose_name_plural": "Здания",
            },
        ),
        migrations.AlterModelOptions(
            name="branch",
            options={"verbose_name": "Отрасль", "verbose_name_plural": "Отрасли"},
        ),
        migrations.AlterModelOptions(
            name="resident",
            options={"verbose_name": "Резидент", "verbose_name_plural": "Резиденты"},
        ),
    ]
