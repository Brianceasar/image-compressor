from flask import Flask, render_template, request, send_file
from io import BytesIO
from PIL import Image
import base64

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        # Get the uploaded image
        image = request.files['image'].read()
        image = Image.open(BytesIO(image))


        # Get the file extension of the uploaded image

        file_ext = request.files['image'].filename.split('.')[-1]

        # compress the image
        output = BytesIO()

        if image.mode != 'RGB':

            image = image.convert('RGB')
        if file_ext.lower() == 'png':
            image.save(output, format='PNG', optimize=True)
        else:

            image.save(output, format='JPEG', quality=50)

        output.seek(0)

        # Get the size of the compressed image
        compressed_size = len(output.getvalue())

        # Convert the compressed image to base64 for display
        compressed_image = base64.b64encode(output.getvalue())

        # Download the compressed image
        download_filename = f'compressed.{file_ext.lower()}'
        download_attachment = f'attachment; filename={download_filename}'

        return send_file(BytesIO(output.getvalue()), mimetype=f'image/{file_ext.lower()}',
                         as_attachment=True, attachment_filename=download_filename)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
