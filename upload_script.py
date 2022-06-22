from multiprocessing import connection
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import sqlite3
import asana
import re
import os
import json
from datetime import datetime

con = sqlite3.connect('Database.db', check_same_thread=False)
cursor = con.cursor() 
cursor.execute('''CREATE TABLE IF NOT EXISTS Users (ID_Usuario INTEGER PRIMARY KEY AUTOINCREMENT, Usuario TEXT, Clave TEXT, Tier INTEGER, Nombre TEXT(200), Correo TEXT(200), Ultimo_Inicio TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Projects (ID_Proyecto INTEGER PRIMARY KEY AUTOINCREMENT, Nombre TEXT(200), Creador TEXT, Asignado TEXT, Fecha_Apertura TEXT, Fotos BIT, Partes BIT, Subido_Fotos TEXT, Subido_Partes TEXT, Finalizado BIT)''')
con.commit()
 
os.chdir(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
app.config['FILE_UPLOADS'] = os.path.dirname(os.path.abspath(__file__))+'\\Files'

client = asana.Client.access_token('1/1202152890606392:57a2152dee423466ce283d2b8a3c70f5')

@app.route("/", methods=['GET', 'POST'])
def home():
	if request.method == "GET":
		return render_template("iniciarsesion.htm")
	if request.method == "POST" and request.files.getlist('Archivo') == []:
		username = request.form.get('Usuario')
		password = request.form.get('Contraseña')
		try:
			cursor.execute('''SELECT ID_Usuario, Clave, Tier FROM Users WHERE Usuario = ?''', (username,))
			credentials_tuple = cursor.fetchone()
			if credentials_tuple[1] == password and credentials_tuple[2] >= 0:
				cursor.execute('''SELECT ID_Proyecto, Nombre, Asignado FROM Projects''')
				projects_tuple_list = cursor.fetchall()
				project_list = []
				for project_tuple in projects_tuple_list:
					asignee_list = project_tuple[2].strip('][').split(', ')
					if '\''+str(credentials_tuple[0])+'\'' in asignee_list: 
						project_list.append(project_tuple[1])
				return render_template("webpage.htm", username=username, project_list=project_list)
			else: return render_template("iniciarsesion.htm", info='No tiene permisos de acceso')
		except Exception as e:
			return render_template("iniciarsesion.htm", info='Usuario o contraseña incorrectos. Inténtelo de nuevo')
			
	elif request.method == "POST" and request.files.getlist('Archivo') != []:
		plant = request.form.get('Planta')
		username = request.form.get('Usuario')
		cursor.execute('''SELECT ID_Usuario FROM Users WHERE Usuario = ?''', (username,))
		user_id = cursor.fetchone()[0]
		type = request.form.get('Tipo')
		if not os.path.exists(os.path.dirname(os.path.abspath(__file__))+'\\Files\\'+plant):
			os.mkdir(app.config['FILE_UPLOADS']+'\\'+plant)
			os.mkdir(app.config['FILE_UPLOADS']+'\\'+plant+'\\'+type)
		elif not os.path.exists(os.path.dirname(os.path.abspath(__file__))+'\\Files\\'+plant+'\\'+type):
			os.mkdir(app.config['FILE_UPLOADS']+'\\'+plant+'\\'+type)
		for file in request.files.getlist('Archivo'):
			filename = secure_filename(file.filename)
			file.save(app.config['FILE_UPLOADS']+plant+'\\'+type+'\\'+filename)
	return render_template("iniciarsesion.htm", info='Archivos subidos correctamente')

@app.route("/admin", methods=['GET', 'POST'])
def admin():
	if request.method == "GET":
		return render_template("iniciarsesion.htm")
		
	if request.method == "POST" and request.form.get('Planta') == None:
		username = request.form.get('Usuario')
		password = request.form.get('Contraseña')
		try:
			cursor.execute('''SELECT ID_Usuario, Clave, Tier FROM Users WHERE Usuario = ?''', (username,))
			credentials_tuple = cursor.fetchone()
			if credentials_tuple[1] == password and credentials_tuple[2] >= 1:
				workspaces = client.workspaces.find_all()
				workspace = list(workspaces)[0]
				projects = client.projects.find_all({'workspace': workspace['gid']})
				plant_list = []
				for project in projects:
					cursor.execute('''SELECT ID_Proyecto FROM Projects WHERE Nombre = ?''', (project['name'],))
					project_id = cursor.fetchone()
					if re.search('^MP|^MC', project['name']) and project_id == None:
						plant_list.append(project['name'])
				cursor.execute('''SELECT ID_Usuario, Nombre FROM Users''')
				users_tuples_list = cursor.fetchall()
				asignee_list = []
				for users_tuple in users_tuples_list:
					asignee_list.append(users_tuple)
				return render_template("admin.htm", plant_list=sorted(plant_list), username=username, asignee_list=sorted(asignee_list))
			else: return render_template("iniciarsesion.htm", info='Usuario o contraseña incorrectos. Inténtelo de nuevo')
		except Exception as e:
			return render_template("iniciarsesion.htm", info='Usuario o contraseña incorrectos. Inténtelo de nuevo')
	
	elif request.method == "POST" and request.form.get('Planta') != None and request.form.get('Usuario') != None:
		plant = request.form.get('Planta')
		username = request.form.get('Usuario')
		cursor.execute('''SELECT ID_Usuario FROM Users WHERE Usuario = ?''', (username,))
		user_id = cursor.fetchone()[0]
		asignee_list = request.form.getlist('Casilla_Asignado')
		now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		cursor.execute('''INSERT INTO Projects (Nombre, Creador, Asignado, Fecha_Apertura, Fotos, Partes, Subido_Fotos, Subido_Partes, Finalizado) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (plant, user_id, str(asignee_list), now, 0, 0, None, None, 0))
		con.commit()
		return render_template("iniciarsesion.htm", info='Proyecto abierto correctamente')

if __name__ == "__main__":
	app.run(port=5000)
