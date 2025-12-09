from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class MediaItem(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('movie', 'Movie'),
        ('book', 'Book'),
        ('music', 'Music'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES, default='other')
    release_date = models.DateField(null=True, blank=True)
    poster = models.ImageField(upload_to='posters/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Media Item'
        verbose_name_plural = 'Media Items'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:50] or 'item'
            slug = base
            counter = 1
            while MediaItem.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:media_detail', kwargs={'slug': self.slug})
