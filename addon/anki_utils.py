import anki.collection
import aqt
from typing import List

class AnkiUtils():
    def __init__(self):
        pass

    def get_note_type_list(self) -> List[str]:
        return aqt.mw.col.models.all_names()

    def get_field_list_for_note_type(self, note_type_name: str) -> List[str]:
        model = aqt.mw.col.models.by_name(note_type_name)
        return aqt.mw.col.models.field_names(model)

    def get_deck_list(self) -> List[str]:
        return aqt.mw.col.decks.all_names()