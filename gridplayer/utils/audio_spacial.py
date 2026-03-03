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
    