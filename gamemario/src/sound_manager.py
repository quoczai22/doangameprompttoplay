import os
import atexit
import gc

import arcade
import pyglet.media.codecs.wmf as pyglet_wmf

from Settings import ASSETS_PATH
from game_settings import (
    get_effects_volume,
    get_music_volume,
    is_effects_enabled,
    is_music_enabled,
)


SOUNDS_PATH = os.path.join(ASSETS_PATH, "sounds")

MENU_MUSIC = "menusound"
SUPPORTED_AUDIO_EXTENSIONS = (".wav", ".ogg")
FALLBACK_AUDIO_EXTENSIONS = (".mp3",)
EFFECT_SOUND_BASENAMES = {
    "click": "click",
    "checkpoint": "checkpoint",
    "selectbutton": "selectbutton",
    "collectitem": "collectitem",
    "die": "die",
    "jump": "jump",
    "spawn": "spawn",
    "throw": "throw",
    "finish": "finish",
}

_loaded_sounds = {}
_menu_music_player = None
_active_effect_players = {}
_all_players = []
_missing_sounds = set()
_wmf_destructor_patched = False


def _patch_wmf_destructor():
    """
    Pyglet's WMF mp3 decoder can raise a harmless exception from __del__ on
    Windows shutdown. Patch it once so mp3 files can still be used without
    noisy ignored-exception tracebacks.
    """
    global _wmf_destructor_patched
    if _wmf_destructor_patched:
        return

    original_del = getattr(pyglet_wmf.WMFSource, "__del__", None)
    if original_del is None:
        _wmf_destructor_patched = True
        return

    def safe_del(self):
        try:
            original_del(self)
        except Exception:
            pass

    pyglet_wmf.WMFSource.__del__ = safe_del
    _wmf_destructor_patched = True


_patch_wmf_destructor()


def _resolve_sound_path(sound_name):
    basename = MENU_MUSIC if sound_name == MENU_MUSIC else EFFECT_SOUND_BASENAMES.get(sound_name)
    if not basename:
        return None

    for extension in SUPPORTED_AUDIO_EXTENSIONS:
        sound_path = os.path.join(SOUNDS_PATH, f"{basename}{extension}")
        if os.path.exists(sound_path):
            return sound_path

    for extension in FALLBACK_AUDIO_EXTENSIONS:
        fallback_path = os.path.join(SOUNDS_PATH, f"{basename}{extension}")
        if os.path.exists(fallback_path):
            _patch_wmf_destructor()
            return fallback_path

    if sound_name not in _missing_sounds:
        expected = ", ".join(f"{basename}{extension}" for extension in SUPPORTED_AUDIO_EXTENSIONS)
        print(f"[Sound] Khong tim thay file am thanh ho tro: {expected}")
        _missing_sounds.add(sound_name)
    return None


def _load_sound(sound_name):
    if sound_name in _loaded_sounds:
        return _loaded_sounds[sound_name]

    sound_path = _resolve_sound_path(sound_name)
    if sound_path is None:
        return None

    try:
        sound = arcade.load_sound(sound_path)
    except Exception as exc:
        if sound_name not in _missing_sounds:
            print(f"[Sound] Khong load duoc {sound_path}: {exc}")
            _missing_sounds.add(sound_name)
        return None

    _loaded_sounds[sound_name] = sound
    return sound


def _play(sound, volume=1.0, looping=False):
    if sound is None:
        return None

    try:
        player = arcade.play_sound(sound, volume=volume, looping=looping)
        _remember_player(player)
        return player
    except TypeError:
        try:
            player = sound.play(volume=volume, loop=looping)
        except TypeError:
            player = sound.play(volume)
        _remember_player(player)
        return player
    except Exception as exc:
        print(f"[Sound] Khong phat duoc am thanh: {exc}")
        return None


def _remember_player(player):
    if player is not None:
        _all_players.append(player)


def _stop_player(player):
    if player is None:
        return

    stopped = False
    try:
        if hasattr(player, "pause"):
            player.pause()
            stopped = True
        if hasattr(player, "delete"):
            player.delete()
            stopped = True
    except Exception:
        pass

    if not stopped:
        try:
            arcade.stop_sound(player)
        except Exception:
            pass


def _set_player_volume(player, volume):
    if player is None:
        return

    try:
        player.volume = volume
    except Exception:
        pass


def play_effect(sound_name, volume=0.75, looping=False):
    if not is_effects_enabled():
        return None

    sound = _load_sound(sound_name)
    if sound_name == "click" or looping:
        _stop_player(_active_effect_players.get(sound_name))

    player = _play(sound, volume=volume * get_effects_volume(), looping=looping)
    if sound_name == "click" or looping:
        _active_effect_players[sound_name] = player
    return player


def stop_effect(sound_name):
    player = _active_effect_players.get(sound_name)
    _stop_player(player)
    _active_effect_players[sound_name] = None


def play_menu_music(volume=None):
    global _menu_music_player
    if not is_music_enabled():
        stop_menu_music()
        return

    actual_volume = get_music_volume() if volume is None else volume
    if _menu_music_player is not None:
        _set_player_volume(_menu_music_player, actual_volume)
        return

    sound = _load_sound(MENU_MUSIC)
    _menu_music_player = _play(sound, volume=actual_volume, looping=True)


def stop_menu_music():
    global _menu_music_player
    if _menu_music_player is None:
        return

    _stop_player(_menu_music_player)
    _menu_music_player = None


def stop_all_sounds():
    global _menu_music_player, _all_players

    stop_menu_music()

    for sound_name, player in list(_active_effect_players.items()):
        _stop_player(player)
        _active_effect_players[sound_name] = None

    _active_effect_players.clear()

    for player in list(_all_players):
        _stop_player(player)
    _all_players = []

    _loaded_sounds.clear()
    gc.collect()


def refresh_menu_music():
    if is_music_enabled():
        play_menu_music()
    else:
        stop_menu_music()


def refresh_effects():
    if is_effects_enabled():
        return

    for sound_name, player in list(_active_effect_players.items()):
        _stop_player(player)
        _active_effect_players[sound_name] = None

    _active_effect_players.clear()


atexit.register(stop_all_sounds)
