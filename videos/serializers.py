from rest_framework import serializers

from .models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Converts a Video object into JSON data for the frontend."""

    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = (
            'id',
            'created_at',
            'title',
            'description',
            'thumbnail_url',
            'category',
        )

    def get_thumbnail_url(self, obj):
        """Returns the full absolute URL to the thumbnail image, or an empty string if none exists."""
        request = self.context.get('request')
        if not obj.thumbnail:
            return ''
        if request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return obj.thumbnail.url
