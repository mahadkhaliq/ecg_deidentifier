import matplotlib.pyplot as plt
import pydicom
import os

def load_view_echocardiogram(folder):
	dicom_files = [f for f in os.listdir(dicom_folder)]
	
	if not dicom_files:
		print("No Dicom files found")
		return
		
	dicom_path = os.path.join(dicom_folder, dicom_files[0])
	dicom_data = pydicom.dcmread(dicom_path)
	
	print(dicom_data)
	
	if "PixelData" in dicom_data:

		image_data = dicom_data.pixel_array
		print(image_data.shape)
		image_data = image_data[1,:,:,:]
		image_data_c = image_data[50:,:]
		print(image_data.shape)
		plt.subplot(1,2,1)
		plt.imshow(image_data, cmap='gray')
		plt.title ("Original Echocardiogram")
		plt.subplot(1,2,2)
		plt.imshow(image_data_c, cmap='gray')
		plt.title("Cropped Echocardiogram")
		plt.show()
		
	else:
		print("no image data")
dicom_folder = './20240702112621038f3abf762fb'
load_view_echocardiogram(dicom_folder)
