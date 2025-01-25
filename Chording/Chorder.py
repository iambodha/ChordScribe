import sys
import json
import os
import logging
import locale
import platform
import time
from typing import Dict, List, Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget,
    QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QHBoxLayout,
    QComboBox, QInputDialog, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt
from pynput import keyboard
from pynput.keyboard import Key
import pyautogui

from platform_specific import TextInputFactory

# Configure application-wide logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class KeyboardLayoutManager:
    """
    Handles keyboard layout specifics and character mapping based on the system's locale.
    Supports QWERTY and QWERTZ layouts with special character mappings.
    """
    
    def __init__(self):
        # Determine keyboard layout based on system locale
        self.layout = "QWERTZ" if locale.getdefaultlocale()[0].startswith('de') else "QWERTY"
        self.logger = logging.getLogger('chord_expander')
        
        # Define layout-specific character mappings
        self.special_mappings = {
            "QWERTZ": {
                'z': 'y',
                'y': 'z',
                "'": '#'  # German keyboard mapping
            }
        }

    def get_char(self, key: keyboard.Key) -> str:
        """
        Converts a keyboard key event to its corresponding character based on the current layout.
        
        Args:
            key: The keyboard key event to process
            
        Returns:
            str: The corresponding character or empty string for non-character keys
        """
        try:
            # Handle regular character keys
            if hasattr(key, 'char') and key.char:
                if self.layout in self.special_mappings:
                    return self.special_mappings[self.layout].get(key.char, key.char)
                return key.char
            
            # Handle special keys
            special_keys = {
                Key.space: ' ',
                Key.enter: '\n'
            }
            return special_keys.get(key, '')
            
        except Exception as e:
            self.logger.error(f"Character conversion error: {e}")
            return ''

class KeyboardController:
    """
    Core controller managing text expansion functionality, profile handling,
    and keyboard event processing.
    """
    
    PROFILES_FILE = 'chord_expander_profiles.json'
    DEFAULT_PROFILES = {
        "Default": {
            "btw": "by the way",
            "idk": "I don't know",
            "omw": "on my way"
        },
        "Developer": {
            "cls": "class",
            "fn": "function",
            "ret": "return",
            "imp": "import",
            "pr": "print"
        },
        "Medical": {
            "pt": "patient",
            "rx": "prescription",
            "dx": "diagnosis",
            "tx": "treatment",
            "hx": "history"
        },
        "Legal": {
            "def": "defendant",
            "plt": "plaintiff",
            "jdg": "judgment",
            "crt": "court",
            "att": "attorney"
        },
        "Student": {
            "asap": "as soon as possible",
            "tba": "to be announced",
            "tbd": "to be determined",
            "eg": "for example",
            "ie": "that is"
        }
    }
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.current_word = ""
        self.layout_manager = KeyboardLayoutManager()
        self.input_language = "English"
        self.current_profile = "Default"
        self.profiles = self._load_profiles()
        self.shortcuts = self.profiles[self.current_profile]
        self.keyboard_listener = None
        self.text_input = TextInputFactory.get_text_input()

    def _setup_logger(self) -> logging.Logger:
        """Configures and returns a logger instance for the controller."""
        logger = logging.getLogger('chord_expander')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def _load_profiles(self) -> Dict[str, Dict[str, str]]:
        """
        Loads chord profiles from file or creates default profiles if none exist.
        
        Returns:
            Dict containing profile names mapped to their chords
        """
        if os.path.exists(self.PROFILES_FILE):
            try:
                with open(self.PROFILES_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Profile loading failed: {e}")

        self._save_profiles_to_file(self.DEFAULT_PROFILES)
        return self.DEFAULT_PROFILES.copy()

    def _save_profiles_to_file(self, profiles: Dict[str, Dict[str, str]]) -> None:
        """
        Saves profiles to a JSON file with error handling.
        
        Args:
            profiles: Dictionary of profiles to save
        """
        try:
            with open(self.PROFILES_FILE, 'w') as f:
                json.dump(profiles, f, indent=4)
            self.logger.info("Profiles saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save profiles: {e}")

    def start(self) -> None:
        """Starts the keyboard listener for text expansion."""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        self.keyboard_listener.start()
        self.logger.info(f"Keyboard listener started with {self.layout_manager.layout} layout")

    def stop(self) -> None:
        """Stops the keyboard listener."""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
            self.logger.info("Keyboard listener stopped")

    def on_press(self, key: keyboard.Key) -> None:
        """
        Handles keyboard press events for text expansion.
        
        Args:
            key: The keyboard key that was pressed
        """
        try:
            if key == Key.space:
                if self.current_word.lower() in self.profiles[self.current_profile]:
                    self.check_and_expand()
                self.current_word = ""
                return

            if hasattr(key, 'char') and key.char:
                if key.char.isalnum():
                    self.current_word += key.char
        except Exception as e:
            self.logger.error(f"Error processing keypress: {e}")

    def check_and_expand(self) -> None:
        """Checks if current word should be expanded and performs the expansion."""
        if not self.current_word:
            return

        try:
            expansion = self.profiles[self.current_profile].get(self.current_word.lower())
            if not expansion:
                return

            # Handle QWERTZ mapping if needed
            if self.layout_manager.layout == "QWERTZ":
                expansion = self._apply_qwertz_mapping(expansion)

            # Delete original text and insert expansion
            self.text_input.delete_chars(len(self.current_word) + 1)
            self.text_input.insert_text(expansion + " ")
                
        except Exception as e:
            self.logger.error(f"Expansion error: {e}")

    def _apply_qwertz_mapping(self, text: str) -> str:
        """
        Applies QWERTZ keyboard layout mapping to the given text.
        
        Args:
            text: Text to convert
            
        Returns:
            Converted text with QWERTZ mappings applied
        """
        modified_text = ""
        for char in text:
            if char.lower() == 'y':
                modified_text += 'z' if char.islower() else 'Z'
            elif char.lower() == 'z':
                modified_text += 'y' if char.islower() else 'Y'
            elif char == "'":
                modified_text += "#"
            else:
                modified_text += char
        return modified_text

    def create_profile(self, profile_name: str) -> None:
        """
        Creates a new empty profile.
        
        Args:
            profile_name: Name of the new profile
        """
        profile_name = profile_name.strip()
        if profile_name.lower() not in [p.lower() for p in self.profiles.keys()]:
            self.profiles[profile_name] = {}
            self.current_profile = profile_name
            self.shortcuts = self.profiles[profile_name]
            self._save_profiles_to_file(self.profiles)
            self.logger.info(f"Created profile: {profile_name}")

    def switch_profile(self, profile_name: str) -> None:
        """
        Switches to a different profile.
        
        Args:
            profile_name: Name of the profile to switch to
        """
        profile_name = profile_name.strip()
        profile_dict = {k.lower(): k for k in self.profiles.keys()}
        if profile_name.lower() in profile_dict:
            actual_name = profile_dict[profile_name.lower()]
            self.set_profile(actual_name)
        else:
            self.logger.error(f"Profile not found: {profile_name}")
            self.set_profile("Default")

    def set_profile(self, profile_name: str) -> None:
        """
        Sets the active profile.
        
        Args:
            profile_name: Name of the profile to set as active
        """
        if profile_name in self.profiles:
            self.current_profile = profile_name
            self.shortcuts = self.profiles[profile_name]
            self.logger.info(f"Activated profile: {profile_name}")

    def get_profiles(self) -> List[str]:
        """
        Returns a list of available profile names.
        
        Returns:
            List of profile names
        """
        return list(self.profiles.keys())

    def delete_profile(self, profile_name: str) -> None:
        """
        Deletes a profile.
        
        Args:
            profile_name: Name of the profile to delete
        """
        if profile_name in self.profiles:
            del self.profiles[profile_name]
            self.current_profile = "Default"
            self.shortcuts = self.profiles[self.current_profile]
            self._save_profiles_to_file(self.profiles)
            self.logger.info(f"Deleted profile: {profile_name}")

class MainWindow(QMainWindow):
    """Main application window for the Chord Expander - a text expansion utility."""
    
    def __init__(self, chord_controller: KeyboardController):
        super().__init__()
        self.chord_controller = chord_controller
        self.init_ui()

    def init_ui(self) -> None:
        """Initializes the modern, user-friendly interface."""
        self.setWindowTitle("Chord Expander - Type Smarter, Not Harder")
        self.setGeometry(100, 100, 1000, 700)
        self._setup_styles()
        self._create_layout()

    def _setup_styles(self) -> None:
        """Configures a modern, clean stylesheet for the application."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QLabel {
                font-size: 14px;
                color: #212529;
                margin: 5px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel#HeaderLabel {
                font-size: 24px;
                color: #1a73e8;
                font-weight: bold;
                margin: 15px 0;
            }
            QLabel#StatusLabel {
                font-size: 14px;
                color: #28a745;
                font-weight: bold;
                padding: 8px;
                background: #e8f5e9;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                margin: 5px;
                font-weight: 500;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
            QPushButton#DeleteButton {
                background-color: #dc3545;
            }
            QPushButton#DeleteButton:hover {
                background-color: #c82333;
            }
            QComboBox {
                padding: 8px;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background: white;
                min-width: 200px;
                font-size: 14px;
            }
            QComboBox:hover {
                border-color: #1a73e8;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                margin: 5px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #1a73e8;
            }
            QTableWidget {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background: white;
                gridline-color: #e9ecef;
                selection-background-color: #e8f0fe;
                selection-color: #1a73e8;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e9ecef;
            }
            QTableWidget::item:selected {
                background-color: #e8f0fe;
                color: #1a73e8;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                font-weight: bold;
                color: #495057;
            }
            QScrollBar:vertical {
                border: none;
                background: #f8f9fa;
                width: 10px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #adb5bd;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #6c757d;
            }
        """)

    def _create_layout(self) -> None:
        """Creates a modern, organized layout with clear visual hierarchy."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Header section
        header_label = QLabel("Chord Expander")
        header_label.setObjectName("HeaderLabel")
        main_layout.addWidget(header_label)

        # Status indicator
        self.status_label = QLabel("Chord Expander is actively listening...")
        self.status_label.setObjectName("StatusLabel")
        main_layout.addWidget(self.status_label)

        # Controls section
        controls_container = QWidget()
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setSpacing(20)
        
        # Profile section
        profile_group = self._create_profile_section()
        controls_layout.addLayout(profile_group)
        
        # Language section
        language_group = self._create_language_section()
        controls_layout.addLayout(language_group)
        
        main_layout.addWidget(controls_container)

        # Add chord section
        main_layout.addLayout(self._create_chord_input_section())

        # Table section with search
        main_layout.addLayout(self._create_table_section())

        # Set main layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def _create_profile_section(self) -> QVBoxLayout:
        """Creates an enhanced profile selection section."""
        profile_group = QVBoxLayout()
        
        profile_header = QHBoxLayout()
        profile_label = QLabel("Active Profile")
        profile_label.setStyleSheet("font-weight: bold;")
        
        add_profile_btn = QPushButton("+")
        add_profile_btn.setFixedWidth(40)
        add_profile_btn.clicked.connect(self.add_new_profile)
        
        profile_header.addWidget(profile_label)
        profile_header.addWidget(add_profile_btn)
        
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(self.chord_controller.get_profiles())
        self.profile_combo.setCurrentText(self.chord_controller.current_profile)
        self.profile_combo.currentTextChanged.connect(self.on_profile_changed)
        
        profile_group.addLayout(profile_header)
        profile_group.addWidget(self.profile_combo)
        
        return profile_group

    def _create_language_section(self) -> QVBoxLayout:
        """Creates the language selection section."""
        language_group = QVBoxLayout()
        language_label = QLabel("Input Language:")
        language_label.setStyleSheet("font-weight: bold;")
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "German"])
        self.language_combo.setCurrentText(self.chord_controller.input_language)
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        
        language_group.addWidget(language_label)
        language_group.addWidget(self.language_combo)
        
        return language_group

    def _create_chord_input_section(self) -> QVBoxLayout:
        """Creates an enhanced chord input section with validation."""
        input_layout = QVBoxLayout()
        
        # Section header
        input_header = QLabel("Add New Chord")
        input_header.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        input_layout.addWidget(input_header)

        # Input fields container
        fields_layout = QHBoxLayout()
        
        # Chord input
        chord_group = QVBoxLayout()
        chord_label = QLabel("Chord:")
        self.chord_input = QLineEdit()
        self.chord_input.setPlaceholderText("e.g., 'btw'")
        chord_group.addWidget(chord_label)
        chord_group.addWidget(self.chord_input)
        
        # Expansion input
        expansion_group = QVBoxLayout()
        expansion_label = QLabel("Expansion:")
        self.expansion_input = QLineEdit()
        self.expansion_input.setPlaceholderText("e.g., 'by the way'")
        expansion_group.addWidget(expansion_label)
        expansion_group.addWidget(self.expansion_input)
        
        # Add button
        button_group = QVBoxLayout()
        button_group.addSpacing(24)  # Align with input fields
        add_button = QPushButton("Add Chord")
        add_button.clicked.connect(self.add_chord)
        button_group.addWidget(add_button)
        
        fields_layout.addLayout(chord_group)
        fields_layout.addLayout(expansion_group)
        fields_layout.addLayout(button_group)
        
        input_layout.addLayout(fields_layout)
        
        return input_layout

    def _create_table_section(self) -> QVBoxLayout:
        """Creates an enhanced table section with search functionality."""
        table_layout = QVBoxLayout()
        
        # Table header with search
        header_layout = QHBoxLayout()
        table_label = QLabel("Available Chords")
        table_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search chords...")
        self.search_input.setMaximumWidth(300)
        self.search_input.textChanged.connect(self.filter_table)
        
        header_layout.addWidget(table_label)
        header_layout.addStretch()
        header_layout.addWidget(self.search_input)
        
        table_layout.addLayout(header_layout)
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Chord", "Expansion"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.update_table()
        
        table_layout.addWidget(self.table)
        
        # Add delete button
        delete_button = QPushButton("Delete Selected")
        delete_button.setObjectName("DeleteButton")
        delete_button.clicked.connect(self.delete_selected_chord)
        table_layout.addWidget(delete_button)
        
        return table_layout

    def filter_table(self, search_text: str) -> None:
        """Filters the table based on search input."""
        search_text = search_text.lower()
        for row in range(self.table.rowCount()):
            chord = self.table.item(row, 0).text().lower()
            expansion = self.table.item(row, 1).text().lower()
            matches = search_text in chord or search_text in expansion
            self.table.setRowHidden(row, not matches)

    def add_new_profile(self) -> None:
        """Prompts user to create a new profile."""
        name, ok = QInputDialog.getText(self, "New Profile", "Enter profile name:")
        if ok and name:
            self.chord_controller.create_profile(name)
            self.update_profiles()

    def delete_selected_chord(self) -> None:
        """Deletes the selected chord from the current profile."""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            return
            
        chord = self.table.item(selected_rows[0].row(), 0).text()
        current_profile = self.chord_controller.current_profile
        
        if chord in self.chord_controller.profiles[current_profile]:
            del self.chord_controller.profiles[current_profile][chord]
            self.chord_controller._save_profiles_to_file(self.chord_controller.profiles)
            self.update_table()

    def add_chord(self) -> None:
        """Adds a new chord-expansion pair to the current profile."""
        chord = self.chord_input.text().strip()
        expansion = self.expansion_input.text().strip()
        
        if chord and expansion:
            current_profile = self.chord_controller.current_profile
            self.chord_controller.profiles[current_profile][chord] = expansion
            self.chord_controller._save_profiles_to_file(self.chord_controller.profiles)
            
            # Update UI
            self.update_table()
            self.chord_input.clear()
            self.expansion_input.clear()

    def on_profile_changed(self, profile_name: str) -> None:
        """Handles profile selection changes."""
        self.chord_controller.switch_profile(profile_name)
        self.update_table()

    def on_language_changed(self, new_language: str) -> None:
        """Handles language selection changes."""
        self.chord_controller.input_language = new_language
        self.chord_controller.logger.info(f"Input language changed to: {new_language}")

    def update_profiles(self) -> None:
        """Updates the profile dropdown with current available profiles."""
        self.profile_combo.clear()
        profiles = self.chord_controller.get_profiles()
        self.profile_combo.addItems(profiles)
        self.profile_combo.setCurrentText(self.chord_controller.current_profile)

    def update_table(self) -> None:
        """Updates the shortcuts table with current profile's chords."""
        current_profile = self.chord_controller.current_profile
        chords = self.chord_controller.profiles[current_profile]
        self.table.setRowCount(len(chords))
        
        for i, (chord, expansion) in enumerate(chords.items()):
            self.table.setItem(i, 0, QTableWidgetItem(chord))
            self.table.setItem(i, 1, QTableWidgetItem(expansion))
        
        self.table.resizeColumnsToContents()

def main():
    """Main entry point for the Chord Expander application."""
    try:
        app = QApplication(sys.argv)
        controller = KeyboardController()
        window = MainWindow(controller)
        window.show()
        controller.start()
        sys.exit(app.exec_())
    except Exception as e:
        logging.error(f"Fatal error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
