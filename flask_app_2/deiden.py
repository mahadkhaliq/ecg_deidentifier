import os
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from faker import Faker
import random
import base64
import numpy as np

# Initialize Faker
fake = Faker()

# Mindray functions
def extract_patient_info_mindray(root):
    patient_info = {}
    patient_element = root.find('.//Patient')
    if patient_element is not None:
        for child in patient_element:
            patient_info[child.tag] = child.text

    demographics_element = root.find('.//Demographics')
    if demographics_element is not None:
        for child in demographics_element:
            patient_info[child.tag] = child.text
    
    visit_number_element = root.find('.//VisitNumber')
    if visit_number_element is not None:
        patient_info['VisitNumber'] = visit_number_element.text

    return patient_info

def replace_patient_info_mindray(root, new_first_name, new_last_name, new_visit_number):
    patient_element = root.find('.//Patient')
    if patient_element is not None:
        for child in patient_element:
            if 'FirstName' in child.tag:
                child.text = new_first_name
            if 'LastName' in child.tag:
                child.text = new_last_name

    demographics_element = root.find('.//Demographics')
    if demographics_element is not None:
        for child in demographics_element:
            if 'FirstName' in child.tag:
                child.text = new_first_name
            if 'LastName' in child.tag:
                child.text = new_last_name
    
    visit_number_element = root.find('.//VisitNumber')
    if visit_number_element is not None:
        visit_number_element.text = new_visit_number

def extract_waveform_data_mindray(waveform_element):
    data = []
    for segment in waveform_element.findall('.//WaveformSegment'):
        data_text = segment.find('Data').text
        segment_data = list(map(int, data_text.split(',')))
        data.extend(segment_data)
    return data

def process_mindray_file(file_path, output_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    patient_info_before = extract_patient_info_mindray(root)

    random_first_name = fake.first_name()
    random_last_name = fake.last_name()
    random_visit_number = str(random.randint(1000, 9999))

    replace_patient_info_mindray(root, random_first_name, random_last_name, random_visit_number)

    patient_info_after = extract_patient_info_mindray(root)

    print(f"Processed file: {file_path}")
    print("Patient Information Before Replacement:")
    for key, value in patient_info_before.items():
        print(f"{key}: {value}")

    print("\nPatient Information After Replacement:")
    for key, value in patient_info_after.items():
        print(f"{key}: {value}")

    waveform_data = {}
    waveforms = root.findall('.//TwelveLeadReport//Waveform')

    for waveform in waveforms:
        lead_type = waveform.attrib.get('Type')
        if lead_type not in waveform_data:
            waveform_data[lead_type] = []
        waveform_data[lead_type].extend(extract_waveform_data_mindray(waveform))

    for lead_type, data in waveform_data.items():
        print(f"Lead {lead_type}: First 10 samples: {data[:10]}")

    num_leads = len(waveform_data)
    # fig, axs = plt.subplots(num_leads, 1, figsize=(12, num_leads * 3))

    # for i, (lead_type, data) in enumerate(waveform_data.items()):
    #     axs[i].plot(data[:500])
    #     axs[i].set_title(f'ECG Lead {lead_type}')
    #     axs[i].set_xlabel('Sample')
    #     axs[i].set_ylabel('Amplitude (uV)')

    #plt.tight_layout()
    #plt.show()

    # Save the modified XML tree to the output path
    tree.write(output_path)

# Philips functions
def update_patient_info_philips(root, namespace):
    # Find and update name
    name = root.find('.//ns:patient/ns:generalpatientdata/ns:name', namespace)
    if name is not None:
        name.find('ns:lastname', namespace).text = fake.last_name()
        name.find('ns:firstname', namespace).text = fake.first_name()
        name.find('ns:middlename', namespace).text = fake.first_name()
    
    # Find and update bed number
    acquirer = root.find('.//ns:dataacquisition/ns:acquirer', namespace)
    if acquirer is not None:
        acquirer.find('ns:bed', namespace).text = fake.bothify(text='Bed ##')

    # Find and update date of birth
    age = root.find('.//ns:patient/ns:generalpatientdata/ns:age', namespace)
    if age is not None:
        age.find('ns:dateofbirth', namespace).text = fake.date_of_birth(minimum_age=0, maximum_age=100).strftime('%Y-%m-%d')

def process_philips_file(file_path, output_path):
    namespace = {'ns': 'http://www3.medical.philips.com'}
    tree = ET.parse(file_path)
    root = tree.getroot()

    update_patient_info_philips(root, namespace)

    print(f"Processed file: {file_path}")

    # Save the modified XML tree to the output path
    tree.write(output_path)

# Mortara functions
def decode_ecg_data(base64_data):
    decoded_data = base64.b64decode(base64_data)
    return np.frombuffer(decoded_data, dtype=np.int16)

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

def replace_patient_info_mortara(root):
    new_first_name = fake.first_name()
    new_last_name = fake.last_name()
    new_id = fake.uuid4()
    new_dob = fake.date_of_birth().strftime("%Y%m%d")

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

# def plot_ecg_data_mortara(root):
#     channels = root.findall(".//CHANNEL")
#     num_channels = len(channels)

#     print(f"Number of Channels: {num_channels}")

#     fig, axs = plt.subplots(num_channels, 1, figsize=(10, 4 * num_channels))

#     samples = 500  # number of samples to plot

#     for idx, channel in enumerate(channels):
#         lead_name = channel.attrib.get("NAME", "Unknown")
#         print(f"Lead {lead_name}: First {samples} samples: {decode_ecg_data(channel.attrib.get('DATA', ''))[:samples]}")
        
#         base64_data = channel.attrib.get("DATA", "")
#         ecg_data = decode_ecg_data(base64_data) if base64_data else np.array([])
        
#         axs[idx].plot(ecg_data[:samples])
#         axs[idx].set_title(f"Lead: {lead_name}")
#         axs[idx].set_xlabel("Sample Number")
#         axs[idx].set_ylabel("Signal (400 units/mV)")
    
#     plt.tight_layout()
#     plt.show()

def process_mortara_file(file_path, output_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    patient_info_before = extract_patient_info_mortara(root)
    print("Patient Information Before Replacement:")
    print_patient_info(patient_info_before)

    replace_patient_info_mortara(root)

    patient_info_after = extract_patient_info_mortara(root)
    print("\nPatient Information After Replacement:")
    print_patient_info(patient_info_after)

    #plot_ecg_data_mortara(root)

    # Save the modified XML tree to the output path
    tree.write(output_path)

# Utility function to print patient information
def print_patient_info(info):
    for key, value in info.items():
        print(f"{key}: {value}")

# Main function to process files based on the device name
def process_files_in_folder(device_name, input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            file_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            if device_name.lower() == 'mindray':
                process_mindray_file(file_path, output_path)
            elif device_name.lower() == 'philips':
                process_philips_file(file_path, output_path)
            elif device_name.lower() == 'mortara':
                process_mortara_file(file_path, output_path)
            else:
                print(f"Unknown device name: {device_name}")

# Example usage


if __name__=="__main__":

    input_folder = './input'
    output_folder = './output'
    device_name = 'philips'  # Change this to 'mindray', 'philips' or 'mortara' as needed

    process_files_in_folder(device_name, input_folder, output_folder)
