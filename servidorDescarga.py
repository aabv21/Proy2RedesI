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
import threading
import json, os
from time import sleep
display = threading.Event()

#
class Servidor():

    def __init__(self, servidorCentral, direccion, puerto):
        self.servidorCentral = servidorCentral
        self.direccion = direccion
        self.puerto = puerto
        self.mostrar = False

    # Direccion ip del servidor que se enviara al servidor central para su bd
    def enviarDireccion(self):
        si = self.servidorCentral.registrarServidores(self.direccion, self.puerto)

    # Lista de libros que se enviaran al servidor central para su bd
    def enviarListaLibros(self):
        listado = os.popen('ls | grep pdf').read()
        si = self.servidorCentral.registrarLibros(listado, self.direccion)

    # Menu del Servidor de descarga
    def consolaServidor(self):
        terminar = False
        while not (terminar):
            print("\n1) Estado de las Descargas \n2) Libros Descargados \n3) Clientes que solicitan mas libros \n0) Salir")
            opcion = int(input(">>> "))
            if 0 <= opcion <= 3:
                if opcion == 1:
                    self.estadoDescarga()
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

        return True

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

        return True

    # Ver en pantalla los libros descargados y en que cantidad
    def verLibrosDescargados(self):
        print("")
        with open('librosDescargados.json' ,'r') as archivo:
            info = json.load(archivo)

        for i in info['Descargas']:
            print("%s     %s" % (i['archivo'], i['numero']))

    # Ver los clientes los clientes que han hecho solicitudes 
    def verClientesQueSolicitan(self):
        print("")
        with open('SolicitudesClientes.json' ,'r') as archivo:
            info = json.load(archivo)

        for i in info['Clientes']:
            print("%s     %s      %s" % (i['nombre'], i['direccion'], i['numero']))

    def calcularPorcentaje(self, total_len, current_len):
        try:
            if total_len == current_len:
                return 100
            else:
                aux = (current_len * 100)/total_len
                return aux
        except:
            return 0

    def calcularSizeTotalLibro(self, filename):
        return os.stat(filename).st_size

    # Abrir el archivo .pdf en formato rbs
    def leer_pdf(self, filename, user, direccion_cliente, buffer_actual, fileoption="rb"):
        try:
            with open(filename, fileoption) as f:
                total = self.calcularSizeTotalLibro(filename)
                faltante = total - buffer_actual
                f.seek(buffer_actual)

                if faltante >= 1024:
                    #print("rango de "+str(buffer_actual)+ " al "+str(buffer_actual+1024))
                    data = f.read(1024)
                else:
                    #print("rango de "+str(buffer_actual)+ " al "+str(buffer_actual+faltante))
                    data = f.read(faltante)

                porcentaje = self.calcularPorcentaje(total, buffer_actual)
                sleep(0.1)
                show_status = display.wait(0.01)
                if show_status: 
                    aux_porcentaje = '{:.2f}'.format(porcentaje)
                    print('Descarga ' + filename + ' en el servidor ' +self.direccion+' : ' + aux_porcentaje)

                buffer_actual = buffer_actual + 1024

                return self.descargar_pdf(data, filename, user, direccion_cliente, buffer_actual, porcentaje)
        except Exception as ex:
            print(ex)
            print('Error al leer el archivo')

    # Transferirir el binary data del pdf al servidor central
    def descargar_pdf(self, data, filename, user, direccion, buffer_actual, porcentaje):

        binary_data =  xmlrpc.client.Binary(data)
        return binary_data, buffer_actual, porcentaje

    def conseguirUser(self, direccion_cliente):
        return self.servidorCentral.userCliente(self.direccion, self.puerto)

    # Funcion que se encarga de mostrar el estado de las descargas actuales
    def estadoDescarga(self):
        self.mostrar = True
        print('\nDescargas en Curso:\n')
        display.set()
        sleep(0.5)
        display.clear()

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
    ip_server = input("Introduzca la direccion ip publica del servidor central: ")
    instancia = conectar('http://'+str(ip_server)+":"+str(puerto)) # Me comporto como cliente y me conecto con el servidor central
    server = SimpleXMLRPCServer((ip, puerto), logRequests = False) # Me levanto como servidor (servidor de descarga)
    server.register_instance(Servidor(instancia, ip, puerto))

    crearArchivos()

    servidor = Servidor(instancia, ip, puerto)
    servidor.enviarDireccion()
    servidor.enviarListaLibros()
    t = threading.Thread(target=servidor.consolaServidor)
    t.start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Saliendo')
