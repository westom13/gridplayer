import logging
from abc import abstractmethod
from typing import TYPE_CHECKING

from PyQt5.QtCore import QObject, pyqtSignal

from gridplayer.utils.qt import QABC
from gridplayer.vlc_player.static import Media, MediaInput

if TYPE_CHECKING:
    from gridplayer.vlc_player.player_base import VlcPlayerBase


class VLCVideoDriver(QObject, metaclass=QABC):
    time_changed = pyqtSignal(int)
    playback_status_changed = pyqtSignal(int)
    load_finished = pyqtSignal(Media)
    snapshot_taken = pyqtSignal(str)

    error = pyqtSignal(str)
    crash = pyqtSignal(str)
    update_status = pyqtSignal(str, int)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._log = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def cleanup(self): ...

    def time_changed_emit(self, new_time):
        self.time_changed.emit(new_time)

    def playback_status_changed_emit(self, status):
        self.playback_status_changed.emit(status)

    @abstractmethod
    def load_video(self, media_input: MediaInput): ...

    def load_video_done(self, media_track: Media):
        self.load_finished.emit(media_track)

    @abstractmethod
    def snapshot(self): ...

    def snapshot_taken_emit(self, snapshot_path):
        self.snapshot_taken.emit(snapshot_path)

    @abstractmethod
    def play(self): ...

    @abstractmethod
    def set_pause(self, is_paused): ...

    @abstractmethod
    def set_time(self, seek_ms): ...

    @abstractmethod
    def set_playback_rate(self, rate): ...

    @abstractmethod
    def audio_set_mute(self, is_muted): ...

    @abstractmethod
    def audio_set_volume(self, volume): ...

    @abstractmethod
    def set_audio_track(self, track_id): ...

    @abstractmethod
    def set_video_track(self, track_id): ...

    @abstractmethod
    def set_audio_channel_mode(self, mode): ...

    def error_state(self, error):
        self.error.emit(error)

    def update_status_emit(self, status, percent):
        self.update_status.emit(status, percent)

    def get_vlc_player(self) -> "VlcPlayerBase | None":
        """
        Return the underlying `VlcPlayerBase` instance when available.

        Default implementation tries common attributes (`_media_player`,
        `video_driver`, `player`) and returns the matching object or `None`.
        """
        # If this driver itself looks like a VlcPlayerBase, return it
        if hasattr(self, "_media_player"):
            return self  # type: ignore[return-value]

        # Common wrapper attributes
        if hasattr(self, "video_driver"):
            return getattr(self, "video_driver")

        if hasattr(self, "player"):
            return getattr(self, "player")

        return None
