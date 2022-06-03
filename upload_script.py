from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import ctypes, sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if is_admin():
	print('PERMISOS DE ADMINISTRADOR COMPROBADOS')
	pass
else:
	print('NECESITO DARLE PERMISOS')
	ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
	sys.exit()


app = Flask(__name__)
app.config['IMAGE_UPLOADS'] = 'C:/Users/Usuario/Desktop'

@app.route("/", methods=['GET', 'POST'])
def home():
	if request.method == "POST":
		print(request.files)
		image = request.files['file']
		filename = secure_filename(image.filename)
		image.save(app.config['IMAGE_UPLOADS'])
		return render_template("webpage.htm")

	return render_template("webpage.htm")

@app.route("/Fajardo")
def fajardo():
	return "Puto Fajardo qué buen coche se ha comprado"

if __name__ == "__main__":
	app.run(port=5001)
