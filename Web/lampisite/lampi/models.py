from django.db import models
from django.contrib.auth.models import User

# Create your models here.
DEFAULT_USER = 'parked_device_user'


def get_parked_user():
    return get_user_model().objects.get_or_create(username=DEFAULT_USER)[0]


class Lampi(models.Model):
    name = models.CharField(max_length=50, default="My LAMPI")
    device_id = models.CharField(max_length=12, primary_key=True)
    user = models.ForeignKey(User,
                             on_delete=models.SET(get_parked_user))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}: {}".format(self.device_id, self.name)
