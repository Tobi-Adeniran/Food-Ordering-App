from django.contrib import admin
from .models import MenuItem, OrderModel, Category
from .models import Payment

admin.site.register(MenuItem)
admin.site.register(OrderModel)
admin.site.register(Category)
admin.site.register(Payment)
