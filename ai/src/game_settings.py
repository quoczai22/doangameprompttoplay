selected_character_folder = "Pink Man"

CHARACTER_LABELS = {
    "Pink Man": "PINK MAN",
    "Ninja Frog": "NINJA FROG",
}


def get_selected_character_folder():
    return selected_character_folder


def set_selected_character_folder(character_folder):
    global selected_character_folder
    selected_character_folder = character_folder


def get_selected_character_label():
    return CHARACTER_LABELS.get(selected_character_folder, selected_character_folder)
