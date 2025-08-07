from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

class Base(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"created at: {self.created}"


class Product(Base):
    name = models.CharField('name', max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)
    slug = models.SlugField(null=True)

    def __str__(self):
        return f"{self.name} - {self.price} R$"

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"slug": self.slug})
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)