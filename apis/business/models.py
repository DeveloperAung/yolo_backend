from django.db import models

from apis.core.models import BaseModel


def logo_file_path(instance, filename):
    return "business/logo/{}".format(filename)


def social_logo_file_path(instance, filename):
    return "business/logo/social/{}".format(filename)


def carousel_file_path(instance, filename):
    return "business/carousel/social/{}".format(filename)


def bank_logo_path(instance, filename):
    return "business/logo/bank/{}".format(filename)


class Business(BaseModel):
    name = models.CharField(max_length=50)
    logo = models.ImageField(upload_to=logo_file_path, null=True)
    contact = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Carousel (BaseModel):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to=carousel_file_path, null=True)

    def __str__(self):
        return self.title


class BankInfo(BaseModel):
    title = models.CharField(max_length=50)
    logo = models.ImageField(upload_to=carousel_file_path, null=True)

    def __str__(self):
        return self.title


class PaymentBankInfo(BaseModel):
    bank = models.ForeignKey(BankInfo, on_delete=models.CASCADE, related_name='bank')
    account_no = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f'{self.bank} - {self.account_no} - {self.name}'

# class SocialApp(BaseModel):
#     name = models.CharField(max_length=50)
#     logo = models.ImageField(upload_to=social_logo_file_path, null=True)
#
#     def __str__(self):
#         return self.name
#
#
# class SocialProfile(BaseModel):
#     business = models.ForeignKey(Business, on_delete=models.SET_NULL(), null=True)
#     social_app = models.ForeignKey(SocialApp, on_delete=models.SET_NULL(), null=True)
#     title = models.CharField(max_length=150)
#     link = models.URLField(blank=True, null=True)
#
#     def __str__(self):
#         return self.name



