# Generated by Django 4.1.1 on 2022-09-14 15:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("tobibotapp", "0003_building_alter_branch_options_alter_resident_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="resident",
            name="building",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="tobibotapp.building",
            ),
        ),
        migrations.AddField(
            model_name="resident",
            name="office",
            field=models.CharField(default="", max_length=50),
        ),
    ]
