from gridplayer.models.video import Video
from gridplayer.params.static import VideoTransform

from gridplayer.utils.audio_panning import _build_matrixmixer_filter

TransformMap = {
    VideoTransform.ROTATE_90: "90",
    VideoTransform.ROTATE_180: "180",
    VideoTransform.ROTATE_270: "270",
    VideoTransform.HFLIP: "hflip",
    VideoTransform.VFLIP: "vflip",
    VideoTransform.TRANSPOSE: "transpose",
    VideoTransform.ANTITRANSPOSE: "antitranspose",
}


def get_vlc_options(video_params: Video | None):
    vlc_options = []

    if video_params is None:
        return vlc_options

    if video_params.transform != VideoTransform.NONE:
        option_str = TransformMap[video_params.transform]
        vlc_options.append(f"--video-filter=transform{{type='{option_str}'}}")

    # NEW: Add stereo panning support
    if video_params.spatial_balance_enabled and video_params.grid_column is not None:
        pan_value = _calculate_pan_from_column(video_params.grid_column)
        if pan_value != 0.0:
            filter_str = _build_matrixmixer_filter(pan_value)
            # Apply the dynamically generated filter string instead of hardcoding 'spatializer'
            vlc_options.append(f"--audio-filter={filter_str}")
            
            # Store pan value for later application
            video_params._pending_pan_value = pan_value

    return vlc_options


def _calculate_pan_from_column(grid_column: int) -> float:
    """Calculate pan value from grid column index."""
    # This will be set by the VideoBlocksManager
    # Returns value from -1.0 (left) to 1.0 (right)
    if hasattr(_calculate_pan_from_column, '_pan_map'):
        return _calculate_pan_from_column._pan_map.get(grid_column, 0.0)
    return 0.0


def set_pan_calculation_map(column_to_pan: dict) -> None:
    """Set the mapping from grid column to pan value."""
    _calculate_pan_from_column._pan_map = column_to_pan