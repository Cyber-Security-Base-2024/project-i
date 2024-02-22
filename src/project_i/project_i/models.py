from django.db.models import Model, CharField, DateField

class User(Model):
    login = CharField(max_length=255)
    password = CharField(max_length=255)
    member_since = DateField()
