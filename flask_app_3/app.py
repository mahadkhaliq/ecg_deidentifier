from flask import Flask, request, render_template, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import zipfile
import deiden
import detect_type

ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'  # Needed for session handling

    input_folder = os.path.abspath("input")
    output_folder = os.path.abspath("output")

    # Function to delete all files in a folder
    def delete_files(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

    # Delete all files in the output folder when the app launches
    delete_files(output_folder)

    @app.route('/upload', methods=['GET', 'POST'])
    def upload():
        if request.method == 'POST':
            files = request.files.getlist('file')
            if not files:
                return "No files selected", 400

            os.makedirs(input_folder, exist_ok=True)
            os.makedirs(output_folder, exist_ok=True)

            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    new_filename = f'{filename.rsplit(".", 1)[0]}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
                    file.save(os.path.join(input_folder, new_filename))

            return redirect(url_for('download'))

        return render_template('upload.html')

    @app.route('/download')
    def download():
        deiden.process_files_in_folder(input_folder, output_folder)

        # Create a zip file
        zip_filename = f"ecg_deidentified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_filepath = os.path.join(output_folder, zip_filename)
        with zipfile.ZipFile(zip_filepath, 'w') as zipf:
            for root, dirs, files in os.walk(output_folder):
                for file in files:
                    if file != zip_filename:
                        zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), output_folder))

        # Delete input files after processing
        delete_files(input_folder)

        return render_template('download.html', zip_filename=zip_filename)

    @app.route('/download/<filename>')
    def download_file(filename):
        file_path = os.path.join(output_folder, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        return "File not found", 404

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
