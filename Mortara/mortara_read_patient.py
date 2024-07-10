"""
author: mahad

this script reads the data, then deidentifies the information and also visualizes the matplotlib graphs
"""

import base64
import numpy as np
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
from faker import Faker

# Initialize the Faker library
faker = Faker()

# Read the Mortara file
file_path = "./ABC1234_2010-01-05_22-17-59 Mortara file.txt"
tree = ET.parse(file_path)
root = tree.getroot()

# Function to decode ECG data
def decode_ecg_data(base64_data):
    decoded_data = base64.b64decode(base64_data)
    return np.frombuffer(decoded_data, dtype=np.int16)

# Extract patient information
def extract_patient_info_mortara(root):
    demographic_fields = root.find(".//DEMOGRAPHIC_FIELDS")
    patient_info = {}
    if demographic_fields:
        for field in demographic_fields.findall("DEMOGRAPHIC_FIELD"):
            id_tag = field.get('_ID')
            value_tag = field.get('_VALUE')
            patient_info[id_tag] = value_tag
    
    subject = root.find(".//SUBJECT")
    if subject is not None:
        patient_info["LAST_NAME"] = subject.get("LAST_NAME")
        patient_info["FIRST_NAME"] = subject.get("FIRST_NAME")
        patient_info["ID"] = subject.get("ID")
        patient_info["DOB"] = subject.get("DOB")
    
    return patient_info

# Replace patient information with random data
def replace_patient_info(root):
    new_first_name = faker.first_name()
    new_last_name = faker.last_name()
    new_id = faker.uuid4()
    new_dob = faker.date_of_birth().strftime("%Y%m%d")

    demographic_fields = root.find(".//DEMOGRAPHIC_FIELDS")
    if demographic_fields:
        for field in demographic_fields.findall("DEMOGRAPHIC_FIELD"):
            id_tag = field.get('_ID')
            if id_tag == "1":  # Last Name
                field.set('_VALUE', new_last_name)
            elif id_tag == "7":  # First Name
                field.set('_VALUE', new_first_name)
            elif id_tag == "2":  # Patient ID
                field.set('_VALUE', new_id)
            elif id_tag == "16":  # Date of Birth
                field.set('_VALUE', new_dob)
    
    subject = root.find(".//SUBJECT")
    if subject is not None:
        subject.set("LAST_NAME", new_last_name)
        subject.set("FIRST_NAME", new_first_name)
        subject.set("ID", new_id)
        subject.set("DOB", new_dob)

# Print patient information
def print_patient_info(info):
    for key, value in info.items():
        print(f"{key}: {value}")

# Plot the ECG data
def plot_ecg_data(root):
    channels = root.findall(".//CHANNEL")
    num_channels = len(channels)

    print(f"Number of Channels: {num_channels}")

    fig, axs = plt.subplots(num_channels, 1, figsize=(10, 4 * num_channels))

    samples = 10  # number of samples to plot

    for idx, channel in enumerate(channels):
        lead_name = channel.attrib.get("NAME", "Unknown")
        print(f"Lead {lead_name}: First {samples} samples: {decode_ecg_data(channel.attrib.get('DATA', ''))[:samples]}")
        
        base64_data = channel.attrib.get("DATA", "")
        ecg_data = decode_ecg_data(base64_data) if base64_data else np.array([])
        
        axs[idx].plot(ecg_data[:samples])
        axs[idx].set_title(f"Lead: {lead_name}")
        axs[idx].set_xlabel("Sample Number")
        axs[idx].set_ylabel("Signal (400 units/mV)")
    
    plt.tight_layout()
    plt.show()

# Extract and print patient information before replacement
patient_info_before = extract_patient_info_mortara(root)
print("Patient Information Before Replacement:")
print_patient_info(patient_info_before)

# Replace patient information
replace_patient_info(root)
    
# Extract and print patient information after replacement
patient_info_after = extract_patient_info_mortara(root)
print("\nPatient Information After Replacement:")
print_patient_info(patient_info_after)

# Plot ECG data
plot_ecg_data(root)
