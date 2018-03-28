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
import sys, json, os, threading

class Servidor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

class ServidorCentral(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def consolaServidorCentral():
        terminar = False
        while not (terminar):
            print("1) LibrosDescargadosxServidor \n2) Nro. De clientes atendidos \n3) Servidores Caídos \n0) Salir")
            opcion = int(input(">>> "))
            if 0 <= opcion <= 3:
                if opcion == 1:
                    print("LibrosDescargadosxServidor\n")
                elif opcion == 2:
                    print("Nro. De clientes atendidos\n")
                elif opcion == 3:
                    print("Servidores Caídos\n")
                else:
                    terminar = True

class Cliente():

    # Funcion prueba de xml-rpc
    def add(self, x, y):
        return x + y

    def listaDeLibros(self):
        pass

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

# Crea los archivos del servidor
def crearArchivos():
    with open('inscripciones.json', 'a+') as f:
        if os.stat('inscripciones.json').st_size == 0:
            data = {}
            data['Registro'] = []
            json.dump(data, f)

### Corrida del programa
if __name__ == '__main__':
    puerto = 8000
    server = SimpleXMLRPCServer(("localhost", puerto)) #Servidor Central

    crearArchivos()

    server.register_instance(Cliente())
    server.register_introspection_functions()
    #server.register_multicall_functions()
    #server.register_function(add)
    sc = ServidorCentral()
    sc.start()

    server.serve_forever()

    print("Esperando peticiones por el puerto: "+str(puerto))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Saliendo')
    
