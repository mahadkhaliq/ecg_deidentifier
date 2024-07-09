import base64
import matplotlib.pyplot as plt
import numpy as np
from xml.etree import ElementTree as ET

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

    # Debugging: Print XML structure and elements
    print("Root tag:", root.tag)
    for elem in root.iter():
        print(f"Tag: {elem.tag}, Attributes: {elem.attrib}")
    
    # Adjust the path to locate the waveform data
    waveform_element = root.find(".//{http://www3.medical.philips.com}parsedwaveforms")
    if waveform_element is None:
        raise ValueError("Waveform data not found in the XML file")

    encoded_data = waveform_element.text.strip()
    
    # Debugging: Print base64 encoded data size
    print(f"Base64 encoded data size: {len(encoded_data)}")
    
    decoded_data = decode_base64_data(encoded_data)
    
    # Debugging: Print decoded data size
    print(f"Decoded data size: {len(decoded_data)}")
    
    # Assuming 16-bit signed integers with a resolution of 5 µV/LSB (as mentioned in the Philips file)
    ecg_data = np.frombuffer(decoded_data, dtype=np.int16) * 5e-3
    
    lead_labels = waveform_element.attrib.get('leadlabels', '').split()
    samples_per_second = int(waveform_element.attrib.get('samplespersecond', 500))  # Defaulting to 500 if not found
    num_leads = int(waveform_element.attrib.get('numberofleads', 12))  # Defaulting to 12 if not found

    # Debugging: Print reshaping information
    print(f"Number of leads: {num_leads}, Samples per second: {samples_per_second}")

    try:
        leads_data = np.reshape(ecg_data, (-1, num_leads)).T
    except ValueError as e:
        print(f"Reshape error: {e}")
        raise

    return leads_data, lead_labels, samples_per_second

# Example usage with one of the files (repeat for each file as necessary)
file_path = './ABC1234_2016-10-09_16-28-49 Philips file.txt'
leads_data, lead_labels, samples_per_second = extract_ecg_data_from_xml(file_path)
plot_ecg_leads(leads_data, lead_labels, samples_per_second, duration=10)

