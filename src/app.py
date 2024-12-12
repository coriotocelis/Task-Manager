import json
import os
from flask import Flask, render_template, request, redirect, url_for
from flask import flash
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
DATABASE_URL = "sqlite:///tareas.db"

class Tarea(Base):
    __tablename__ = 'tareas'
    id = Column(Integer, primary_key=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    completada = Column(Boolean, default=False)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/')
def index():
    tareas = session.query(Tarea).all()
    return render_template('index.html', tareas=tareas)

@app.route('/agregar', methods=['POST'])
def agregar():
    titulo = request.form['titulo']
    descripcion = request.form['descripcion']
    nueva_tarea = Tarea(titulo=titulo, descripcion=descripcion)
    session.add(nueva_tarea)
    session.commit()
    return redirect(url_for('index'))

@app.route('/completar/<int:id>')
def completar(id):
    tarea = session.query(Tarea).filter(Tarea.id == id).first()
    if tarea:
        tarea.completada = True
        session.commit()
    return redirect(url_for('index'))

@app.route('/eliminar/<int:id>')
def eliminar(id):
    tarea = session.query(Tarea).filter(Tarea.id == id).first()
    if tarea:
        session.delete(tarea)
        session.commit()
    return redirect(url_for('index'))

@app.route('/guardar')
def guardar():
    tareas = session.query(Tarea).all()
    tareas_lista = [{"id": tarea.id, "titulo": tarea.titulo, "descripcion": tarea.descripcion, "completada": tarea.completada} for tarea in tareas]
    with open("tareas.json", "w") as file:
        json.dump(tareas_lista, file, indent=4)
    return redirect(url_for('index'))

@app.route('/cargar', methods=['POST'])
def cargar():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and file.filename.endswith('.json'):
        try:

            data = json.load(file)

            session.query(Tarea).delete()
            session.commit()

            for tarea_data in data:
                nueva_tarea = Tarea(
                    id=tarea_data['id'],
                    titulo=tarea_data['titulo'],
                    descripcion=tarea_data['descripcion'],
                    completada=tarea_data['completada']
                )
                session.add(nueva_tarea)
            
            session.commit()
            flash('Archivo JSON cargado exitosamente.')
        except json.JSONDecodeError:
            flash('Error al leer el archivo JSON.')
    else:
        flash('El archivo debe ser un JSON.')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
