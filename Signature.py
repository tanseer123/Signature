from flask import Flask, render_template_string, request, send_file
import os
from PIL import Image
import io
import base64

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Signature</title>
    <style>
        .main {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
        .canvas {
            border: 2px solid black;
        }
        .top,
        .bottom {
            display: flex;
            flex-direction: row;
            justify-content: space-between;
            margin: 20px 0 20px 0;
        }
        .block,
        input,
        select,
        button {
            width: 80%;
        }
        .column {
            display: flex;
            flex-direction: column;
        }
        .bottom>button {
            margin: 10px;
        }
        .top>.block {
            margin: 10px;
        }
        .block>p {
            margin: 10px auto;
            width: 50%;
        }
    </style>
    <link rel="icon" href="favicon.png">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css"
        integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk" crossorigin="anonymous">
</head>
<body>
    <div class="main">
        <div class="top">
            <div class="block">
                <p>Text color picker</p>
                <input class="form-control" type="color" id="colorPicker">
            </div>
            <div class="block">
                <p>Background</p>
                <input class="form-control" type="color" id="canvasColor">
            </div>
            <div class="block">
                <p>Font size</p>
                <select class="custom-select" type="select" id="fontSizePicker">
                    <option value="5">5px</option>
                    <option value="10">10px</option>
                    <option value="20">20px</option>
                    <option value="30">30px</option>
                    <option value="40">40px</option>
                    <option value="50">50px</option>
                </select>
            </div>
        </div>
        <canvas class="canvas" id="myCanvas" width="800" height="500"></canvas>
        <div class="bottom">
            <button type="button" class="btn btn-danger" id="clearButton">Clear</button>
            <button type="button" class="btn btn-success" id="saveButton">Save & download</button>
            <button type="button" class="btn btn-warning" id="retrieveButton">Retrieve saved signature</button>
        </div>
    </div>
    <script>
        let history = [];
        const colorPicker = document.getElementById('colorPicker');
        const canvasColor = document.getElementById('canvasColor');
        const canvas = document.getElementById('myCanvas');
        const clearButton = document.getElementById('clearButton');
        const saveButton = document.getElementById('saveButton');
        const fontSizePicker = document.getElementById('fontSizePicker');
        const ctx = canvas.getContext('2d');

        let isDrawing = false;
        let lastX = 0;
        let lastY = 0;

        colorPicker.addEventListener('change', (event) => {
            ctx.fillStyle = event.target.value;
            ctx.strokeStyle = event.target.value;
        });

        canvasColor.addEventListener('change', (event) => {
            ctx.fillStyle = event.target.value;
            ctx.fillRect(0, 0, 800, 500);
        });

        canvas.addEventListener('mousedown', (event) => {
            isDrawing = true;
            lastX = event.offsetX;
            lastY = event.offsetY;
        });

        canvas.addEventListener('mousemove', (event) => {
            if (isDrawing) {
                ctx.beginPath();
                ctx.moveTo(lastX, lastY);
                ctx.lineTo(event.offsetX, event.offsetY);
                ctx.stroke();
                lastX = event.offsetX;
                lastY = event.offsetY;
            }
        });

        canvas.addEventListener('mouseup', () => {
            isDrawing = false;
        });

        fontSizePicker.addEventListener('change', (event) => {
            ctx.lineWidth = event.target.value;
        });

        clearButton.addEventListener('click', () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        });

        saveButton.addEventListener('click', () => {
            const dataUrl = canvas.toDataURL();
            fetch('/save_canvas', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ image: dataUrl }),
            }).then(response => response.json())
              .then(data => {
                  const link = document.createElement('a');
                  link.download = 'my-canvas.png';
                  link.href = data.url;
                  link.click();
              });
        });

        retrieveButton.addEventListener('click', () => {
            fetch('/retrieve_canvas')
                .then(response => response.json())
                .then(data => {
                    if (data.image) {
                        let img = new Image();
                        img.src = data.image;
                        img.onload = () => {
                            ctx.clearRect(0, 0, canvas.width, canvas.height);
                            ctx.drawImage(img, 0, 0);
                        }
                    }
                });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/save_canvas', methods=['POST'])
def save_canvas():
    data = request.json
    image_data = data['image']
    image_data = image_data.split(",")[1]
    image_data = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(image_data))
    image.save("signature.png")

    return {"url": "/download_canvas"}

@app.route('/retrieve_canvas', methods=['GET'])
def retrieve_canvas():
    if os.path.exists("signature.png"):
        with open("signature.png", "rb") as img_file:
            b64_string = base64.b64encode(img_file.read()).decode('utf-8')
            return {"image": f"data:image/png;base64,{b64_string}"}
    return {"image": None}

@app.route('/download_canvas', methods=['GET'])
def download_canvas():
    return send_file("signature.png", as_attachment=True, attachment_filename="signature.png")

if __name__ == '__main__':
    app.run(debug=True)
