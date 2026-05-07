import os
import subprocess

from django.conf import settings

from .models import Video


def run_ffmpeg_conversion(input_path, output_dir, height):
    """Converts a video to HLS format at the given height and saves the segments to output_dir."""
    os.makedirs(output_dir, exist_ok=True)
    segment_path = os.path.join(output_dir, 'segment%03d.ts')
    manifest_path = os.path.join(output_dir, 'index.m3u8')
    subprocess.run([
        'ffmpeg', '-i', input_path,
        '-vf', f'scale=-2:{height}',
        '-c:v', 'h264',
        '-c:a', 'aac',
        '-hls_time', '10',
        '-hls_playlist_type', 'vod',
        '-hls_segment_filename', segment_path,
        manifest_path,
    ], check=True)


def generate_thumbnail(video_id, input_path):
    """Extracts a single frame at 3 seconds from the video and saves it as a JPEG thumbnail."""
    thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
    os.makedirs(thumbnail_dir, exist_ok=True)
    thumbnail_path = os.path.join(thumbnail_dir, f'{video_id}.jpg')
    subprocess.run([
        'ffmpeg', '-i', input_path,
        '-ss', '00:00:03',
        '-vframes', '1',
        thumbnail_path, '-y',
    ], check=True)
    return thumbnail_path


def save_thumbnail(video, thumbnail_path):
    """Saves the generated thumbnail path to the video record in the database."""
    relative_path = os.path.relpath(thumbnail_path, settings.MEDIA_ROOT)
    video.thumbnail = relative_path
    video.save(update_fields=['thumbnail'])


def generate_and_save_thumbnail(video_id):
    """Generates and saves an auto-thumbnail for a video that has no thumbnail."""
    video = Video.objects.get(pk=video_id)
    input_path = os.path.join(settings.MEDIA_ROOT, video.video_file.name)
    thumbnail_path = generate_thumbnail(video_id, input_path)
    save_thumbnail(video, thumbnail_path)


def convert_video_to_hls(video_id):
    """Converts the uploaded video to HLS format in 480p, 720p, and 1080p."""
    video = Video.objects.get(pk=video_id)
    input_path = os.path.join(settings.MEDIA_ROOT, video.video_file.name)
    base_output = os.path.join(settings.MEDIA_ROOT, 'hls', str(video_id))
    run_ffmpeg_conversion(input_path, os.path.join(base_output, '480p'), 480)
    run_ffmpeg_conversion(input_path, os.path.join(base_output, '720p'), 720)
    run_ffmpeg_conversion(input_path, os.path.join(base_output, '1080p'), 1080)
