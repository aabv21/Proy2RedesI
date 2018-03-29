"""
    servidorDescarga.py

    Fecha: /04/2018
    Autor: Andres Buelvas
    carnet: 13-10184
    Materia: CI-4835 Redes De Computadoras I
    Proyecto #2: Cliente-Servidor
"""
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import socket, os
from _thread import *
import json

#
class Servidor():

    def __init__(self, servidorCentral, direccion, puerto):
        self.servidorCentral = servidorCentral
        self.nombre = socket.gethostname()
        self.direccion = direccion
        self.puerto = puerto

    # Direccion ip del servidor que se enviara al servidor central
    def enviarDireccion(self):
        si = self.servidorCentral.registrarServidores(self.direccion, self.puerto)

    # Lista de libros que se enviaran al servidor central
    def enviarListaLibros(self):
        listado = os.popen('ls | grep pdf').read()
        print(listado)
        si = self.servidorCentral.registrarLibros(listado, self.direccion)

    # Menu del Servidor 
    def consolaServidor(self):
        terminar = False
        while not (terminar):
            print("\n1) Estado de las Descargas \n2) Libros Descargados \n3) Clientes que solicitan mas libros \n0) Salir")
            opcion = int(input(">>> "))
            if 0 <= opcion <= 3:
                if opcion == 1:
                    print("Estado de las Descargas\n")
                elif opcion == 2:
                    self.VerLibrosDescargados()
                elif opcion == 3:
                    self.VerClientesQueSolicitan()
                else:
                    terminar = True

    # Registrar los libros descargados (No probado)
    def RegistrarLibrosDescargados(self, archivo):

        match = False
        cont = 0
        with open('librosDescargados.json' ,'r') as archivo:
            info = json.load(archivo)

        for i in info['Descargas']:
            if i['archivo'] == archivo:
                aux = int(i['numero'])
                aux += 1
                dicc = {'archivo': archivo, 'numero': str(aux)}
                with open('librosDescargados.json', 'r+') as f:
                    data = json.load(f)
                    f.seek(0)
                    data["Descargas"].pop(cont)
                    data["Descargas"].append(dicc)
                    json.dump(data, f, indent=4)
                match = True
                break
            else:
                cont += 1
        if not(match):
            with open('librosDescargados.json', 'r+') as f:
                data = json.load(f)
                f.seek(0)
                data["Descargas"].append({'archivo': archivo, 'numero': '1'})
                json.dump(data, f, indent=4)

    # Para registrar los clientes que mas han solicitado (No probado)
    def RegistrarClientesQueSolicitan(self, user, direccion):
        match = False
        cont = 0
        with open('SolicitudesClientes.json' ,'r') as archivo:
            info = json.load(archivo)

        for i in info['Clientes']:
            if i['nombre'] == user and i['direccion'] = direccion:
                aux = int(i['numero'])
                aux += 1
                dicc = {'nombre': user, 'direccion': direccion, 'numero': str(aux)}
                with open('SolicitudesClientes.json', 'r+') as f:
                    data = json.load(f)
                    f.seek(0)
                    data["Clientes"].pop(cont)
                    data["Clientes"].append(dicc)
                    json.dump(data, f, indent=4)
                match = True
                break
            else:
                cont += 1
        if not(match):
            with open('SolicitudesClientes.json', 'r+') as f:
                data = json.load(f)
                f.seek(0)
                data["Descargas"].append({'nombre': user, 'direccion': direccion, 'numero': '1'})
                json.dump(data, f, indent=4)

    # Ver en pantalla los libros descargados y en que cantidad
    def VerLibrosDescargados(self):
        with open('librosDescargados.json' ,'r') as archivo:
            info = json.load(archivo)

        for i in info['Descargas']:
            print("%s     %s" % (i['archivo'], i['numero']))

    def VerClientesQueSolicitan(self):
        with open('SolicitudesClientes.json' ,'r') as archivo:
            info = json.load(archivo)

        for i in info['Clientes']:
            print("%s     %s      %s" % (i['nombre'], i['direccion'], i['numero']))


# Crea los archivos del servidor
def crearArchivos():
    with open('librosDescargados.json', 'a+') as f:
        if os.stat('librosDescargados.json').st_size == 0:
            data = {}
            data['Descargas'] = []
            json.dump(data, f)

    with open('SolicitudesClientes.json', 'a+') as f:
        if os.stat('SolicitudesClientes.json').st_size == 0:
            data = {}
            data['Clientes'] = []
            json.dump(data, f)


# Conectarse con el servidor central
def conectar(ip):
    cliente = xmlrpc.client.ServerProxy(ip)
    return cliente

### Corrida del programa
if __name__ == '__main__':

    puerto = 8000
    #ip_server = datosDelServidor()
    ip = input("Introduce la direccion ip del servidor: ")
    instancia = conectar('http://192.168.1.140:8000')
    server = SimpleXMLRPCServer((ip, puerto), logRequests = False) #Servidor Central

    crearArchivos()

    servidor = Servidor(instancia, ip, puerto)
    servidor.enviarDireccion()
    servidor.enviarListaLibros()
    start_new_thread(servidor.consolaServidor, ())

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Saliendo')