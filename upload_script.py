from multiprocessing import connection
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import sqlite3
import asana
import os

con = sqlite3.connect('Database.db', check_same_thread=False)
cursor = con.cursor() 
cursor.execute('''CREATE TABLE IF NOT EXISTS Users (ID_Usuario PRIMARY KEY, Usuario TEXT, Clave TEXT, Tier INT, Correo TEXT, Ultimo_Inicio TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Projects (ID_Proyecto PRIMARY KEY, Nombre TEXT, Creador TEXT, Asignado TEXT, Fecha_Apertura TEXT, Fotos BOOL, Partes BOOL, Subido_Fotos TEXT, Subido_Partes TEXT, Finalizado BOOL)''')
con.commit()
 
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir("..")
credentials_AMM = {'Username': 'AMM', 'Password': '1234', 'Tier': 1} # Borrar esto en cuanto esté 100% implementada la base de datos con las claves
credentials_AFM = {'Username': 'AFM', 'Password': '5678', 'Tier': 0}
credentials_list = [credentials_AMM, credentials_AFM]

app = Flask(__name__)
app.config['FILE_UPLOADS'] = 'C:/Users/Usuario/Desktop/Proyectos/adrianmudarramartin.github.io/Files'

client = asana.Client.access_token('1/1202152890606392:57a2152dee423466ce283d2b8a3c70f5')

@app.route("/", methods=['GET', 'POST'])
def home():
	if request.method == "GET":
		return render_template("iniciarsesion.htm")
	if request.method == "POST" and request.files.getlist('file') == []:
		username = request.form.get('Usuario')
		password = request.form.get('Contraseña')
		try:
			cursor.execute('''SELECT Clave, Tier FROM Users WHERE Usuario = ?''', (username,))
			credentials_tuple = cursor.fetchone()
			if credentials_tuple[0] == password and credentials_tuple[1] >= 0:
				return render_template("webpage.htm")
			else: return render_template("iniciarsesion.htm")
		except:
			return render_template("iniciarsesion.htm")
			
	elif request.method == "POST" and request.files.getlist('file') != []:
		print(request.form.get('type'))
		for file in request.files.getlist('file'):
			filename = secure_filename(file.filename)
			file.save(app.config['FILE_UPLOADS']+'/'+filename)
	return render_template("webpage.htm")

@app.route("/admin", methods=['GET', 'POST'])
def admin():
	if request.method == "GET":
		return render_template("iniciarsesion.htm")
		
	if request.method == "POST" and request.form.get('Planta') == None:
		username = request.form.get('Usuario')
		password = request.form.get('Contraseña')
		try:
			credentials_check = False
			for credentials_dict in credentials_list:
				if credentials_dict['Username'] == username and credentials_dict['Password'] == password and credentials_dict['Tier'] >= 1:
					credentials_check = True
					workspaces = client.workspaces.find_all()
					workspace = list(workspaces)[0]
					projects = client.projects.find_all({'workspace': workspace['gid']})
					plant_list = []
					for project in projects:
						plant_list.append(project['name'])
					return render_template("admin.htm", plant_list=plant_list)
					break
			if credentials_check == False: return render_template("iniciarsesion.htm")
		except:
			return render_template("iniciarsesion.htm")
	
	#elif request.method == "POST" and request.form.get('plant') != None:
	#	plant = request.form.get('Planta')


if __name__ == "__main__":
	app.run(port=5000)
