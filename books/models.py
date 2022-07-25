import uuid

from django.db import models

# Create your models here.



class BaseModelMixin(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Book(BaseModelMixin):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    reviews = models.ManyToManyField('Review', blank=True, related_name='reviews')
    items = models.ManyToManyField('Inventory', blank=True, related_name='items')


class Review(BaseModelMixin):
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    rating = models.IntegerField()
    is_helpful = models.BooleanField(default=False)


class Inventory(BaseModelMixin):
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    remaining = models.IntegerField()
