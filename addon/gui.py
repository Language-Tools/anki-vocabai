from PyQt6.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QVBoxLayout, QLineEdit, QRadioButton, QButtonGroup, QHBoxLayout, QMessageBox
from typing import List
import logging
from . import anki_utils
from . import data

logger = logging.getLogger(__name__)

class ConfigureBaserowDialog(QDialog):
    def __init__(self, config: data.BaserowConfig, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Baserow")
        self.username_label = QLabel("Username:")
        self.username_edit = QLineEdit()
        self.username_edit.setText(config.username)
        self.password_label = QLabel("Password:")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setText(config.password)
        self.api_url_label = QLabel("API URL:")
        self.api_url_radio_group = QButtonGroup()
        self.app_vocab_radio = QRadioButton("https://app.vocab.ai")
        self.baserow_io_radio = QRadioButton("https://api.baserow.io")
        self.custom_radio = QRadioButton("Custom:")
        self.custom_edit = QLineEdit()
        self.custom_edit.setEnabled(False)
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self.on_ok_button_clicked)
        self.cancel_button.clicked.connect(self.reject)
        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_edit)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_edit)
        layout.addWidget(self.api_url_label)
        layout.addWidget(self.app_vocab_radio)
        layout.addWidget(self.baserow_io_radio)
        layout.addWidget(self.custom_radio)
        layout.addWidget(self.custom_edit)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        # set up radio button group
        self.api_url_radio_group.addButton(self.app_vocab_radio)
        self.api_url_radio_group.addButton(self.baserow_io_radio)
        self.api_url_radio_group.addButton(self.custom_radio)
        self.app_vocab_radio.setChecked(config.api_base_url == data.API_URL_VOCABAI)
        self.baserow_io_radio.setChecked(config.api_base_url == data.API_URL_BASEROW)
        if config.api_base_url not in [data.API_URL_VOCABAI, data.API_URL_BASEROW]:
            self.custom_radio.setChecked(True)
            self.custom_edit.setText(config.api_base_url)
            self.custom_edit.setEnabled(True)

        # connect signals
        self.app_vocab_radio.toggled.connect(self.api_url_radio_toggled)
        self.baserow_io_radio.toggled.connect(self.api_url_radio_toggled)
        self.custom_radio.toggled.connect(self.api_url_radio_toggled)

    def on_ok_button_clicked(self):
        try:
            self.validate_config()
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Validation Error", str(e))

    def api_url_radio_toggled(self, checked):
        if checked:
            if self.app_vocab_radio.isChecked():
                self.custom_edit.setEnabled(False)
            elif self.baserow_io_radio.isChecked():
                self.custom_edit.setEnabled(False)
            elif self.custom_radio.isChecked():
                self.custom_edit.setEnabled(True)

    def validate_config(self):
        self.config.validate()

    @property
    def config(self) -> data.BaserowConfig:
        config = data.BaserowConfig()
        config.username = self.username_edit.text()
        config.password = self.password_edit.text()
        if self.app_vocab_radio.isChecked():
            config.api_base_url = data.API_URL_VOCABAI
        elif self.baserow_io_radio.isChecked():
            config.api_base_url = data.API_URL_BASEROW  
        elif self.custom_radio.isChecked():
            config.api_base_url = self.custom_edit.text()
        return config



class ConfigureTableImportDialog(QDialog):
    UNMAPPED_FIELD_NAME = '(Unmapped)'

    def __init__(self, model: data.TableImportConfig, csv_field_names: List[str], anki_utils, parent=None):
        super().__init__(parent)
        self.csv_field_names = csv_field_names
        self.all_field_names = [self.UNMAPPED_FIELD_NAME] + csv_field_names
        self.anki_utils = anki_utils
        self.setWindowTitle("Anki Import")
        self.note_type_label = QLabel("Note Type:")
        self.note_type_combo = QComboBox()
        self.deck_label = QLabel("Deck:")
        self.deck_combo = QComboBox()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        layout = QVBoxLayout()
        layout.addWidget(self.note_type_label)
        layout.addWidget(self.note_type_combo)
        layout.addWidget(self.deck_label)
        layout.addWidget(self.deck_combo)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)

        # add layout for field mappings
        self.field_mappings_layout = QVBoxLayout()
        layout.addLayout(self.field_mappings_layout)
        
        self.setLayout(layout)
        self.populate_note_type_combo()
        self.populate_deck_combo()

        # populate controls based on model  
        self.load_model(model)

        self.note_type_combo.currentIndexChanged.connect(self.note_type_selected)
        self.deck_combo.currentIndexChanged.connect(self.deck_selected)

    def load_model(self, model: data.TableImportConfig):
        self.model = model

        # configure controls based on model
        if model.note_type_name != None:
            self.note_type_combo.setCurrentText(model.note_type_name)
        # make sure that callback fires, to update the model
        self.note_type_selected()

        if model.deck_name != None:
            self.deck_combo.setCurrentText(model.deck_name)
        # make sure to fire callbacks, to update model
        self.deck_selected()


    def populate_note_type_combo(self):
        note_types = self.anki_utils.get_note_type_list()
        self.note_type_combo.addItems(note_types)

    def populate_deck_combo(self):
        decks = self.anki_utils.get_deck_list()
        self.deck_combo.addItems(decks)

    def note_type_selected(self):
        logger.debug("note_type_selected")
        note_type = self.note_type_combo.currentText()
        self.model.note_type_name = note_type
        self.note_type_fields = self.anki_utils.get_field_list_for_note_type(note_type)
        # clear all widgets from the self.field_mappings_layout layout
        for i in reversed(range(self.field_mappings_layout.count())):
            self.field_mappings_layout.itemAt(i).widget().setParent(None)
        # for each field in self.note_type_fields, add a combo box populated with self.csv_field_names
        for field in self.note_type_fields:
            label = QLabel(field)
            combo = QComboBox()
            combo.setObjectName(field)
            combo.addItems(self.all_field_names)
            if field in self.model.field_mapping:
                mapped_csv_field_name = self.model.field_mapping[field]
                if mapped_csv_field_name in self.csv_field_names:
                    combo.setCurrentText(mapped_csv_field_name)
            self.field_mappings_layout.addWidget(label)
            self.field_mappings_layout.addWidget(combo)
            # when the combo box is changed, call a lambda function which contains field
            # this will capture the current value of field in the lambda function
            combo.currentTextChanged.connect(self.get_field_mapping_text_changed_lambda(field, combo))


    def deck_selected(self):
        deck_name = self.deck_combo.currentText()
        self.model.deck_name = deck_name

    def get_field_mapping_text_changed_lambda(self, anki_field_name: str, combo: QComboBox):
        def current_text_changed(csv_field_name: str):
            if csv_field_name == self.UNMAPPED_FIELD_NAME:
                if anki_field_name in self.model.field_mapping:
                    del self.model.field_mapping[anki_field_name]
            else:
                self.model.field_mapping[anki_field_name] = csv_field_name
        return current_text_changed

    
def display_table_import_dialog(model: data.TableImportConfig, csv_field_names: List[str], parent=None) -> data.TableImportConfig:
    dialog = ConfigureTableImportDialog(model, csv_field_names, parent)
    result = dialog.exec_()
    if result == QDialog.DialogCode.Accepted:
        return dialog.model
    else:
        return None


def display_baserow_config_dialog(config: data.BaserowConfig, parent=None) -> data.BaserowConfig:
    dialog = ConfigureBaserowDialog(config, parent)
    result = dialog.exec()
    if result == QDialog.DialogCode.Accepted:
        return dialog.config
    else:
        return None