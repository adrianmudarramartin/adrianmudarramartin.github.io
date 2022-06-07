from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir("..")


app = Flask(__name__)
app.config['IMAGE_UPLOADS'] = 'C:/Users/piano/Desktop/Yo/2022/Webpage/Images'

@app.route("/", methods=['GET', 'POST'])
def home():
	if request.method == "POST":
		print(request.files)
		image = request.files['file']
		filename = secure_filename(image.filename)
		image.save(app.config['IMAGE_UPLOADS']+'/'+filename)
		return render_template("webpage.htm")

	return render_template("webpage.htm")

@app.route("/Fajardo")
def fajardo():
	return "Puto Fajardo qué buen coche se ha comprado"

if __name__ == "__main__":
	app.run(port=5000)
