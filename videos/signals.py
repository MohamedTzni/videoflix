import django_rq
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Video
from .tasks import convert_video_to_hls


@receiver(post_save, sender=Video)
def trigger_video_conversion(sender, instance, created, **kwargs):
    """Starts the HLS conversion task in the background whenever a new video is uploaded."""
    if created:
        queue = django_rq.get_queue('default')
        queue.enqueue(convert_video_to_hls, instance.pk)
