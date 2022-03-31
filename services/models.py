import uuid
from django.db import models

from authentication.models import ServiceProvider, User


# Create your models here.


class Category(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)

    CATEGORY_LIST = (
        ("FASHION", "Fashion"),
        ("ELECTRONICS", "Electroincs"),
        ("WEB DEVELOPMENT", "Web Development"),
        ("ARTS & CRAFTS", "Arts & Crafts"),
        ("BOOKS", "Books"),
        ("SOFTWARE", "Software"),
        ("HOME & KITCHEN", "Home & Kitchen"),
    )

    name = models.CharField(max_length=225, choices=CATEGORY_LIST)

    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self) -> str:
        return self.name


class Rating(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name="rating")
    rating = models.PositiveIntegerField()
    review = models.TextField()
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    rated_at = models.DateTimeField(auto_now_add=True)
