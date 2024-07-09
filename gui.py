import sys
import os
import random
import string
import base64
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox, QLabel, QTextEdit

def generate_random_id():
    return ''.join(random.choices(string.ascii_uppercase, k=3)) + ''.join(random.choices(string.digits, k=4))

def generate_random_name():
    names = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "India", "Juliet", "Kilo", "Lima", "Mike", "November", "Oscar", "Papa", "Quebec", "Romeo", "Sierra", "Tango", "Uniform", "Victor", "Whiskey", "X-ray", "Yankee", "Zulu"]
    return random.choice(names)

def decode_base64_data(data):
    return base64.b64decode(data)

def plot_ecg_leads(leads_data, lead_names, samples_per_second, duration=10):
    time_axis = np.linspace(0, duration, samples_per_second * duration)
    num_leads = len(leads_data)
    
    fig, axs = plt.subplots(num_leads, 1, figsize=(12, 2 * num_leads))
    for i in range(num_leads):
        lead_data = leads_data[i][:samples_per_second * duration]
        axs[i].plot(time_axis, lead_data)
        axs[i].set_title(lead_names[i])
        axs[i].set_xlabel('Time (s)')
        axs[i].set_ylabel('mV')
    
    plt.tight_layout()
    plt.show()

def extract_ecg_data_from_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Extract patient ID and name
    patient_id = ""
    patient_name = ""
    for elem in root.iter():
        if elem.tag.endswith('patientid') or elem.tag.endswith('MRN'):
            patient_id = elem.text
        elif elem.tag.endswith('firstname'):
            patient_name = elem.text
        elif elem.tag.endswith('lastname'):
            patient_name += " " + elem.text
    
    waveform_element = root.find(".//{http://www3.medical.philips.com}parsedwaveforms")
    if waveform_element is None:
        raise ValueError("Waveform data not found in the XML file")

    encoded_data = waveform_element.text.strip()
    decoded_data = decode_base64_data(encoded_data)
    
    ecg_data = np.frombuffer(decoded_data, dtype=np.int16) * 5e-3
    
    lead_labels = waveform_element.attrib.get('leadlabels', '').split()
    samples_per_second = int(waveform_element.attrib.get('samplespersecond', 500))  # Defaulting to 500 if not found
    num_leads = int(waveform_element.attrib.get('numberofleads', 12))  # Defaulting to 12 if not found

    leads_data = np.reshape(ecg_data, (-1, num_leads)).T
    
    return leads_data, lead_labels, samples_per_second, patient_id, patient_name

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

        self.loadLabel = QLabel('Select folder containing ECG files:')
        self.layout.addWidget(self.loadLabel)
        
        self.loadButton = QPushButton("Load ECGs (folder)", self)
        self.loadButton.clicked.connect(self.load_folder_dialog)
        self.layout.addWidget(self.loadButton)
        
        self.outputLabel = QLabel('Select folder to save de-identified files:')
        self.layout.addWidget(self.outputLabel)
        
        self.outputButton = QPushButton("Output Location (folder)", self)
        self.outputButton.clicked.connect(self.output_folder_dialog)
        self.layout.addWidget(self.outputButton)
        
        self.saveButton = QPushButton("Save", self)
        self.saveButton.clicked.connect(self.save_files)
        self.layout.addWidget(self.saveButton)
        
        self.visualizeButton = QPushButton("Visualize ECG", self)
        self.visualizeButton.clicked.connect(self.visualize_ecg)
        self.layout.addWidget(self.visualizeButton)
        
        self.infoText = QTextEdit(self)
        self.infoText.setReadOnly(True)
        self.layout.addWidget(self.infoText)
        
        self.setLayout(self.layout)
        self.setWindowTitle('ECG Deidentifier')
        self.setGeometry(100, 100, 600, 400)
        self.show()
        
        self.source_folder = ''
        self.save_folder = ''

    def load_folder_dialog(self):
        self.source_folder = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if self.source_folder:
            self.loadLabel.setText(f"Loaded ECG folder: {self.source_folder}")
    
    def output_folder_dialog(self):
        self.save_folder = QFileDialog.getExistingDirectory(self, "Select Save Folder")
        if self.save_folder:
            self.outputLabel.setText(f"Output folder: {self.save_folder}")
    
    def save_files(self):
        if not self.source_folder or not self.save_folder:
            QMessageBox.warning(self, "Error", "Please select both source and output folders.")
            return
        
        xml_files = [f for f in os.listdir(self.source_folder) if f.endswith('.txt')]
        deidentified_files = []
        
        for xml_file in xml_files:
            full_path = os.path.join(self.source_folder, xml_file)
            new_file_path = deidentify_xml(full_path, self.save_folder)
            deidentified_files.append(new_file_path)
        
        QMessageBox.information(self, "Deidentification Complete", f"Deidentified {len(deidentified_files)} files.")
    
    def visualize_ecg(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open ECG File", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                leads_data, lead_labels, samples_per_second, patient_id, patient_name = extract_ecg_data_from_xml(file_path)
                self.infoText.setPlainText(f"Patient ID: {patient_id}\nPatient Name: {patient_name}")
                plot_ecg_leads(leads_data, lead_labels, samples_per_second)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load and visualize ECG: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DeidentifyApp()
    sys.exit(app.exec_())

