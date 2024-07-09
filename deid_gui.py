import sys
import os
import random
import string
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox

def generate_random_id():
    return ''.join(random.choices(string.ascii_uppercase, k=3)) + ''.join(random.choices(string.digits, k=4))

def generate_random_name():
    names = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "India", "Juliet", "Kilo", "Lima", "Mike", "November", "Oscar", "Papa", "Quebec", "Romeo", "Sierra", "Tango", "Uniform", "Victor", "Whiskey", "X-ray", "Yankee", "Zulu"]
    return random.choice(names)

def deidentify_xml(file_path, save_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Replace filename
    new_filename = generate_random_id() + " file.txt"
    new_file_path = os.path.join(save_path, new_filename)
    
    # Replace patient ID and name
    for elem in root.iter():
        if elem.tag.endswith('patientid') or elem.tag.endswith('MRN'):
            elem.text = generate_random_id()
        elif elem.tag.endswith('firstname'):
            elem.text = generate_random_name()
        elif elem.tag.endswith('lastname'):
            elem.text = generate_random_name()
        elif elem.tag.endswith('documentname'):
            elem.text = new_filename

    tree.write(new_file_path)
    return new_file_path

class DeidentifyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.layout = QVBoxLayout()
        
        self.browseButton = QPushButton("Browse Folder", self)
        self.browseButton.clicked.connect(self.showFolderDialog)
        self.layout.addWidget(self.browseButton)
        
        self.setLayout(self.layout)
        self.setWindowTitle('ECG Deidentifier')
        self.show()
    
    def showFolderDialog(self):
        source_folder = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if source_folder:
            save_folder = QFileDialog.getExistingDirectory(self, "Select Save Folder")
            if save_folder:
                self.deidentify_files_in_folder(source_folder, save_folder)
    
    def deidentify_files_in_folder(self, source_folder, save_folder):
        xml_files = [f for f in os.listdir(source_folder) if f.endswith('.txt')]
        deidentified_files = []
        
        for xml_file in xml_files:
            full_path = os.path.join(source_folder, xml_file)
            new_file_path = deidentify_xml(full_path, save_folder)
            deidentified_files.append(new_file_path)
        
        QMessageBox.information(self, "Deidentification Complete", f"Deidentified {len(deidentified_files)} files.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DeidentifyApp()
    sys.exit(app.exec_())

