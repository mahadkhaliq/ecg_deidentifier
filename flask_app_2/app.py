from flask import Flask, request, render_template, redirect, url_for, session, send_file
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import deiden
import zipfile

ALLOWED_EXTENSIONS = set(['txt'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'  # Needed for session handling

    @app.route('/upload', methods=['GET', 'POST'])
    def upload():
        if request.method == 'POST':
            files = request.files.getlist('file')
            device = request.form.get('device')

            if not files:
                return "No files selected", 400

            save_location = os.path.join(os.path.abspath("input"))
            out_location = os.path.join(os.path.abspath("output"))
            os.makedirs(save_location, exist_ok=True)
            os.makedirs(out_location, exist_ok=True)

            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    new_filename = f'{filename.split(".")[0]}_{str(datetime.now())}.txt'
                    file.save(os.path.join(save_location, new_filename))

            # Store the device in the session
            session['device'] = device

            return redirect(url_for('download'))

        return render_template('upload.html')

    @app.route('/download')
    def download():
        device = session.get('device')
        if not device:
            return "Device not selected", 400

        save_location = os.path.join(os.path.abspath("input"))
        out_location = os.path.join(os.path.abspath("output"))
        deiden.process_files_in_folder(device, save_location, out_location)

        # Create a zip file
        zip_filename = f"ecg_deidentified_{device}_{datetime.now()}.zip"
        zip_filepath = os.path.join(out_location, zip_filename)
        with zipfile.ZipFile(zip_filepath, 'w') as zipf:
            for root, dirs, files in os.walk(out_location):
                for file in files:
                    if file != zip_filename:
                        zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), out_location))

        return render_template('download.html', zip_filename=zip_filename)

    @app.route('/download/<filename>')
    def download_file(filename):
        file_path = os.path.join(os.path.abspath("output"), filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        return "File not found", 404

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
