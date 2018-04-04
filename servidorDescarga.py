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
#display = threading.Event()

#
class Servidor():

    def __init__(self, servidorCentral, direccion, puerto):
        self.servidorCentral = servidorCentral
        #self.nombre = socket.gethostname()
        self.direccion = direccion
        self.puerto = puerto

    # Direccion ip del servidor que se enviara al servidor central para su bd
    def enviarDireccion(self):
        si = self.servidorCentral.registrarServidores(self.direccion, self.puerto)

    # Lista de libros que se enviaran al servidor central para su bd
    def enviarListaLibros(self):
        listado = os.popen('ls | grep pdf').read()
        #print(listado)
        si = self.servidorCentral.registrarLibros(listado, self.direccion)

    # Menu del Servidor de descarga
    def consolaServidor(self):
        terminar = False
        while not (terminar):
            print("\n1) Estado de las Descargas \n2) Libros Descargados \n3) Clientes que solicitan mas libros \n0) Salir")
            opcion = int(input(">>> "))
            if 0 <= opcion <= 3:
                if opcion == 1:
                    print("Estado de las Descargas\n")
                elif opcion == 2:
                    self.verLibrosDescargados()
                elif opcion == 3:
                    self.verClientesQueSolicitan()
                else:
                    terminar = True

    # Registrar los libros descargados 
    def registrarLibrosDescargados(self, archivo):

        match = False
        cont = 0
        with open('librosDescargados.json' ,'r') as f:
            info = json.load(f)

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

    # Para registrar los clientes que mas han solicitado 
    def registrarClientesQueSolicitan(self, user, direccion):
        match = False
        cont = 0
        with open('SolicitudesClientes.json' ,'r') as f:
            info = json.load(f)

        for i in info['Clientes']:
            if i['nombre'] == user and i['direccion'] == direccion:
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
                data["Clientes"].append({'nombre': user, 'direccion': direccion, 'numero': '1'})
                json.dump(data, f, indent=4)

    # Ver en pantalla los libros descargados y en que cantidad
    def verLibrosDescargados(self):
        with open('librosDescargados.json' ,'r') as archivo:
            info = json.load(archivo)

        for i in info['Descargas']:
            print("%s     %s" % (i['archivo'], i['numero']))

    # Ver los clientes los clientes que han hecho solicitudes 
    def verClientesQueSolicitan(self):
        with open('SolicitudesClientes.json' ,'r') as archivo:
            info = json.load(archivo)

        for i in info['Clientes']:
            print("%s     %s      %s" % (i['nombre'], i['direccion'], i['numero']))

    # Abrir el archivo .pdf en formato rbs
    #def leer_pdf(self, filename, user, direccion_cliente, fileoption="rb"):
    def leer_pdf(self, filename, direccion_cliente, fileoption="rb"):
        print("holaaaa")
        try:
            with open(filename, fileoption) as f:
                data = f.read()
                #return self.descargar_pdf(data, filename, user, direccion_cliente)
                return self.descargar_pdf(data, filename, direccion_cliente)
        except Exception as ex:
            print(ex)
            print('Error al leer el archivo')

    # Transferirir el binary data del pdf al servidor central
    def descargar_pdf(self, data, filename, direccion):

        binary_data =  xmlrpc.client.Binary(data)
        self.registrarLibrosDescargados(filename)
        #self.registrarClientesQueSolicitan(user, direccion)
        return binary_data, self.direccion

    #def descargar_pdf(self, contenido, offset, nombre_libro):

        #longitud_contenido = len(contenido)
        #enviado = offset
        #while enviado < longitud_contenido:
            #sleep(0.1)
            #status = display.wait(0.01)

            #if status:
                #porcentaje = calcularPorcentaje(longitud_contenido, enviado)
                #aux_porcentaje = "{:.2f}".format(porcentaje)
                #print("")
                #print("Descarga "+ nombre_libro + ": " + aux_porcentaje)
                #print("")

        #print("Libro enviado completamente")


# Crea los archivos del servidor
def crearArchivos():

    # Base de datos de los libros descargados y en que cantidad
    with open('librosDescargados.json', 'a+') as f:
        if os.stat('librosDescargados.json').st_size == 0:
            data = {}
            data['Descargas'] = []
            json.dump(data, f)

    # Base de datos con los clientes que solicitan libros
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
    ip = input("Introduce la direccion ip publica del servidor de descarga: ")
    instancia = conectar('http://192.168.1.140:8000') # Me comporto como cliente y me conecto con el servidor central
    server = SimpleXMLRPCServer((ip, puerto), logRequests = False) # Me levanto como servidor (servidor de descarga)
    server.register_instance(Servidor(instancia, ip, puerto))

    crearArchivos()

    servidor = Servidor(instancia, ip, puerto)
    servidor.enviarDireccion()
    servidor.enviarListaLibros()
    start_new_thread(servidor.consolaServidor, ())

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Saliendo')