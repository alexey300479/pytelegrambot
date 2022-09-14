from tabnanny import verbose
from django.db import models

# Create your models here.


class Building(models.Model):
    address = models.CharField(max_length=100, verbose_name='Адрес (описание)')
    tg_group_invite = models.URLField(
        default='', verbose_name='Ссылка-приглашение в группу телеграм')

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Здание'
        verbose_name_plural = 'Здания'


class Branch(models.Model):
    name = models.CharField(
        max_length=100, verbose_name='Название направления')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Направление деятельности'
        verbose_name_plural = 'Направления деятельности'


class Resident(models.Model):
    tg_user_id = models.IntegerField(
        primary_key=True, auto_created=False, unique=True, verbose_name='Telegram ID')
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    phone = models.CharField(max_length=12, verbose_name='Телефон')
    socials = models.URLField(default='', verbose_name='Страница в соцсети')
    birthdate = models.DateField(verbose_name='Дата рождения')
    photo = models.ImageField(verbose_name='Фотография', upload_to='images/')
    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, default=1, verbose_name='Здание инкубатора')
    office = models.CharField(max_length=50, default='', verbose_name='Офис')
    company = models.CharField(
        max_length=100, verbose_name='Название компании')
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, verbose_name='Направление')
    description = models.TextField(
        max_length=500, default='', verbose_name='Описание')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Резидент'
        verbose_name_plural = 'Резиденты'
