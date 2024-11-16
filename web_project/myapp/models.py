from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Mobiteli', 'Mobiteli'),
        ('Zvučnici', 'Zvučnici'),
        ('Slušalice', 'Slušalice'),
        ('Monitori', 'Monitori'),
        ('Miševi', 'Miševi'),
        ('Računala', 'Računala'),
        ('Tipkovnice', 'Tipkovnice'),
        ('Kamere', 'Kamere'),
        ('Ostala oprema', 'Ostala oprema'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE)  
    title = models.CharField(max_length=128)  
    description = models.TextField(max_length=1000, blank=True, null=True)  
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    category = models.CharField(max_length=128, choices=CATEGORY_CHOICES, blank=True, null=True)  
    brand = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.IntegerField(default=1) 
    date_posted = models.DateTimeField(default=timezone.now)  
    image = models.ImageField(upload_to='images', blank=True, null=True, default='images/default_product_image.jpg')
    status = models.CharField(max_length=128, default="Dostupno")  
    
    def __str__(self):
        return f"{self.id}: {self.title}"

    def is_available(self):
        return self.status.lower() == "Dostupno"
    
    def mark_as_sold(self):
        self.status = "Nedostupno"
        self.save()
    
    def update_quantity(self, quantity_sold):
        if self.quantity >= quantity_sold:
            self.quantity -= quantity_sold
            if self.quantity == 0:
                self.status = "Nedostupno"
            self.save()
        else:
            raise ValueError("Nema dovoljno proizvoda na stanju.")
        
    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'product_id': self.id})
    
    
class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    city = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    name = models.CharField(max_length=50, null=True)
    surname = models.CharField(max_length=50, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('P', 'Na čekanju'),
        ('C', 'Dovršeno'),
        ('F', 'Neuspjelo'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transactions')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    stripe_payment_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Transaction {self.id} - {self.product.title} - {self.buyer.username} to {self.seller.username}"

    class Meta:
        ordering = ['-created_at']

class Notification(models.Model):
    MESSAGE_NOTIFICATION = 1
    TRANSACTION_NOTIFICATION = 2

    NOTIFICATION_TYPE_CHOICES = [
        (MESSAGE_NOTIFICATION, 'Message Notification'),
        (TRANSACTION_NOTIFICATION, 'Transaction Notification'),
    ]

    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    type = models.PositiveSmallIntegerField(choices=NOTIFICATION_TYPE_CHOICES)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']  
        
    def __str__(self):
        return f"Notification from {self.sender} to {self.receiver} - Type: {self.get_type_display()}"