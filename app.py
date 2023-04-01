from typing import Tuple
from flask import Flask, render_template, request, send_file
from io import BytesIO
from PIL import Image
import base64
from werkzeug.datastructures import FileStorage

app = Flask(__name__)

last_output: dict = {}


@app.route('/', methods=["POST", "GET"])
def index():

    if request.method == 'POST':
        # Get the uploaded image
        file = request.files['image']

        if file is None:
            return

        file_name = file.filename.split('.')
        file_ext = file_name[1]
        mimetype = f'image/{file_ext}'
        download_filename = f'{file_name[0]}-compressed.{file_ext}'

        output, original_size = compress_image(file)
        last_output["bytes"] = output
        last_output["mimetype"] = mimetype
        last_output["download_filename"] = download_filename
        last_output["original_size"] = original_size

        compressed_size = len(output)

        compress_response = {
            "image_compressed": compressed_size > 0,
            "original_size": original_size,
            "compressed_size": compressed_size
        }

        return render_template(
            'index.html',
            compress_response=compress_response
        )
    else:
        if last_output is not None and "bytes" in last_output and isinstance(last_output["bytes"], bytes):
            send_image(
                output=BytesIO(last_output["bytes"]),
                mimetype=last_output["mimetype"],
                as_attachment=True,
                download_name=last_output["download_filename"]
            )
        # else:
        #     return "No compressed image to download."

    return render_template('index.html')


@app.route('/download')
def download():
    if last_output is not None:
        return send_file(
            BytesIO(last_output["bytes"]),
            mimetype=last_output["mimetype"],
            as_attachment=True,
            download_name=last_output["download_filename"]
        )


def compress_image(file: FileStorage) -> tuple[bytes, int]:
    file_name = file.filename.split(".")[0]
    file_ext = file.filename.split(".")[1]

    file_bytes = BytesIO(file.read())

    image: Image = Image.open(file_bytes)

    # Get the size of the original image
    original_size = len(file_bytes.getvalue())

    # compress the image
    output = BytesIO()
    if image.mode != 'RGB':
        image = image.convert('RGB')
    if file_ext.lower() == 'png':
        image.save(output, format='PNG', optimize=True)
    else:
        image.save(output, format='JPEG', quality=50)
    output.seek(0)

    return output.getvalue(), original_size


def send_image(output: BytesIO, download_name: str, mimetype: str, as_attachment: bool = True):

    # Download the compressed image
    download_attachment = f'attachment; filename={download_name}'

    return send_file(
        path_or_file=BytesIO(output.getvalue()),
        mimetype=mimetype,
        as_attachment=as_attachment,
        download_name=download_name
    )


if __name__ == '__main__':
    app.run(debug=True)
