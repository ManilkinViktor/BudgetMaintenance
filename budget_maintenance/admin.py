from django.contrib import admin
from . import models

# Register your models here.

admin.register(models.Wallet)
admin.register(models.Transaction)
admin.register(models.Category)
admin.register(models.Transfer)