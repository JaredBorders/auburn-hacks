from django.db import models
# from django.contrib.auth.models import User


# Create your models here.
class Location(models.Model):
    city = models.CharField(max_length=50, default='')
    state = models.CharField(max_length=2, default='')

    def __str__(self):
        return self.city + ', ' + self.state


class Shelter(models.Model):
    name = models.CharField(max_length=50, default='')
    street_addr = models.CharField(max_length=100, default='')
    location = models.ForeignKey(Location, on_delete=models.CASCADE,
                                 default='')
    zip = models.CharField(max_length=5, default='')
    max_capacity = models.IntegerField(default=10)
    current_capacity = models.IntegerField(default=0)
    photo = models.URLField(default='')
    # owner = models.ForeignKey(User, on_delete=models.CASCADE,
    #                           default='') # TODO
    owner = models.CharField(max_length=50, default='')

    def __str__(self):
        return (
            self.name +
            ' -- ' +
            self.location.city +
            ', ' +
            self.location.state)


class Comment(models.Model):
    # author = models.ForeignKey(User, on_delete=models.CASCADE,
    #                            default='') # TODO
    author = models.CharField(max_length=50, default='')
    content = models.TextField(default='')
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, default='')

    def __str__(self):
        return self.author + ' -- ' + self.content
