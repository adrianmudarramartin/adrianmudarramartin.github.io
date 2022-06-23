from multiprocessing import connection
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import sqlite3
import asana
import re
import os
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
		return render_template("iniciarsesion.htm", admin=False)
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
			else: return render_template("iniciarsesion.htm", info='No tiene permisos de acceso', admin=False)
		except Exception as e:
			return render_template("iniciarsesion.htm", info='Usuario o contraseña incorrectos. Inténtelo de nuevo', admin=False)
			 
	elif request.method == "POST" and request.form['submit'] == "Iniciar sesión":
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
		now = datetime.now().strftime("%d-%m-%Y %H.%M")
		number = 0
		for file in request.files.getlist('Archivo'):
			filetype = file.filename.split('.')[-1]
			#filename = secure_filename(file.filename)
			while(True):
				filepath = app.config['FILE_UPLOADS']+'\\'+plant+'\\'+type+'\\'+now+'_'+username+'_'+type+'_'+str(number)+'.'+filetype  
				if not os.path.exists(filepath):
					file.save(app.config['FILE_UPLOADS']+'\\'+plant+'\\'+type+'\\'+now+'_'+username+'_'+type+'_'+str(number)+'.'+filetype)
					number = number + 1
					break
				else: number = number + 1
		if type == 'PARTES DE INSPECCIÓN': cursor.execute('''UPDATE Projects SET Partes = ?, Subido_Partes = ? WHERE Nombre = ?''', (1, user_id, plant))
		else: cursor.execute('''UPDATE Projects SET Fotos = ?, Subido_Fotos = ? WHERE Nombre = ?''', (1, user_id, plant))
		con.commit()
		return render_template("iniciarsesion.htm", info='Archivos subidos correctamente', admin=False)

@app.route("/admin", methods=['GET', 'POST'])
def admin():
	if request.method == "GET":
		return render_template("iniciarsesion.htm", admin=True)
		
	if request.method == "POST" and request.form['submit'] == 'Abrir caso':
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
				return render_template("admin-open.htm", plant_list=sorted(plant_list), username=username, asignee_list=sorted(asignee_list))
			else: return render_template("iniciarsesion.htm", info='Usuario o contraseña incorrectos. Inténtelo de nuevo', admin=True)
		except Exception as e:
			return render_template("iniciarsesion.htm", info='Usuario o contraseña incorrectos. Inténtelo de nuevo', admin=True)
	
	elif request.method == "POST" and request.form.get('Planta') != None and request.form.get('Usuario') != None:
		plant = request.form.get('Planta')
		username = request.form.get('Usuario')
		cursor.execute('''SELECT ID_Usuario FROM Users WHERE Usuario = ?''', (username,))
		user_id = cursor.fetchone()[0]
		asignee_list = request.form.getlist('Casilla_Asignado')
		now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		cursor.execute('''INSERT INTO Projects (Nombre, Creador, Asignado, Fecha_Apertura, Fotos, Partes, Subido_Fotos, Subido_Partes, Finalizado) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (plant, user_id, str(asignee_list), now, 0, 0, None, None, 0))
		con.commit()
		return render_template("iniciarsesion.htm", info='Proyecto abierto correctamente', admin=True)

	if request.method == "POST" and request.form['submit'] == 'Revisar caso':
		username = request.form.get('Usuario')
		password = request.form.get('Contraseña')
		try:
			cursor.execute('''SELECT ID_Usuario, Clave, Tier FROM Users WHERE Usuario = ?''', (username,))
			credentials_tuple = cursor.fetchone()
			if credentials_tuple[1] == password and credentials_tuple[2] >= 1:
				cursor.execute('''SELECT ID_Proyecto, Nombre FROM Projects''')
				
		except Exception as e:
			return render_template("iniciarsesion.htm", info='Usuario o contraseña incorrectos. Inténtelo de nuevo', admin=True)
if __name__ == "__main__":
	app.run(port=5000)
