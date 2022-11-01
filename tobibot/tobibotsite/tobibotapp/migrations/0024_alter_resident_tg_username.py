# Generated by Django 4.1.1 on 2022-09-30 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tobibotapp", "0023_remove_resident_reg_state_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resident",
            name="tg_username",
            field=models.CharField(
                blank=True,
                default="",
                max_length=33,
                null=True,
                unique=True,
                verbose_name="Имя пользователя Telegram",
            ),
        ),
    ]
