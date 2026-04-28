from pathlib import PurePath


def is_valid_segment_name(segment):
    """Returns True if the segment filename is safe and ends with .ts, to prevent path traversal attacks."""
    return PurePath(segment).name == segment and segment.endswith('.ts')
