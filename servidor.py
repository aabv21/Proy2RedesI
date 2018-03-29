"""
    servidor.py
    
    Fecha: /04/2018
    Autor: Andres Buelvas
    carnet: 13-10184
    Materia: CI-4835 Redes De Computadoras I
    Proyecto #2: Cliente-Servidor
"""

from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import sys, json, os
import threading
from _thread import *

class ServidorCentral():

    def solicitarListaServidores(self):
        pass

    #######
    ### SERVIDOR DESCARGA
    #######

    def registrarServidores(self, direccion, puerto):
        match = False
        with open('servidoresDescargas.json', 'r+') as f:
            data = json.load(f)

            for i in data['Registro']:
                if i['direccion'] == direccion:
                    match = True
                    break

            if not(match):
                f.seek(0)
                data["Registro"].append({'direccion': direccion, 'puerto': puerto})
                json.dump(data, f, indent=4)
        return True

    def registrarLibros(self, lista, direccion):
        match = False
        with open('servidoresLibros.json', 'r+') as f:
            info = json.load(f)

            for i in info['Registro']:
                if i['direccion'] == direccion:
                    match = True
                    break

            if not(match):
                f.seek(0)
                info["Registro"].append({'direccion': direccion, 'libros': lista})
                json.dump(info, f, indent=4)
        return True


    #######
    ### CLIENTE
    #######

    # Verifica si el cliente ya se encuentra en la base de datos
    def consultarRegistro(self, user):
        with open('inscripciones.json', 'r') as archivo:
            info = json.load(archivo)

        for i in info['Registro']:
            if i['usuario'] == user:
                return True
        return False

    def consultarlogin(self, user, passw):
        with open('inscripciones.json', 'r') as archivo:
            info = json.load(archivo)

        for i in info['Registro']:
            if i['usuario'] == user and i['password'] == passw:
                return True
        return False

    # Registra el nuevo cliente
    def inscribirse(self, user, passw):
        with open('inscripciones.json', 'r+') as f:
            data = json.load(f)
            f.seek(0)
            data["Registro"].append({'usuario': user, 'password': passw})
            json.dump(data, f, indent=4)
        return True

    def solicitarListaServidores(self):
        listado = "\n"
        with open('servidoresLibros.json' ,'r') as archivo:
            info = json.load(archivo)

        for i in info['Registro']:
            listado += i["direccion"] +":\n" +i["libros"]

        return listado

    def pedirLibro(self, filename, name, ip_cliente):
        pass

    def VerLibrosDescargadosXServidor(self):
        with open('librosDescargadosxServidor.json' ,'r') as archivo:
            info = json.load(archivo)

        for i in info['Descargas']:
            print("%s     %s" % (i['libro'], i['numero']))

    def VerClientesAtendidos(self):
        with open('ClientesAtendidos.json' ,'r') as archivo:
            info = json.load(archivo)

        for i in info['Servidores']:
            print("%s     %s" % (i['direccion'], i['numero']))

    def VerServidoresCaidos(self):
        with open('ServidoresCaidos.json' ,'r') as archivo:
            info = json.load(archivo)

        for i in info['Caidos']:
            print("%s     %s" % (i['direccion'], i['numero']))


# Consola del Servidor Central
def consolaServidorCentral(s):
    terminar = False
    while not (terminar):
        print("\n1) LibrosDescargadosxServidor \n2) Nro. De clientes atendidos \n3) Servidores Caídos \n0) Salir")
        opcion = int(input(">>> "))
        if 0 <= opcion <= 3:
            if opcion == 1:
                s.VerLibrosDescargadosXServidor()
            elif opcion == 2:
                s.VerClientesAtendidos()
            elif opcion == 3:
                s.VerServidoresCaidos()
            else:
                terminar = True

# Crea los archivos del servidor
def crearArchivos():
    with open('inscripciones.json', 'a+') as f:
        if os.stat('inscripciones.json').st_size == 0:
            data = {}
            data['Registro'] = []
            json.dump(data, f)

    with open('servidoresDescargas.json', 'a+') as f:
        if os.stat('servidoresDescargas.json').st_size == 0:
            data = {}
            data['Registro'] = []
            json.dump(data, f)

    with open('servidoresLibros.json', 'a+') as f:
        if os.stat('servidoresLibros.json').st_size == 0:
            data = {}
            data['Registro'] = []
            json.dump(data, f)

    with open('librosDescargadosxServidor.json', 'a+') as f:
        if os.stat('librosDescargadosxServidor.json').st_size == 0:
            data = {}
            data['Descargas'] = []
            json.dump(data, f)

    with open('ClientesAtendidos.json', 'a+') as f:
        if os.stat('ClientesAtendidos.json').st_size == 0:
            data = {}
            data['Servidores'] = []
            json.dump(data, f)

    with open('ServidoresCaidos.json', 'a+') as f:
        if os.stat('ServidoresCaidos.json').st_size == 0:
            data = {}
            data['Caidos'] = []
            json.dump(data, f)

### Corrida del programa
if __name__ == '__main__':
    puerto = 8000
    server = SimpleXMLRPCServer(("192.168.1.140", puerto), logRequests = False) #Servidor Central
    #print(server.server_address)

    crearArchivos()

    server.register_instance(ServidorCentral())
    server.register_introspection_functions()
    s = ServidorCentral()
    start_new_thread(consolaServidorCentral, (s,))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Saliendo')
    
