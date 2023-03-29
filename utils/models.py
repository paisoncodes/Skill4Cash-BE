from django.db import models
import uuid


NIGERIA = "NIGERIA"

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    date_created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    name = models.CharField(max_length=225, unique=True)
    image = models.URLField(default="https://res.cloudinary.com/skill4cash/image/upload/v1/profile/default")

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name

class Keyword(models.Model):
    keyword = models.CharField(max_length=225, unique=True)
    
    def __str__(self) -> str:
        return self.keyword


class State(models.Model):
    state = models.CharField(max_length=25)
    country = models.CharField(max_length=50, default=NIGERIA)

    def __str__(self) -> str:
        return self.state

class Lga(models.Model):
    lga = models.CharField(max_length=25)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    country = models.CharField(max_length=50, default=NIGERIA)

    def __str__(self) -> str:
        return self.lga