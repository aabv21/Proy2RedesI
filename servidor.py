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

class ServidorCentral():

    def __init__(self):
        self.servidores_descarga = []

    # conectarse con el servidor de descarga
    def conectar_servidores_descarga(self, ip):
        servidor = xmlrpc.client.ServerProxy("http://"+ip) # Me comporto como cliente y me conecto con servidor de descarga
        return servidor

    # Funcion que permite conseguir el user del cliente dado su direccion ip
    def conseguirUserCliente(self, direccion_cliente, user):
        with open('inscripciones.json', 'r+') as f:
            data = json.load(f)

            for i in data['Registro']:
                if i['direccion'] == direccion_cliente and i["usuario"] == user:
                    return i["usuario"]

    """
    FUNCIONES QUE PUEDE USAR EL SERVIDOR DE DESCARGA
    """

    # Registra los servidores conectados en un .json y en un arreglo
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
        self.servidores_descarga.append(direccion+":"+str(puerto))
        return True

    # Registra los libros que posee un servidor descarga en la base de datos del servidor central
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


    """
    FUNCIONES QUE PUEDE USAR EL CLIENTE
    """

    # Verifica si el cliente ya se encuentra en la base de datos
    def consultarRegistro(self, user):
        with open('inscripciones.json', 'r') as archivo:
            info = json.load(archivo)

        for i in info['Registro']:
            if i['usuario'] == user:
                return True
        return False

    # Verifica que los datos introducidos coinciden con el de la cuenta
    def consultarlogin(self, user, passw):
        with open('inscripciones.json', 'r') as archivo:
            info = json.load(archivo)

        for i in info['Registro']:
            if i['usuario'] == user and i['password'] == passw:
                return True
        return False

    # Registra el nuevo cliente
    def inscribirse(self, user, passw, direccion_cliente):
        with open('inscripciones.json', 'r+') as f:
            data = json.load(f)
            f.seek(0)
            data["Registro"].append({'usuario': user, 'password': passw, 'direccion': direccion_cliente})
            json.dump(data, f, indent=4)
        return True

    # Solicita la lista de libros de los servidores descargas a traves del servidor central
    def solicitarListaServidores(self):
        listado = "\n"
        with open('servidoresLibros.json' ,'r') as archivo:
            info = json.load(archivo)

        for i in info['Registro']:
            listado += i["direccion"] +":\n" +i["libros"]

        return listado

    # Solicita un libro
    def pedirLibro(self, filename, direccion_cliente, size_parcial_libro, user_cliente):

        user = self.conseguirUserCliente(direccion_cliente, user_cliente)
        buffer_actual_descargado = size_parcial_libro

        for servidor_actual in self.servidores_descarga:
            servidor = self.conectar_servidores_descarga(servidor_actual) # conexion con el servidor descarga
            size_total_libro = servidor.calcularSizeTotalLibro(filename)
            binary_pdf, buffer_actual_descargado = servidor.leer_pdf(filename, user, direccion_cliente, buffer_actual_descargado) #binary data del pdf traido por el servidor descarga
            
            if size_total_libro <= buffer_actual_descargado:

                self.registrarLibrosDescargadosXServidor(servidor_actual, filename)
                self.registrarClientesAtendidos(servidor_actual)

            return binary_pdf, buffer_actual_descargado, size_total_libro

    """
    OPCIONES DE LA CONSOLA DEL SERVIDOR CENTRAL
    """  

    # Ver libros solicitados por cada servidor de descarga y el numero de veces que se ha descargado ese libro
    def VerLibrosDescargadosXServidor(self):
        print("")
        with open('librosDescargadosxServidor.json' ,'r') as archivo:
            info = json.load(archivo)

        for i in info['Descargas']:
            print("%s     %s       %s" % (i["direccion"], i['libro'], i['numero']))

    # Ver el numero de clientes atendidos por servidor de descarga
    def VerClientesAtendidos(self):
        print("")
        with open('ClientesAtendidos.json' ,'r') as archivo:
            info = json.load(archivo)

        for i in info['Servidores']:
            print("%s     %s" % (i['direccion'], i['numero']))

    # Ver cuantas veces se ha caido un servidor de desccarga
    def VerServidoresCaidos(self):
        print("")
        with open('ServidoresCaidos.json' ,'r') as archivo:
            info = json.load(archivo)

        for i in info['Caidos']:
            print("%s     %s" % (i['direccion'], i['numero']))

    #  Registrar los libros solicitados por cada servidor de descarga y el numero de veces que se ha descargado ese libro
    def registrarLibrosDescargadosXServidor(self, direccion_servidor, libro):
        match = False
        cont = 0
        with open('librosDescargadosxServidor.json', 'r+') as f:
            info = json.load(f)

            for i in info['Descargas']:
                if i['libro'] == libro and i["direccion"] == direccion_servidor:
                    aux = int(i['numero'])
                    aux += 1
                    dicc = {'libro': libro, "direccion": direccion_servidor, 'numero': str(aux)}
                    with open('librosDescargadosxServidor.json', 'r+') as f:
                        data = json.load(f)
                        f.seek(0)
                        data["Descargas"].pop(cont)
                        data["Descargas"].append(dicc)
                        json.dump(data, f, indent=4)
                    match = True
                    break
                else:
                    cont += 1

        if match == False:
            with open('librosDescargadosxServidor.json', 'r+') as f:
                data = json.load(f)
                f.seek(0)
                data["Descargas"].append({'libro': libro, "direccion" : direccion_servidor, 'numero': '1'})
                json.dump(data, f, indent=4)

    #  Registrar los clientes atendidos por servidor de descarga
    def registrarClientesAtendidos(self, direccion):
        match = False
        cont = 0
        with open('ClientesAtendidos.json', 'r+') as f:
            info = json.load(f)

            for i in info['Servidores']:
                if i['direccion'] == direccion:
                    aux = int(i['numero'])
                    aux += 1
                    dicc = {'direccion': direccion, 'numero': str(aux)}
                    with open('ClientesAtendidos.json', 'r+') as f:
                        data = json.load(f)
                        f.seek(0)
                        data["Servidores"].pop(cont)
                        data["Servidores"].append(dicc)
                        json.dump(data, f, indent=4)
                    match = True
                    break
                else:
                    cont += 1

        if match == False:
            with open('ClientesAtendidos.json', 'r+') as f:
                data = json.load(f)
                f.seek(0)
                data["Servidores"].append({'direccion': direccion, 'numero': '1'})
                json.dump(data, f, indent=4)

    #  Registrar cuantas veces se ha caido un servidor de desccarga
    def registrarServidoresCaidos(self, direccion):
        match = False
        cont = 0
        with open('ServidoresCaidos.json', 'r+') as f:
            info = json.load(f)

            for i in info['Caidos']:
                if i['direccion'] == direccion:
                    aux = int(i['numero'])
                    aux += 1
                    dicc = {'direccion': direccion, 'numero': str(aux)}
                    with open('ServidoresCaidos.json', 'r+') as f:
                        data = json.load(f)
                        f.seek(0)
                        data["Caidos"].pop(cont)
                        data["Caidos"].append(dicc)
                        json.dump(data, f, indent=4)
                    match = True
                    break
                else:
                    cont += 1

        if match == False:
            with open('ServidoresCaidos.json', 'r+') as f:
                data = json.load(f)
                f.seek(0)
                data["Caidos"].append({'direccion': direccion, 'numero': '1'})
                json.dump(data, f, indent=4)


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
    # Base de datos de los clientes
    with open('inscripciones.json', 'a+') as f:
        if os.stat('inscripciones.json').st_size == 0:
            data = {}
            data['Registro'] = []
            json.dump(data, f)

    # Base de datos de los servidores descargas
    with open('servidoresDescargas.json', 'a+') as f:
        if os.stat('servidoresDescargas.json').st_size == 0:
            data = {}
            data['Registro'] = []
            json.dump(data, f)

    # Base de datos de libros pertenecientes a cada servidor descargas
    with open('servidoresLibros.json', 'a+') as f:
        if os.stat('servidoresLibros.json').st_size == 0:
            data = {}
            data['Registro'] = []
            json.dump(data, f)

    # Base de datos de los libros solicitados por cada servidor y cuantas veces
    with open('librosDescargadosxServidor.json', 'a+') as f:
        if os.stat('librosDescargadosxServidor.json').st_size == 0:
            data = {}
            data['Descargas'] = []
            json.dump(data, f)

    # Base de datos de los clientes atendidos
    with open('ClientesAtendidos.json', 'a+') as f:
        if os.stat('ClientesAtendidos.json').st_size == 0:
            data = {}
            data['Servidores'] = []
            json.dump(data, f)

    # Base de datos de los servidores caidos
    with open('ServidoresCaidos.json', 'a+') as f:
        if os.stat('ServidoresCaidos.json').st_size == 0:
            data = {}
            data['Caidos'] = []
            json.dump(data, f)

### Corrida del programa
if __name__ == '__main__':
    puerto = 8000
    ip = input("Introduzca la direccion ip publica del servidor: ")
    server = SimpleXMLRPCServer((ip, puerto), logRequests = False) #Me levanto como un servidor (servidor central)

    crearArchivos()

    server.register_instance(ServidorCentral())
    #server.register_introspection_functions()

    s = ServidorCentral()
    t = threading.Thread(target=consolaServidorCentral, args=([s]))
    t.start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Saliendo')
    
