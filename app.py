from typing import Tuple
from flask import Flask, render_template, request, send_file, Response, url_for
from io import BytesIO
from PIL import Image
import base64
from werkzeug.datastructures import FileStorage


app = Flask(__name__)


last_output = {}


@app.route('/', methods=["POST", "GET"])
def index() -> str:
    if request.method == 'POST':
        # Get the uploaded image
        file = request.files.get('image')

        if not file:
            return "No image uploaded.", 400

        file_name, file_ext = file.filename.split('.')

        mimetype = f'image/{file_ext}'
        download_filename = f'{file_name}-compressed.{file_ext}'

        output, original_size = compress_image(file)

        if not output:
            return "Unable to compress the image.", 500

        last_output["bytes"] = output
        last_output["mimetype"] = mimetype
        last_output["download_filename"] = download_filename
        last_output["original_size"] = original_size

        compressed_size = len(output)
        compression_ratio = round(compressed_size / original_size * 100)

        compress_response = {
            "image_compressed": True,
            "original_size": original_size,
            "compressed_size": compressed_size,
            "compression_ratio": compression_ratio
        }

        return render_template(
            'index.html',
            compress_response=compress_response,
            download_url=url_for('download'),
            last_output=last_output
        )
    else:
        if last_output and "bytes" in last_output and isinstance(last_output["bytes"], bytes):
            return send_image(
                output=BytesIO(last_output["bytes"]),
                mimetype=last_output["mimetype"],
                as_attachment=True,
                download_name=last_output["download_filename"]
            )
        else:
            return "No compressed image to download.", 404


@app.route('/download')
def download() -> Response:
    if last_output and "bytes" in last_output and isinstance(last_output["bytes"], bytes):
        return send_image(
            output=BytesIO(last_output["bytes"]),
            mimetype=last_output["mimetype"],
            as_attachment=True,
            download_name=last_output["download_filename"]
        )
    else:
        return "No compressed image to download.", 404


def compress_image(file: FileStorage) -> Tuple[bytes, int]:
    try:
        file_bytes = BytesIO(file.read())

        image = Image.open(file_bytes)

        # Get the size of the original image
        original_size = len(file_bytes.getvalue())

        # compress the image
        output = BytesIO()

        if image.mode != 'RGB':
            image = image.convert('RGB')

        file_ext = file.filename.split(".")[-1].lower()

        if file_ext == 'png':
            image.save(output, format='PNG', optimize=True)
        else:
            image.save(output, format='JPEG', quality=50)

        output.seek(0)

        return output.getvalue(), original_size

    except Exception as e:
        print(f"Unable to compress image. Error: {e}")
        return None, 0


def send_image(output: BytesIO, download_name: str, mimetype: str, as_attachment: bool = True) -> Response:
    # Download the compressed image
    return send_file(
        path_or_file=output,
        mimetype=mimetype,
        as_attachment=as_attachment,
        download_name=download_name
    )


if __name__ == '__main__':
    app.run(debug=True)

