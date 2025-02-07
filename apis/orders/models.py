from django.db import models
from django.contrib.auth import get_user_model

from apis.core.models import BaseModel
from apis.courses.models import Course

User = get_user_model()


class Order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20,
                              choices=[
                                  ('pending_upload', 'Pending upload'),
                                  ('pending_acceptance', 'Pending Acceptance'),
                                  ('accepted', 'Accepted')
                              ],
                              default='pending_upload')

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.course.title} in Order #{self.order.id}"
