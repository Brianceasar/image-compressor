from flask import Flask, render_template, request
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

        # Get file extension of uploaded image
        file_ext = request.files['image'].filename.split('.')[-1]

        # compress the image
        output = BytesIO()
        if image.mode !='RGB':
            image = image.convert('RGB')
        if file_ext.lower() == 'png':
            image.save(output, format='PNG', optimize=True)
        else:
            image.save(output, format="JPEG", quality=50)
        output.seek(0)

        # convert the compressed image to base64 for display
        compressed_image = base64.b64encode(output.getvalue())

        return render_template('index.html', compressed_image=compressed_image)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
