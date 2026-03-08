from gridplayer.vlc_player.libvlc import vlc

def apply_spatial_audio(player, pan: float):
    if player is None:
        return

    try:
        # We target the StereoMode constants (3=Left, 4=Right, 1=Stereo)
        # These constants specifically handle spatial routing to hardware
        if pan < -0.2:
            mode = 3  # Physical Left only
        elif pan > 0.2:
            mode = 4  # Physical Right only
        else:
            mode = 1  # Standard Stereo
            
        # audio_set_stereo_mode is the standard VLC way to handle 
        # spatial "balancing" without complex filters.
        player.audio_set_stereo_mode(mode)
        
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Failed to set stereo mode: {e}")