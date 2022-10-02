from django.db import models
import secrets
from .paystack import PayStack

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='menu_images/')
    price = models.DecimalField(max_digits=5, decimal_places=2)
    category = models.ManyToManyField('Category', related_name='item')

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class OrderModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    items = models.ManyToManyField('MenuItem', related_name='order', blank=True)
    name = models.CharField(max_length=50, blank = True)
    email = models.CharField(max_length=50, blank = True)
    street = models.CharField(max_length=50, blank = True)
    city = models.CharField(max_length=50, blank = True)
    state = models.CharField(max_length=15, blank = True)
    zip_code = models.IntegerField(blank = True, null=True)



    def __str__(self):
        return f'Order: {self.created_on.strftime("%b %d %I: %M %p")}'

class Payment(models.Model):
    amount = models.PositiveIntegerField()
    ref = models.CharField(max_length=200)
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add = True)
    
    class Meta:
        ordering = ('-date_created',)

    def __str__(self) -> str:
        return f"Payment: {self.amount}"
        
    def save(self, *args, **kwargs) -> None:
        while not self.ref:
            ref = secrets.token_urlsafe(50)
            object_with_similar_ref = Payment.objects.filter(ref=ref)
            if not object_with_similar_ref:
                self.ref = ref
        super().save(*args, **kwargs)

    def amount_value(self) -> int:
        return self.amount * 100 

    def verify_payment(self):
        paystack = PayStack()
        status, result = paystack.verify_payment(self.ref, self.amount)
        if status:
            if result['amount'] / 100 == self.amount:
                self.verified = True
                self.save()
            if self.verified:
                return True
            return False