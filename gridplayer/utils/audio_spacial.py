import ctypes
from gridplayer.vlc_player.libvlc import vlc

def apply_spatial_audio(player, column_index, total_columns,
                        max_volume=100, min_volume=70):

    active_player = player._playlist_player.get_media_player()

    if total_columns <= 1:
        active_player.audio_set_channel(ctypes.c_int(vlc.AudioOutputChannel.Stereo))
        active_player.audio_set_volume(max_volume)
        return

    # ---- LEFT / RIGHT CHANNEL SPLIT ----
    midpoint = (total_columns - 1) / 2

    if column_index < midpoint:
        active_player.audio_set_channel(ctypes.c_int(vlc.AudioOutputChannel.Left))
    elif column_index > midpoint:
        active_player.audio_set_channel(ctypes.c_int(vlc.AudioOutputChannel.Right))
    else:
        active_player.audio_set_channel(ctypes.c_int(vlc.AudioOutputChannel.Stereo))

    # ---- VOLUME DIMMING ----
    distance_from_center = abs(column_index - midpoint) / midpoint
    volume_range = max_volume - min_volume
    volume = max_volume - (distance_from_center * volume_range)

    active_player.audio_set_volume(int(volume))
