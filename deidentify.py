import random
import string
import xml.etree.ElementTree as ET
import os

def generate_random_id():
    return ''.join(random.choices(string.ascii_uppercase, k=3)) + ''.join(random.choices(string.digits, k=4))

def generate_random_name():
    names = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "India", "Juliet", "Kilo", "Lima", "Mike", "November", "Oscar", "Papa", "Quebec", "Romeo", "Sierra", "Tango", "Uniform", "Victor", "Whiskey", "X-ray", "Yankee", "Zulu"]
    return random.choice(names)

def deidentify_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Replace filename
    original_filename = os.path.basename(file_path)
    new_filename = generate_random_id() + " " + "file.txt"
    new_file_path = os.path.join(os.path.dirname(file_path), new_filename)
    
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
    print(f"De-identified file saved as: {new_file_path}")

# Paths to the uploaded files
file_paths = [
    './ABC1234_2021-09-27_21-53-39 Mindray file.txt',
    './ABC1234_2010-01-05_22-17-59 Mortara file.txt',
    './ABC1234_2016-10-09_16-28-49 Philips file.txt'
]

# Deidentify each file
for file_path in file_paths:
    deidentify_xml(file_path)

