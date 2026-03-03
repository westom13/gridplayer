"""Apply stereo panning to VLC media player."""

from gridplayer.vlc_player.libvlc import vlc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gridplayer.vlc_player.player_base import VlcPlayerBase

    import vlc

def apply_spatial_audio(player, column_index, total_columns,
                        max_volume=100, min_volume=70):

    if total_columns <= 1:
        player.audio_set_channel(vlc.AudioOutputChannel.Stereo)
        player.audio_set_volume(max_volume)
        return

    # ---- LEFT / RIGHT CHANNEL SPLIT ----
    midpoint = (total_columns - 1) / 2

    if column_index < midpoint:
        player.audio_set_channel(vlc.AudioOutputChannel.Left)
    elif column_index > midpoint:
        player.audio_set_channel(vlc.AudioOutputChannel.Right)
    else:
        player.audio_set_channel(vlc.AudioOutputChannel.Stereo)

    # ---- VOLUME DIMMING ----
    distance_from_center = abs(column_index - midpoint) / midpoint
    volume_range = max_volume - min_volume
    volume = max_volume - (distance_from_center * volume_range)

    player.audio_set_volume(int(volume))

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

    # 1. Get the actual MediaPlayer from the playlist manager
    # MediaListPlayer uses an internal MediaPlayer to do the actual work.
    active_player = player._playlist_player.get_media_player()

    if active_player:
        # 2. Build your filter string
        filter_str = _build_matrixmixer_filter(pan)
        
        # 3. Apply it to the active player. 
        # Note: In most VLC bindings, the method is audio_filter_set(), 
        # but some custom wrappers use set_audio_filter().
        try:
            active_player.audio_filter_set(filter_str)
            # To "kick" VLC into applying the change immediately:
            active_player.audio_set_delay(0) 
        except AttributeError:
            # Fallback if your specific wrapper uses the other name
            active_player.set_audio_filter(filter_str)

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