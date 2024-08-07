from datetime import datetime

from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify



class Category(models.Model):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, db_index=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Page(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, db_index=True, blank=True)
    category = models.ManyToManyField(Category)
    image = models.ImageField(upload_to='Page/img/', blank=True, null=True)
    is_private = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Tag(models.Model):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, db_index=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Blog(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    subtitle = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, db_index=True, blank=True)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    content = RichTextField(config_name='default')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify(self.title)
            while Blog.objects.filter(slug=self.slug).exists():
                self.slug = f"{slugify(self.title)}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        else:
            existing_blog = Blog.objects.filter(pk=self.pk).first()
            if existing_blog and existing_blog.title != self.title:
                self.slug = slugify(self.title)
                while Blog.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                    self.slug = f"{slugify(self.title)}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.author.username}"



# Create your models here.
