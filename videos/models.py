from django.db import models


class Video(models.Model):
    """Stores all information about a single video including its file and thumbnail."""

    CATEGORY_CHOICES = [
        ('action', 'Action'),
        ('comedy', 'Comedy'),
        ('drama', 'Drama'),
        ('documentary', 'Documentary'),
        ('horror', 'Horror'),
        ('romance', 'Romance'),
        ('sci-fi', 'Sci-Fi'),
        ('thriller', 'Thriller'),
        ('animation', 'Animation'),
        ('sport', 'Sport'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    video_file = models.FileField(upload_to='videos/original/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        """Returns the video title as its string representation."""
        return self.title
