import uuid
from django.db import models
from django.conf import settings

from apis.core.middleware import get_current_user


class BaseModel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="%(class)s_created_by",
        null=True,
        blank=True,
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="%(class)s_modified_by",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        current_user = get_current_user()
        if not self.pk:  # New instance
            self.created_by = current_user if current_user and current_user.is_authenticated else None
        self.modified_by = current_user if current_user and current_user.is_authenticated else None
        super().save(*args, **kwargs)

    class Meta:
        abstract = True  # This makes it a base model and prevents table creation
