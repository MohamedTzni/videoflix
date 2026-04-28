from django.conf import settings

from .models import Video


def get_all_videos():
    """Returns all videos from the database, ordered by creation date (newest first)."""
    return Video.objects.all()


def get_hls_file_path(movie_id, resolution, filename):
    """Builds and returns the path to an HLS file."""
    return settings.MEDIA_ROOT / 'hls' / str(movie_id) / resolution / filename


def hls_file_exists(movie_id, resolution, filename):
    """Checks if the video exists in the database and if the requested HLS file is on disk."""
    if not Video.objects.filter(pk=movie_id).exists():
        return False, None
    file_path = get_hls_file_path(movie_id, resolution, filename)
    return file_path.exists(), file_path
