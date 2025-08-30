from django.db import models


class MyModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.username
