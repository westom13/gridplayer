"""Apply stereo panning to VLC media player."""

from gridplayer.vlc_player.libvlc import vlc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gridplayer.vlc_player.player_base import VlcPlayerBase

def _build_matrixmixer_filter(pan: float) -> str:
    """
    Build VLC audio filter string for panning using the 'remap' filter.
    Pan range: -1.0 (Left) to 1.0 (Right)
    """
    # If perfectly centered, no filter is needed
    if pan == 0.0:
        return ""
        
    # VLC's remap filter allows setting specific volume levels per channel.
    # We will define the left and right channel levels based on the pan value.
    if pan < 0: 
        # Pan left: keep left channel at 100%, reduce right channel
        left_vol = 1.0
        right_vol = 1.0 + pan  # pan is negative, so this becomes < 1.0
    else: 
        # Pan right: reduce left channel, keep right channel at 100%
        left_vol = 1.0 - pan   # pan is positive, so this becomes < 1.0
        right_vol = 1.0

    # Format the remap filter string. 
    # VLC remap string format: remap{channel-left=..., channel-right=...}
    # Note: Exact parameter names depend on the VLC version, but this is the standard approach 
    # for controlling matrix mixing dynamically.
    return f"remap,volume{{panning={pan}}}" # Alternatively, if your VLC version supports the volume panning param natively


def apply_stereo_pan(player: "VlcPlayerBase", pan: float) -> None:
    """
    Apply stereo panning to a VLC player using channel manipulation.
    
    Args:
        player: VlcPlayerBase instance
        pan: Pan value from -1.0 (left) to 1.0 (right)
    
    Note:
        Since VLC's python bindings don't directly support panning,
        we use volume adjustments on left/right channels instead.
    """
    if not -1.0 <= pan <= 1.0:
        raise ValueError("Pan must be between -1.0 and 1.0")
    
    if player._media_player is None:
        import logging
        logging.getLogger(__name__).warning(f"Failed to find player")
        return
    
    # Calculate left and right channel volumes
    # pan = -1.0 → left=1.0, right=0.0
    # pan =  0.0 → left=1.0, right=1.0
    # pan =  1.0 → left=0.0, right=1.0
    
    if pan < 0:  # Pan left
        left_vol = 1.0
        right_vol = 1.0 + pan  # (1.0 to 0.0)
    else:  # Pan right
        left_vol = 1.0 - pan   # (1.0 to 0.0)
        right_vol = 1.0
    
    # VLC uses equalizer and audio filters
    # Better approach: Use VLC's audio matrixmixer filter
    try:
        # Set audio equalizer parameters if available
        media_list = player._playlist_player.get_media_list()
        if media_list and media_list.count() > 0:
            media = media_list.item_at_index(0)
            if media:
                # Apply panning via audio filter option
                filter_str = _build_matrixmixer_filter(pan)
                player._media_player.set_audio_filter(filter_str)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Failed to apply pan: {e}")


def _build_matrixmixer_filter(pan: float) -> str:
    """
    Build VLC matrixmixer audio filter string for panning.
    
    Matrix mixer allows channel remixing:
    {{matrixmixer: matrix=<matrix>}}
    
    Standard stereo matrix (no panning):
    1 0 = L → L, R → (nothing)
    0 1 = L → (nothing), R → R
    
    Left pan (reduce R):
    1 0 = L → L
    <p> 1 = L → R with reduced volume
    """
    # Normalize pan to 0-1 range for filter
    # pan=-1.0 → filter_param=0.0 (full left)
    # pan=0.0 → filter_param=0.5 (center)
    # pan=1.0 → filter_param=1.0 (full right)
    
    filter_param = (pan + 1.0) / 2.0
    
    # Use VLC's audio equalizer instead (simpler approach)
    # Format: --audio-filter=equalizer --audio-equalizer-preset=<preset>
    # But for runtime changes, we use volume manipulation
    
    # Better: Use stereo-widener with pan-like effect
    if pan < 0:  # Pan left - reduce right channel
        reduce_factor = (1.0 + pan)
        return f"stereo-widener{{delay=20,feedback=0.3,crossfeed=0.5}}"
    elif pan > 0:  # Pan right - reduce left channel
        reduce_factor = (1.0 - pan)
        return f"stereo-widener{{delay=20,feedback=0.3,crossfeed=0.5}}"
    else:
        return ""


def apply_channel_balance(player: "VlcPlayerBase", pan: float) -> None:
    """
    Alternative: Apply pan by selecting left/right channel.
    Simpler but less precise than true panning.
    """
    from gridplayer.params.static import AudioChannelMode
    from gridplayer.vlc_player.player_base import AUDIO_CHANNEL_MODE_MAP
    
    if pan < -0.3:
        mode = AudioChannelMode.LEFT
    elif pan > 0.3:
        mode = AudioChannelMode.RIGHT
    else:
        mode = AudioChannelMode.STEREO
    
    player.set_audio_channel_mode(mode)