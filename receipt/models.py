from django.db import models
from django.contrib.auth.models import Permission, User
from django.utils import timezone
	
class Receipt(models.Model):
    user = models.ForeignKey(User, default=1,on_delete=models.CASCADE)
    CompanyName = models.CharField(max_length=250)
    receipt_picture = models.FileField()
    text= models.TextField(default=1)
    date = models.DateField(default= timezone.now())
    total = models.CharField(max_length=250,default=1)
    tax = models.CharField(max_length=250,default=1)	

