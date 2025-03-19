from django.db import models
from django.core.validators import MinValueValidator
class Book(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=250)
    author = models.CharField(max_length=250)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        db_table = 'books'
        managed = False

    def __str__(self):
        return self.title