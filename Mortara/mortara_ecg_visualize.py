import base64
import numpy as np
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

tree = ET.parse("ABC1234_2010-01-05_22-17-59 Mortara file.txt")
root = tree.getroot()

print(tree)
print(root)


def print_all_elements (element, level = 0):
	print('' * level + element.tag)
	for child in element:
		print_all_elements(child, level + 1)
		

print_all_elements(root)

def decode_ecg_data(base64_data):
	decoded_data = base64.b64decode(base64_data)
	return np.frombuffer(decoded_data, dtype=np.int16)
	
def print_element_data(element, level=0):
    indent = '  ' * level
    # Print the element tag and its attributes
    attrs = ' '.join([f'{k}="{v}"' for k, v in element.attrib.items()])
    print(f"{indent}<{element.tag} {attrs}>")
    
    # Print the element text content if it exists
    if element.text and element.text.strip():
        print(f"{indent}  {element.text.strip()}")
    
    # Recursively print child elements
    for child in element:
        print_element_data(child, level + 1)
    
    # Print the closing tag
    print(f"{indent}</{element.tag}>")

print_element_data(root)


channels = root.findall(".//CHANNEL")


# Function to decode base64 and convert to numpy array
def decode_ecg_data(base64_data):
    decoded_data = base64.b64decode(base64_data)
    return np.frombuffer(decoded_data, dtype=np.int16)

# Extract and plot data for each CHANNEL
channels = root.findall(".//CHANNEL")

# Print the number of CHANNEL elements found
print(f"Number of CHANNEL elements found: {len(channels)}")

# Create subplots
num_channels = len(channels)
fig, axs = plt.subplots(num_channels, 1, figsize=(10, 2*num_channels))

for idx, channel in enumerate(channels):
    # Extract the name of the lead
    lead_name = channel.attrib.get('NAME', 'Unknown')
    
    # Extract and decode the base64 data
    base64_data = channel.attrib.get('DATA', '')
    ecg_data = decode_ecg_data(base64_data) if base64_data else np.array([])
    
    # Plot the first 500 samples of the ECG data
    axs[idx].plot(ecg_data[:10000])
    axs[idx].set_title(f"Lead: {lead_name}")
    axs[idx].set_xlabel("Sample Number")
    axs[idx].set_ylabel("ECG Signal")

plt.tight_layout()
plt.show()
