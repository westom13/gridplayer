import ctypes
from gridplayer.vlc_player.libvlc import vlc
from gridplayer.params.static import AudioChannelMode
from gridplayer.vlc_player.player_base import AUDIO_CHANNEL_MODE_MAP

def apply_spatial_audio(player, block, column_index, total_columns,
                        max_volume=100, min_volume=70):

    active_player = player._playlist_player.get_media_player()

    if total_columns <= 1:
        active_player.audio_set_channel(ctypes.c_int(1)) # Stereo
        block.set_audio_channel_mode(AudioChannelMode.STEREO) # Ensure VLC is in stereo mode
        active_player.audio_set_volume(max_volume)
        active_player.audio_set_stereo_mode(1)
        return

    # ---- LEFT / RIGHT CHANNEL SPLIT ----
    midpoint = (total_columns - 1) / 2

    if column_index < (total_columns - 1) * 1 / 3:
        active_player.audio_set_channel(ctypes.c_int(3)) # Left
        active_player.audio_set_stereo_mode(3)
        block.set_audio_channel_mode(AudioChannelMode.LEFT) # Ensure VLC is in left channel mode
    elif column_index > (total_columns - 1) * 2 / 3:
        active_player.audio_set_channel(ctypes.c_int(4)) # Right
        active_player.audio_set_stereo_mode(4)
        block.set_audio_channel_mode(AudioChannelMode.RIGHT) # Ensure VLC is in right channel mode
    else:
        active_player.audio_set_channel(ctypes.c_int(1)) # Stereo
        active_player.audio_set_stereo_mode(1)
        block.set_audio_channel_mode(AudioChannelMode.STEREO) # Ensure VLC is in stereo mode

    # ---- VOLUME DIMMING ----
    distance_from_center = abs(column_index - midpoint) / midpoint
    volume_range = max_volume - min_volume
    volume = max_volume - (distance_from_center * volume_range)

    active_player.audio_set_volume(int(volume))

    import logging
    logging.getLogger(__name__).warning(f"Set audio channel and volume for column {column_index}/{total_columns}: channel={active_player.audio_get_channel()}, volume={active_player.audio_get_volume()}")
