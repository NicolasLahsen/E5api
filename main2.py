from flask import Flask, render_template, request, abort, json
from pymongo import MongoClient
from bson.objectid import ObjectId
#import pandas as pd
#import matplotlib.pyplot as plt
import os
import atexit
import subprocess

USER_KEYS = ['name', 'last_name', 'occupation', 'follows', 'age']

mongod = subprocess.Popen('mongod', stdout=subprocess.DEVNULL)

atexit.register(mongod.kill)

client = MongoClient('localhost', connect=False)

db = client["test"]

usuarios = db.usuarios

mensajes = db.mensajes

app = Flask(__name__)

MSG_KEYS = ['message', 'lat', 'long', 'date']


@app.route("/")
def home():
    return '<h1>Hello</h1>'

@app.route("/todos")
def get_messages():
    mensaje = [u for u in mensajes.find({},{"_id":0})]
    return json.jsonify(mensaje)

@app.route("/message/<int:mid>")
def get_message(mid):
    mensaje = [i for i in mensajes.find({"mid":mid},{"_id":0})]
    return json.jsonify(mensaje)


@app.route("/mensajes_de_usuario/<int:uid>")
def get_messages_user(uid):
    users = list(usuarios.find({"uid": uid}, {"_id": 0}))
    users[0]['mensajes'] = list(mensajes.find({"sender":uid}, {"_id": 0}))
    return json.jsonify(users)


@app.route("/conversacion/<int:uid1>/<int:uid2>")
def get_conv(uid1, uid2):
    enviados = list(mensajes.find({"$and": [{"sender": uid1}, {"receptant": uid2}]}, {"_id": 0}))
    recibidos = list(mensajes.find({"$and": [{"sender": uid2}, {"receptant": uid1}]}, {"_id": 0}))
    conversaciones = enviados + recibidos
    return json.jsonify(conversaciones)


@app.route("/frases_necesarias/<frases>")
def frases_necesarias(frases):
    mensajes.create_index([("message", 'text')])
    if ";" not in frases:
        busqueda = '\"' + frases + '\""' + ' '
        res = list(mensajes.find({"$text": {"$search": busqueda}},{"_id": 0}))
    else:
        busqueda = frases.split(";")
        busqueda2 = ""
        for f in busqueda:
            busqueda2 += '\"' + f + '\""' + ' '
        res = list(mensajes.find({"$text": {"$search": busqueda2}},{"_id": 0}))
    return json.jsonify(res)


@app.route("/frases_necesarias/<int:uid>/<frases>")
def frases_necesarias_uid(uid, frases):
    mensajes.create_index([("message", 'text')])
    if ";" not in frases:
        busqueda = '\"' + frases + '\""' + ' '
        res = list(mensajes.find({"sender": uid, "$text": {"$search": busqueda}},{"_id": 0}))
    else:
        busqueda = frases.split(";")
        busqueda2 = ""
        for f in busqueda:
            busqueda2 += '\"' + f + '\""' + ' '
        res = list(mensajes.find({"sender": uid, "$text": {"$search": busqueda2}},{"_id": 0}))
    return json.jsonify(res)


@app.route("/frases_prohibidas/<frases>")
def frases_prohibidas(frases):
    mensajes.create_index([("message", 'text')])
    if ";" not in frases:
        busqueda = '\"' + frases + '\""' + ' '
        res = [item for item in list(mensajes.find({},{"_id": 0})) if item not in
        list(mensajes.find({"$text": {"$search": busqueda}},{"_id": 0}))]
    else:
        busqueda = frases.split(";")
        busqueda2 = ""
        for f in busqueda:
            busqueda2 += '\"' + f + '\""' + ' '
        res = [item for item in list(mensajes.find({},{"_id": 0})) if item not in
        list(mensajes.find({"$text": {"$search": frases}},{"_id": 0}))]
    return json.jsonify(res)


@app.route("/frases_prohibidas/<int:uid>/<frases>")
def frases_prohibidas2(uid, frases):
    mensajes.create_index([("message", 'text')])
    if ";" not in frases:
        busqueda = '\"' + frases + '\""' + ' '
        res = [item for item in list(mensajes.find({"sender":uid},{"_id": 0})) if item not in
        list(mensajes.find({"$text": {"$search": busqueda}},{"_id": 0}))]
    else:
        busqueda = frases.split(";")
        busqueda2 = ""
        for f in busqueda:
            busqueda2 += '\"' + f + '\""' + ' '
        res = [item for item in list(mensajes.find({"sender":uid},{"_id": 0})) if item not in
        list(mensajes.find({"$text": {"$search": frases}},{"_id": 0}))]
    return json.jsonify(res)


@app.route("/crear_mensaje/<int:uid1>/<int:uid2>", methods=['POST'])
def create_message(uid1, uid2):
    data = {key: request.json[key] for key in MSG_KEYS}
    data['sender'] = uid1
    data['receptant'] = uid2
    result = mensajes.insert_one(data)
    if (result):
        message = "1 mensaje creado"
        success = True
    else:
        message = "No se pudo crear el mensaje"
        success = False

    # Retorno el texto plano de un json
    return json.jsonify({'success': success, 'message': message})


@app.route('/borrar_mensaje/<int:mid>', methods=['DELETE'])
def delete_message(mid):
    mensajes.delete_one(mensajes.find({"mid":mid},{"_id":0}))
    message = str(f'Mensaje con id={mid} ha sido eliminado.')
    return json.jsonify({'result': 'success', 'message': message})

@app.route("/frases_deseables/<frases>")
def frases_deseables(frases):
    mensajes.create_index([("message", 'text')])
    if ";" not in frases:
        busqueda = frases + ' '
        res = list(mensajes.find({"$text": {"$search": busqueda}},{"_id": 0}))
    else:
        busqueda = frases.split(";")
        busqueda2 = ""
        for f in busqueda:
            busqueda2 += f + ' '
        res = list(mensajes.find({"$text": {"$search": busqueda2}},{"_id": 0}))
    return json.jsonify(res)


@app.route("/frases_deseables/<int:uid>/<frases>")
def frases_deseables_uid(uid, frases):
    mensajes.create_index([("message", 'text')])
    if ";" not in frases:
        busqueda =frases + ' '
        res = list(mensajes.find({"sender": uid, "$text": {"$search": busqueda}},{"_id": 0}))
    else:
        busqueda = frases.split(";")
        busqueda2 = ""
        for f in busqueda:
            busqueda2 += f + ' '
        res = list(mensajes.find({"sender": uid, "$text": {"$search": busqueda2}},{"_id": 0}))
    return json.jsonify(res)


if os.name == 'nt':
    app.run()
