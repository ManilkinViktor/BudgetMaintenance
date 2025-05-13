# models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Wallet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wallets',
        verbose_name='Пользователь'
    )
    title = models.CharField(
        max_length=100,
        verbose_name='Название кошелька'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Сумма'
    )
    proportion = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100,
        verbose_name='Процентное соотношение'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание'
    )

    class Meta:
        verbose_name = 'Кошелек'
        verbose_name_plural = 'Кошельки'

    def __str__(self):
        return f"{self.title}"


class Category(models.Model):
    TYPE_CHOICES = [
        ('income', 'Доход'),
        ('expense', 'Расход'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name='Пользователь'
    )
    title = models.CharField(
        max_length=100,
        verbose_name='Название категории'
    )
    type = models.CharField(
        max_length=7,
        choices=TYPE_CHOICES,
        verbose_name='Тип категории'
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name='Категория по умолчанию'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        unique_together = ('user', 'title', 'type')

    def __str__(self):
        return f"{self.title} ({self.type})"

    def save(self, *args, **kwargs):
        # Если это категория по умолчанию, снимаем флаг с других категорий этого пользователя
        if self.is_default:
            Category.objects.filter(user=self.user, type=self.type, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Доход'),
        ('expense', 'Расход'),
        ('transfer', 'Перевод'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='Пользователь'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Сумма'
    )
    type = models.CharField(
        max_length=8,
        choices=TRANSACTION_TYPES,
        verbose_name='Тип операции'
    )
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата операции'
    )
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='Кошелек'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Категория'
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий'
    )

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_type_display()} {self.amount} ({self.date.date()})"

    def save(self, *args, **kwargs):
        # Если категория не указана, устанавливаем категорию по умолчанию
        if not self.category and self.type in ['income', 'expense']:
            default_category = Category.objects.filter(
                user=self.user,
                type=self.type,
                is_default=True
            ).first()
            if default_category:
                self.category = default_category
        super().save(*args, **kwargs)


class Transfer(models.Model):
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Сумма перевода'
    )
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата перевода'
    )
    from_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='outgoing_transfers',
        verbose_name='Исходящий кошелек'
    )
    to_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='incoming_transfers',
        verbose_name='Входящий кошелек'
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий'
    )

    class Meta:
        verbose_name = 'Перевод'
        verbose_name_plural = 'Переводы'
        ordering = ['-date']

    def __str__(self):
        return f"Перевод {self.amount} из {self.from_wallet} в {self.to_wallet}"


# Сигнал для создания категорий по умолчанию при создании пользователя
@receiver(post_save, sender=User)
def create_default_categories(sender, instance, created, **kwargs):
    if created:
        # Создаем категории по умолчанию для доходов и расходов
        Category.objects.create(
            user=instance,
            title="Без категории (доходы)",
            type='income',
            is_default=True
        )
        Category.objects.create(
            user=instance,
            title="Без категории (расходы)",
            type='expense',
            is_default=True
        )