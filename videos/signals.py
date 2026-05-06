import logging

import django_rq
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Video
from .tasks import convert_video_to_hls, generate_and_save_thumbnail

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Video)
def trigger_video_conversion(sender, instance, created, **kwargs):
    """Starts HLS conversion on creation, or auto-generates a thumbnail when it has been cleared."""
    try:
        high_queue = django_rq.get_queue('high')
        default_queue = django_rq.get_queue('default')
        if created:
            if not instance.thumbnail:
                high_queue.enqueue(generate_and_save_thumbnail, instance.pk)
            default_queue.enqueue(convert_video_to_hls, instance.pk)
        elif not instance.thumbnail:
            high_queue.enqueue(generate_and_save_thumbnail, instance.pk)
    except Exception:
        logger.exception('Failed to enqueue video task for video %s', instance.pk)
