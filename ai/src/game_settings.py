selected_character_folder = "Pink Man"
music_enabled = True
effects_enabled = True
music_volume = 0.42
effects_volume = 0.75

CHARACTER_LABELS = {
    "Pink Man": "PINK MAN",
    "Ninja Frog": "NINJA FROG",
    "Mask Dude": "MASK DUDE",
}


def get_selected_character_folder():
    return selected_character_folder


def set_selected_character_folder(character_folder):
    global selected_character_folder
    selected_character_folder = character_folder


def get_selected_character_label():
    return CHARACTER_LABELS.get(selected_character_folder, selected_character_folder)


def is_music_enabled():
    return music_enabled


def set_music_enabled(enabled):
    global music_enabled
    music_enabled = enabled


def is_effects_enabled():
    return effects_enabled


def set_effects_enabled(enabled):
    global effects_enabled
    effects_enabled = enabled


def get_music_volume():
    return music_volume


def set_music_volume(volume):
    global music_volume
    music_volume = max(0.0, min(1.0, volume))


def get_effects_volume():
    return effects_volume


def set_effects_volume(volume):
    global effects_volume
    effects_volume = max(0.0, min(1.0, volume))
