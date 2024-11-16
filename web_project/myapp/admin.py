from django.contrib import admin
from .models import Profile, Product, Transaction, Notification

# Register your models here.
admin.site.register(Profile)
admin.site.register(Product)
admin.site.register(Transaction)
admin.site.register(Notification)