from django.http import FileResponse, Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import VideoSerializer
from .functions import get_all_videos, hls_file_exists
from .utils import is_valid_segment_name


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def video_list_view(request):
    """Returns a list of all videos with their metadata."""
    videos = get_all_videos()
    serializer = VideoSerializer(videos, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hls_manifest_view(request, movie_id, resolution):
    """Returns the HLS playlist file (.m3u8) for the requested video and resolution."""
    exists, file_path = hls_file_exists(movie_id, resolution, 'index.m3u8')
    if not exists:
        raise Http404('Manifest not found.')
    try:
        return FileResponse(open(file_path, 'rb'), content_type='application/vnd.apple.mpegurl')
    except OSError:
        raise Http404('Manifest not found.')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hls_segment_view(request, movie_id, resolution, segment):
    """Returns a single HLS video segment (.ts file) for the requested video and resolution."""
    if not is_valid_segment_name(segment):
        raise Http404('Segment not found.')
    exists, file_path = hls_file_exists(movie_id, resolution, segment)
    if not exists:
        raise Http404('Segment not found.')
    try:
        return FileResponse(open(file_path, 'rb'), content_type='video/MP2T')
    except OSError:
        raise Http404('Segment not found.')
