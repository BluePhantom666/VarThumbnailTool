import sys
import os
import matplotlib.pyplot as plt
import math
from PIL import Image
import zipfile
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog, QMessageBox, \
    QLabel, QScrollArea, QCheckBox
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

        # Add a checkbox for creating a montage
        self.imagegrid_box = QCheckBox("Create a montage after the extraction?")
        self.imagegrid_box.setChecked(True)

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
        vbox.addWidget(self.imagegrid_box)
        vbox.addWidget(self.info_label)
        vbox.addWidget(self.extract_button)
        vbox.addWidget(self.scroll_messages)

        self.setLayout(vbox)

    def extract_thumbnail(self, var_file_path, output_dir):
        # Ensure the file is a .var file
        if not var_file_path.endswith('.var'):
            print(f"{var_file_path} is not a .var file.")
            self.message_layout.addWidget(QLabel(f"{var_file_path} is not a .var file", self))
            return None

        # Get the name of the var file without extension
        var_name = os.path.splitext(os.path.basename(var_file_path))[0]
        
        # Extract creator name from the var file name
        creator_name = var_name.split('.')[0]

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
                        new_thumbnail_path = os.path.join(output_dir, f"{var_name}.jpg")

                        # Write the thumbnail to the directory
                        with open(new_thumbnail_path, 'wb') as thumbnail_file:
                            thumbnail_file.write(thumbnail_data)

                        print(f"Thumbnail for {var_name} extracted and saved as: {new_thumbnail_path}")
                        self.message_layout.addWidget(QLabel(f"Thumbnail for {var_name} extracted and saved as: {new_thumbnail_path}", self))
                        return creator_name
                    else:
                        self.message_layout.addWidget(QLabel(f"No thumbnail found for scene {scene_name} in {var_file_path}", self))
                        print(f"No thumbnail found for scene {scene_name} in {var_file_path}.")
            else:
                print(f"No scene files found in {var_file_path}.")
                self.message_layout.addWidget(QLabel(f"No scene files found in {var_file_path}", self))
                self.message_widget.setLayout(self.message_layout)
        
        return None

    def imagegrid(self, output_dir, image_files, creator_name, grid_size=None):
        if not image_files:
            print(f"No images found for creator {creator_name}.")
            self.message_layout.addWidget(QLabel(f"No images found for creator {creator_name}.", self))
            return None

        # Load all images into a list
        list_images = [Image.open(os.path.join(output_dir, img)) for img in image_files]

        # If grid size (rows, cols) is not provided, calculate it automatically
        num_images = len(list_images)
        if grid_size is None:
            # Determine grid size automatically (square-like grid)
            grid_cols = math.ceil(math.sqrt(num_images))  # Number of columns
            grid_rows = math.ceil(num_images / grid_cols)  # Number of rows
        else:
            grid_rows, grid_cols = grid_size

        # Create a matplotlib figure with increased size and DPI
        fig, axs = plt.subplots(grid_rows + 1, grid_cols, figsize=(grid_cols * 4, (grid_rows + 1) * 4), dpi=300)
    
        # Flatten axs array for easy indexing (in case of multiple subplots)
        axs = axs.flatten() if isinstance(axs, np.ndarray) else [axs]

        # Turn off axes for all subplots
        for ax in axs:
            ax.axis('off')
    
        # Add creator name at the top
        fig.suptitle(f"Creator: {creator_name}", fontsize=14, y=0.99)
    
        # Add each image to the grid
        for i, (img, img_file) in enumerate(zip(list_images, image_files)):
            axs[i + grid_cols].imshow(img)  # Start from the second row
            axs[i + grid_cols].set_title(os.path.splitext(img_file)[0], fontsize=8)  # Add thumbnail name
            
        # Remove empty subplots (if any)
        for j in range(i + grid_cols + 1, len(axs)):
            fig.delaxes(axs[j])
    
        # Adjust spacing between images
        plt.subplots_adjust(wspace=0.05, hspace=0.2)
    
        # Save the final grid image with high quality
        grid_path = os.path.join(output_dir, f'grid_{creator_name}.jpg')
        plt.savefig(grid_path, bbox_inches='tight', pad_inches=0.1)
        plt.close()  # Close the figure to free up memory

        print(f"Image grid for {creator_name} created and saved as: {grid_path}")
        self.message_layout.addWidget(QLabel(f"Image grid for {creator_name} created and saved as: {grid_path}", self))
        return grid_path

    def group_thumbnails_by_creator(self, output_dir):
        creator_thumbnails = {}
        for file in os.listdir(output_dir):
            if file.lower().endswith('.jpg') and file != 'grid.jpg':
                creator_name = file.split('.')[0]
                if creator_name not in creator_thumbnails:
                    creator_thumbnails[creator_name] = []
                creator_thumbnails[creator_name].append(file)
        return creator_thumbnails
        
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
        if target:
            if self.current_status == 1:  # Single file processing
                self.extract_thumbnail(self.to_process, target)
            elif self.current_status == 2:  # Directory processing
                self.process_var_files_recursively(self.to_process, target)                
                # Generate image grid only for directory processing and if checkbox is checked
                if self.imagegrid_box.isChecked():
                    creator_thumbnails = self.group_thumbnails_by_creator(target)
                    for creator, thumbnails in creator_thumbnails.items():
                        self.imagegrid(target, thumbnails, creator)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VarExtractor()
    window.show()
    sys.exit(app.exec_())
