from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir("..")
credentials_dict = {'AMM': '1234'}

app = Flask(__name__)
app.config['FILE_UPLOADS'] = 'C:/Users/Usuario/Desktop/Proyectos/adrianmudarramartin.github.io/Files'

@app.route("/", methods=['GET', 'POST'])
def home():
	if request.method == "GET":
		return render_template("iniciarsesion.htm")
	if request.method == "POST" and request.files.getlist('file') == []:
		pass
		username = request.form.get('Usuario')
		password = request.form.get('Contraseña')
		try:
			if credentials_dict[username] == password:
				return render_template("webpage.htm")
			else:
				return render_template("iniciarsesion.htm")
		except:
			return render_template("iniciarsesion.htm")
			
	elif request.method == "POST" and request.files.getlist('file') != []:
		#print(request.files)
		#print(request.files.getlist('file'))
		print(request.form.get('type'))
		for file in request.files.getlist('file'):
			#print(file)
			filename = secure_filename(file.filename)
			file.save(app.config['FILE_UPLOADS']+'/'+filename)
	return render_template("webpage.htm")

@app.route("/Fajardo")
def fajardo():
	return "Puto Fajardo qué buen coche se ha comprado"

if __name__ == "__main__":
	app.run(port=5000)
