import sys
import os
import zipfile
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog, QMessageBox, \
    QLabel, QScrollArea
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

btn_style = """
        QPushButton {
            background-color: #24a0ed;
            color: white;
            border-radius: 10px;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #0ba6ff;
        }
        QPushButton:pressed {
            background-color: #389bd9;
        }
    """

btn_extract_style = """
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border-radius: 10px;
            padding: 10px;
            font-size: 40px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #388E3C;
        }
    """


class VarExtractor(QWidget):
    def __init__(self):
        super().__init__()
        self.current_status = 0
        self.to_process = ''

        # Set the window properties
        self.setWindowTitle('VAR THUMBNAIL TOOL')
        self.setGeometry(100, 100, 900, 500)
        self.setStyleSheet("background-color: #f0f0f0;")

        # Create buttons
        self.dir_button = QPushButton('Choose Directory', self)
        self.file_button = QPushButton('Choose .var File', self)
        self.extract_button = QPushButton('Extract', self)

        # Create label
        self.info_label = QLabel('Select a directory or a file', self)
        self.info_label.setAlignment(Qt.AlignHCenter)

        self.scroll_messages = QScrollArea(self)
        self.scroll_messages.setWidgetResizable(True)

        self.message_widget = QWidget()
        self.message_layout = QVBoxLayout(self.message_widget)
        self.message_widget.setStyleSheet('color: f0ad4e;')

        self.scroll_messages.setWidget(self.message_widget)

        self.info_label.setFont(QFont("Arial", 10))
        self.info_label.setStyleSheet("color: #333; margin: 40px;")

        # Set modern style and font for buttons
        self.dir_button.setStyleSheet(btn_style)
        self.file_button.setStyleSheet(btn_style)
        self.extract_button.setStyleSheet(btn_extract_style)

        self.dir_button.setFont(QFont("Arial", 12))
        self.file_button.setFont(QFont("Arial", 12))

        # Connect button actions
        self.dir_button.clicked.connect(self.choose_directory)
        self.file_button.clicked.connect(self.choose_var_file)
        self.extract_button.clicked.connect(self.extract)

        # Horizontal layout for buttons
        hbox = QHBoxLayout()
        hbox.addWidget(self.dir_button)
        hbox.addWidget(self.file_button)

        # Vertical layout to include buttons and label
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.info_label)
        vbox.addWidget(self.extract_button)
        vbox.addWidget(self.scroll_messages)

        self.setLayout(vbox)

    def extract_thumbnail(self, var_file_path, output_dir):
        # Ensure the file is a .var file
        if not var_file_path.endswith('.var'):
            print(f"{var_file_path} is not a .var file.")
            self.message_layout.addWidget(QLabel(f"{var_file_path} is not a .var file", self))
            return

        # Get the name of the var file without extension
        var_name = os.path.splitext(os.path.basename(var_file_path))[0]

        # Open the var file (zip archive)
        with zipfile.ZipFile(var_file_path, 'r') as var_file:
            # Check for the presence of the Saves\Scenes\ scene files and thumbnail
            scene_files = [f for f in var_file.namelist() if f.startswith('Saves/scene/') and f.endswith('.json')]

            if scene_files:
                for scene_file in scene_files:
                    # Derive the base name of the scene file (without extension)
                    scene_name = os.path.splitext(os.path.basename(scene_file))[0]

                    # The expected thumbnail path
                    thumbnail_path = f"Saves/scene/{scene_name}.jpg"

                    if thumbnail_path in var_file.namelist():
                        # Extract the thumbnail
                        thumbnail_data = var_file.read(thumbnail_path)

                        # Create the output directory if it doesn't exist
                        os.makedirs(output_dir, exist_ok=True)

                        # Create the new thumbnail file path in the output directory
                        new_thumbnail_path = os.path.join(output_dir, f"{scene_name}.jpg")

                        # Write the thumbnail to the directory
                        with open(new_thumbnail_path, 'wb') as thumbnail_file:
                            thumbnail_file.write(thumbnail_data)

                        print(f"Thumbnail for {scene_name} extracted and saved as: {new_thumbnail_path}")
                        self.message_layout.addWidget(QLabel(f"Thumbnail for {scene_name} extracted and saved as: {new_thumbnail_path}", self))
                    else:
                        self.message_layout.addWidget(QLabel(f"No thumbnail found for scene {scene_name} in {var_file_path}", self))
                        print(f"No thumbnail found for scene {scene_name} in {var_file_path}.")
            else:
                print(f"No scene files found in {var_file_path}.")
                self.message_layout.addWidget(QLabel(f"No scene files found in {var_file_path}", self))
                self.message_widget.setLayout(self.message_layout)

    def process_var_files_recursively(self, directory_path, output_dir):
        # Walk through the directory and its subdirectories
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                # Process only .var files
                if file.endswith('.var'):
                    var_file_path = os.path.join(root, file)
                    print(f"Processing file: {var_file_path}")
                    self.extract_thumbnail(var_file_path, output_dir)

    def choose_directory_(self, message):
        dir_name = QFileDialog.getExistingDirectory(self, message)
        if dir_name:
            return dir_name

    def choose_directory(self):
        directory = self.choose_directory_('Select Directory')
        if directory is not None:
            self.info_label.setText(f'Selected Directory: {directory}')
            self.current_status = 2
            self.to_process = directory



    def choose_var_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Select .var File', '', 'VAR Files (*.var)')
        if file_name:
            self.info_label.setText(f'Selected File: {file_name}')
            self.current_status = 1
            self.to_process = file_name


    def extract(self):
        target = self.choose_directory_('Choose where to extract')
        if self.current_status == 1:
            self.extract_thumbnail(self.to_process, target)
        elif self.current_status == 2:
            self.process_var_files_recursively(self.to_process, target)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VarExtractor()
    window.show()
    sys.exit(app.exec_())
