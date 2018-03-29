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

class Servidor():

    def __init__(self, servidorCentral, puerto):
        self.servidorCentral = servidorCentral
        self.nombre = socket.gethostname()
        self.direccion = socket.gethostbyname(self.nombre)
        self.puerto = puerto

    def enviarDireccion(self):
        self.servidorCentral.registrarServidores(self.direccion, self.puerto)

    def enviarListaLibros(self):
        listado = os.popen('ls | grep pdf').read()
        return "libros del "+self.direccion+":\n"+listado

def conectar(ip):
    cliente = xmlrpc.client.ServerProxy(ip)
    return cliente

### Corrida del programa
if __name__ == '__main__':

    puerto = 8000
    #ip_server = datosDelServidor()
    instancia = conectar('http://localhost:8000')

    servidor = Servidor(instancia, puerto)