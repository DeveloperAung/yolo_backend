from django.db import models

from apis.core.models import BaseModel
from apis.courses.models import Course
from apis.users.models import User


class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='cart_user')

    def __str__(self):
        return f'{self.user} - {self.uuid}'


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_item')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='cart_course')
    price = models.FloatField()

    def __str__(self):
        return f'{self.cart} - {self.course}'
