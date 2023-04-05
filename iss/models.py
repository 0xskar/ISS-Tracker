from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from cities.models import City, Country
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.gis.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    email = models.EmailField(max_length=200, unique=True)
    name = models.CharField(max_length=200)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL)
    city = models.ForeignKey(City, null=True, blank=True, on_delete=models.SET_NULL)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.name

    def set_password(self, password):
        self.password = make_password(password)

    def check_password(self, password):
        return check_password(password, self.password)


# Signal receiver function to create UserProfile object for new user
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, email=instance.email, name=instance.username, password=instance.password)

