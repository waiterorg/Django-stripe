from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)  # cents
    url = models.URLField()

    def __str__(self):
        return self.name
    
    def get_display_price(self):
        return "{0:.2f}".format(self.price / 100)
    
class CustomerSubscription(models.Model):
    subscription_id = models.CharField(max_length=100)
    customer_id = models.CharField(max_length=100)
    