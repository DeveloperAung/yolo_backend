from django.contrib import admin

from .models import Business, Carousel, BankInfo, PaymentBankInfo


admin.site.register(Business)
admin.site.register(Carousel)
admin.site.register(BankInfo)
admin.site.register(PaymentBankInfo)
