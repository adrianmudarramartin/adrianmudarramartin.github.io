from multiprocessing import connection
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import sqlite3
import asana
import re
import os

con = sqlite3.connect('Database.db', check_same_thread=False)
cursor = con.cursor() 
cursor.execute('''CREATE TABLE IF NOT EXISTS Users (ID_Usuario INT PRIMARY KEY AUTOINCREMENT, Usuario TEXT, Clave TEXT, Tier INT, Nombre TEXT, Correo TEXT, Ultimo_Inicio TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Projects (ID_Proyecto INT PRIMARY KEY AUTOINCREMENT, Nombre TEXT, Creador TEXT, Asignado TEXT, Fecha_Apertura TEXT, Fotos BOOL, Partes BOOL, Subido_Fotos TEXT, Subido_Partes TEXT, Finalizado BOOL)''')
con.commit()
 
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir("..")

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
			cursor.execute('''SELECT Clave, Tier FROM Users WHERE Usuario = ?''', (username,))
			credentials_tuple = cursor.fetchone()
			if credentials_tuple[0] == password and credentials_tuple[1] >= 0:
				workspaces = client.workspaces.find_all()
				workspace = list(workspaces)[0]
				projects = client.projects.find_all({'workspace': workspace['gid']})
				plant_list = []
				for project in projects:
					cursor.execute('''SELECT ID_Proyecto FROM Projects WHERE Nombre = ?''', (project['name'],))
					if re.search('^MP|^MC', project['name']) and cursor.fetchone() == None:
						plant_list.append(project['name'])
				cursor.execute('''SELECT ID_Usuario, Nombre FROM Users''')
				users_tuples_list = cursor.fetchall()
				asignee_list = []
				for users_tuple in users_tuples_list:
					asignee_list.append(users_tuple)
				return render_template("admin.htm", plant_list=sorted(plant_list), username=username, asignee_list=sorted(asignee_list))
			else: return render_template("iniciarsesion.htm")
		except:
			return render_template("iniciarsesion.htm")
	
	elif request.method == "POST" and request.form.get('Planta') != None and request.form.get('Usuario') != None:
		plant = request.form.get('Planta')
		username = request.form.get('Usuario')
		asignee_list = request.form.getlist('Casilla_Asignado')
		print(asignee_list)
		cursor.execute('''INSERT INTO Projects VALUES (''')

if __name__ == "__main__":
	app.run(port=5000)
