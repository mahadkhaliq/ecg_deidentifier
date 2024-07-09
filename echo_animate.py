import matplotlib.pyplot as plt
import pydicom
import os
import matplotlib.animation as animation

def load_view_echocardiogram(folder):
    dicom_files = [f for f in os.listdir(folder)]
    
    if not dicom_files:
        print("No DICOM files found")
        return
    
    dicom_path = os.path.join(folder, dicom_files[0])
    dicom_data = pydicom.dcmread(dicom_path)
    
    print(dicom_data)
    
    if "PixelData" in dicom_data:
        image_data = dicom_data.pixel_array[:, 50:, :, :1]
        print(len(image_data))
        print(image_data.shape)        
        fig, ax = plt.subplots()
        im = ax.imshow(image_data[0], cmap='gray')

        def animate(i):
            im.set_array(image_data[i])
            return [im]
        
        ani = animation.FuncAnimation(fig, animate, frames=len(image_data), interval=100, blit=True)
        ani.save(filename="./cropped_echo.gif", writer="pillow")
        plt.show()
        
        
    else:
        print("No image data")

# Specify the folder containing DICOM files
dicom_folder = './20240702112621038f3abf762fb'

load_view_echocardiogram(dicom_folder)

