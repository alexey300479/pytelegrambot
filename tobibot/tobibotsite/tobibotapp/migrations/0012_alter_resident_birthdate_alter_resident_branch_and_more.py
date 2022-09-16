# Generated by Django 4.1.1 on 2022-09-16 13:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("tobibotapp", "0011_resident_tg_username"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resident",
            name="birthdate",
            field=models.DateField(blank=True, verbose_name="Дата рождения"),
        ),
        migrations.AlterField(
            model_name="resident",
            name="branch",
            field=models.ManyToManyField(
                blank=True, to="tobibotapp.branch", verbose_name="Направление"
            ),
        ),
        migrations.AlterField(
            model_name="resident",
            name="building",
            field=models.ForeignKey(
                blank=True,
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="tobibotapp.building",
                verbose_name="Здание инкубатора",
            ),
        ),
        migrations.AlterField(
            model_name="resident",
            name="company",
            field=models.CharField(
                blank=True, max_length=100, verbose_name="Название компании"
            ),
        ),
        migrations.AlterField(
            model_name="resident",
            name="description",
            field=models.TextField(
                blank=True, default="", max_length=500, verbose_name="Описание"
            ),
        ),
        migrations.AlterField(
            model_name="resident",
            name="email",
            field=models.EmailField(
                blank=True, default="", max_length=254, verbose_name="Email"
            ),
        ),
        migrations.AlterField(
            model_name="resident",
            name="office",
            field=models.CharField(
                blank=True, default="", max_length=50, verbose_name="Офис"
            ),
        ),
        migrations.AlterField(
            model_name="resident",
            name="phone",
            field=models.CharField(blank=True, max_length=12, verbose_name="Телефон"),
        ),
        migrations.AlterField(
            model_name="resident",
            name="socials",
            field=models.URLField(
                blank=True, default="", verbose_name="Страница в соцсети"
            ),
        ),
        migrations.AlterField(
            model_name="resident",
            name="website",
            field=models.URLField(blank=True, default="", verbose_name="Сайт компании"),
        ),
    ]