from django.db import models
from django.utils.html import mark_safe

# Create your models here.


class Building(models.Model):
    address = models.CharField(max_length=100, verbose_name='Адрес (описание)')
    tg_group_invite = models.URLField(
        default='',
        blank=True,
        verbose_name='Ссылка-приглашение в группу телеграм')

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
    exclude = ('email_confirm_code', )
    # * Реализовано в боте
    tg_user_id = models.BigIntegerField(
        primary_key=True, auto_created=False, unique=True, verbose_name='Telegram ID')
    # * Реализовано в боте
    tg_username = models.CharField(
        max_length=33, default='', unique=True, verbose_name='Имя пользователя Telegram')
    # ! Реализовано в боте только мехнизмом "Поделиться контактом" и работает
    # ! только при условии правильно заполненного профиля пользователя в Telegram
    # ! ---
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    phone = models.CharField(max_length=12, verbose_name='Телефон', blank=True)
    # ! ---
    email = models.EmailField(default='', verbose_name='Email', blank=True)
    socials = models.URLField(
        default='', verbose_name='Страница в соцсети', blank=True)
    birthdate = models.DateField(
        default='1900-01-01', verbose_name='Дата рождения', blank=True)
    photo = models.URLField(default='', verbose_name='Фотография', blank=True)
    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, default=1, verbose_name='Здание инкубатора', blank=True)
    office = models.CharField(
        max_length=50, default='', verbose_name='Офис', blank=True)
    company = models.CharField(
        max_length=100, verbose_name='Название компании', blank=True)
    branch = models.ManyToManyField(
        Branch, verbose_name='Направление', blank=True)
    website = models.URLField(
        default='', verbose_name='Сайт компании', blank=True)
    description = models.TextField(
        max_length=500, default='', verbose_name='Описание', blank=True)
    email_confirm_code = models.CharField(
        max_length=9, default='', verbose_name='Код подтверждения email')

    def __str__(self):
        return f'{self.company}. Руководитель {self.first_name} {self.last_name}'

    @property
    def photo_preview(self):
        return mark_safe(f'<img src="{self.photo.url}" width="300" height="300" />') if self.photo else ''

    class Meta:
        verbose_name = 'Резидент'
        verbose_name_plural = 'Резиденты'
