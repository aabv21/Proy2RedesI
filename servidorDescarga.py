"""
    servidorDescarga.py

    Fecha: 12/04/2018
    Autores: Andres Buelvas     13-10184
             Salvador Covelo    10-10164  
    Materia: CI-4835 Redes De Computadoras I
    Proyecto #2: Cliente-Servidor
"""

# Importaciones
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import threading
import json, os
from time import sleep
import sys
display = threading.Event()

#
class Servidor():
    """ Clase Servidor que permite crear objetos de tipo Servidor
    """

    def __init__(self, servidorCentral, direccion, puerto):
        """ Constructor de la Clase Servidor

        Cuando es creado el objeto Servidor este almacenara como atributos su direccion IP 
        una instancia del servidor central, el puerto de escucha y un atributo booleano
        que permitira mostrar los eventos de los hilos
        """
        self.servidorCentral = servidorCentral
        self.direccion = direccion
        self.puerto = puerto
        self.mostrar = False

    # Direccion ip del servidor que se enviara al servidor central para su bd
    def enviarDireccion(self):
        """ Envia la direccion ip y puerto al servidor central
        """
        si = self.servidorCentral.registrarServidores(self.direccion, self.puerto)

    # Lista de libros que se enviaran al servidor central para su bd
    def enviarListaLibros(self):
        """ Envia la lista de libros que ofrece al servidor central
        """
        listado = os.popen('ls | grep pdf').read()
        si = self.servidorCentral.registrarLibros(listado, self.direccion)

    # Menu del Servidor de descarga
    def consolaServidor(self, yo):
        """ Menu del Servidor descarga

        Este metodo recibira una intancia propia que permitira apagar el servidor cuando sea solicitado

        Este metodo contendra todas las opciones que puede llevar a cabo el servidor descarga, entre estos:
        ver el estado de las descargas actuales, una estadistica de los cuantos libros fueron descargados y 
        una estadistica de cuantas descargas hechas por los clientes
        """
        terminar = False
        while not (terminar):
            print("\n### Servidor Descarga "+ self.direccion+ " ###")
            print("1) Estado de las Descargas \n2) Libros Descargados \n3) Clientes que solicitan mas libros \n0) Salir")
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
        yo.shutdown()

    # Registrar los libros descargados 
    def registrarLibrosDescargados(self, archivo):
        """ Metodo que permite registrar los libros descargados

        Este metodo recibira el nombre del archivo. Este metodo verificara cuantas veces 
        se ha descargado un libro en este servidor.
        """
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
        """ Metodo que permite registrar los clientes que han solicitado libros

        Este metodo recibira el user y direccion IP del cliente. Este metodo verificara
        cuantas veces un cliente ha descargado un libro.
        """
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
        """ Este metodo permite visualizar los libros descargados
        """
        print("")
        with open('librosDescargados.json' ,'r') as archivo:
            info = json.load(archivo)

        for i in info['Descargas']:
            print("%s     %s" % (i['archivo'], i['numero']))

    # Ver los clientes los clientes que han hecho solicitudes 
    def verClientesQueSolicitan(self):
        """ Este metodo permite visualizar cuantos y cuales clientes han descargado
        """
        print("")
        with open('SolicitudesClientes.json' ,'r') as archivo:
            info = json.load(archivo)

        for i in info['Clientes']:
            print("%s     %s      %s" % (i['nombre'], i['direccion'], i['numero']))

    def calcularPorcentaje(self, total_len, current_len):
        """ Metodo que calcula el porcentaje de traspaso del libro al cliente

        Este metodo recibe constantemente el size total del libro y size parcial que
        se ha transferido y posteriormente hara los calculos para saber el porcentaje
        de descarga actual
        """
        try:
            if total_len == current_len:
                return 100
            else:
                aux = (current_len * 100)/total_len
                return aux
        except:
            return 0

    def calcularSizeTotalLibro(self, filename):
        """ Metodo que permite calcular el size total de un archivo
        """
        return os.stat(filename).st_size

    # Abrir el archivo .pdf en formato rb
    def leer_pdf(self, filename, user, direccion_cliente, buffer_actual, fileoption="rb"):
        """ Metodo encargado de transferir los bytes del libro al cliente

        Este metodo recibe el nombre del archivo, el user del cliente, la direccion IP del cliente,
        el size parcial transferido. Este metodo enviara el libro de 1024 en 1024 bytes en cada iteracion.

        Este metodo le retorna al metodo descargar_pdf() la data (1024 bytes) transferida en una iteracion, el nombre del
        libro, el user y direccion del cliente, el size parcial que se lleva calculado hasta esa iteracion
        y el porcentaje de descarga realizado
        """

        try:
            with open(filename, fileoption) as f:
                total = self.calcularSizeTotalLibro(filename)
                faltante = total - buffer_actual
                f.seek(buffer_actual)

                if faltante >= 1024:
                    data = f.read(1024)
                else:
                    data = f.read(faltante)

                porcentaje = self.calcularPorcentaje(total, buffer_actual)
                sleep(0.1)
                show_status = display.wait(0.01)
                if show_status: 
                    aux_porcentaje = '{:.2f}'.format(porcentaje)
                    print('Descarga por parte del usuario ' +str(user)+ " el archivo "+ filename + ' : ' + aux_porcentaje)

                buffer_actual = buffer_actual + 1024

                return self.descargar_pdf(data, filename, user, direccion_cliente, buffer_actual, porcentaje)
        except Exception as ex:
            print(ex)
            print('Error al leer el archivo')

    # Transferirir el binary data del pdf al servidor central
    def descargar_pdf(self, data, filename, user, direccion, buffer_actual, porcentaje):
        """ Metodo que se encarga de encapsular el binario del libro

        Este metodo le envia al cliente a traves del metodo ofrecido por
        XMLRPC para el encapsulamiento de binarios, los bytes transferidos
        """

        binary_data =  xmlrpc.client.Binary(data)
        return binary_data, buffer_actual, porcentaje

    def conseguirUser(self, direccion_cliente):
        """ Metodo que permite conseguir el user del cliente que lleva a cabo la descarga
        """
        return self.servidorCentral.userCliente(self.direccion, self.puerto)

    # Funcion que se encarga de mostrar el estado de las descargas actuales
    def estadoDescarga(self):
        """ Metodo que permite visualizar el estado de la descarga

        Este meodo se realiza de forma concurrente a traves de hilos
        """
        self.mostrar = True
        print('\nDescargas en Curso:\n')
        display.set()
        sleep(0.5)
        display.clear()

# Crea los archivos del servidor
def crearArchivos():
    """ Metodo que premite la creacion de los .json

    Este metodo creara los .json del servidor que mantendra de manera permanente
    las estadisticas del servidor descarga
    """

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
    """ Funcion que permite conectarse con el Servidor central

    Esta funcion recibe la direccion ip con el puerto (ej 127.0.0.1:8000) e intentara conectarse
    con el servidor central.
    """
    cliente = xmlrpc.client.ServerProxy(ip)
    return cliente

### Corrida del programa
if __name__ == '__main__':

    puerto = 8000
    ip = input("Introduce la direccion ip publica del servidor de descarga: ")
    ip_server = input("Introduzca la direccion ip publica del servidor central: ")
    instancia = conectar('http://'+str(ip_server)+":"+str(puerto)) # Me comporto como cliente y me conecto con el servidor central
    server = SimpleXMLRPCServer((ip, puerto), logRequests = False) # Me levanto como servidor (servidor de descarga)
    server.register_instance(Servidor(instancia, ip, puerto)) # Metodos que ofrecere como servidor a mis clientes

    crearArchivos()

    servidor = Servidor(instancia, ip, puerto)
    servidor.enviarDireccion() #Enviar direccion y puerto al servidor central
    servidor.enviarListaLibros() #Enviar lista de libros al servidor central
    t = threading.Thread(target=servidor.consolaServidor, args=([server])) #Creacion del hilo
    t.start() #Inicio del hilo

    try:
        server.serve_forever() #Ciclo infinito del hilo
    except KeyboardInterrupt:
        print('Saliendo')
