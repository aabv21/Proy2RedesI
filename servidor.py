"""
    servidor.py

    Fecha: /04/2018
    Autores: Andres Buelvas     13-10184
             Salvador         
    Materia: CI-4835 Redes De Computadoras I
    Proyecto #2: Cliente-Servidor
"""
# Importaciones
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import sys, json, os
import threading

class ServidorCentral():
    """ Clase ServidorCentral que permite crear objetos de tipo ServidorCentral
    """

    # conectarse con el servidor de descarga
    def conectar_servidores_descarga(self, ip):
        """ Metodo que permite conectarse con servidores de descarga

        Este metodo recibe una direccion junto a su puerto (ej 127.0.0.1:8000). Este
        metodo intentara conectarse al servidor de descarga, si esto ocurre, entonces se 
        retorna una intancia del servidor de descarga.
        """
        servidor = xmlrpc.client.ServerProxy("http://"+ip) # Me comporto como cliente y me conecto con servidor de descarga
        return servidor

    # Funcion que a partir del nombre del archivo, me permite retornar una lista con todos los servidores descarga que lo posee
    def ListaDeServidoresConLibro(self, filename):
        """ Metodo que permite saber que servidores poseen un libro

        Este metodo a partir del nombre del libro lleva a cabo la recoleccion de todos
        los servidores descarga que lo ofrecen y los retorna a traves de un arreglo
        """
        servidores_con_el_libro = []

        with open('servidoresLibros.json', 'r+') as f:
            info = json.load(f)

            for i in info['Registro']:
                aux = i["libros"]

                aux2 = aux.split('\n')
                aux2.pop()
                for j in aux2:
                    if j == filename:
                        ip = i["direccion"] +":8000"
                        servidores_con_el_libro.append(ip)
                    else:
                        pass

        return servidores_con_el_libro

    """
    FUNCIONES QUE PUEDE USAR EL SERVIDOR DE DESCARGA
    """

    # Registra los servidores conectados en un .json
    def registrarServidores(self, direccion, puerto):
        """ Metodo que permite registrar los servidores descargas

        Este metodo recibira el nombre la direccion y puerto de escucha del
        servidor descarga
        """
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

    # Registra los libros que posee un servidor descarga en la base de datos del servidor central
    def registrarLibros(self, lista, direccion):
        """ Metodo que permite registrar los libros que ofrece cada servidor de descarga

        Este metodo recibira un string con los libros que ofrece cada servidor descarga, estos 
        se guardaran junto a la direccion IP del servidor descarga
        """
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
        """ Metodo que verifica si un cliente se cuentra en la base de datos

        Recibe el user del cliente y verifica si ya existe otro user mas con ese nombre, retorna
        un metodo que permite saber si ya se encuentra o no en la base de datos
        """
        with open('inscripciones.json', 'r') as archivo:
            info = json.load(archivo)

        for i in info['Registro']:
            if i['usuario'] == user:
                return True
        return False

    # Verifica que los datos introducidos coinciden con el de la cuenta
    def consultarlogin(self, user, passw):
        """ Metodo que verifica el user y el password

        Este metodo verifica si los datos introducidos por el cliente son los mismos
        que se introdujeron cuando se registro
        """
        with open('inscripciones.json', 'r') as archivo:
            info = json.load(archivo)

        for i in info['Registro']:
            if i['usuario'] == user and i['password'] == passw:
                return True
        return False

    # Registra el nuevo cliente
    def inscribirse(self, user, passw, direccion_cliente):
        """ Metodo que permite registrar un cliente

        Este metodo recibe el user, password y direccion IP del cliente y lo guarda
        en la base de datos
        """
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
            listado += i["direccion"] +":\n\n" +i["libros"]+"\n"

        return listado

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
    def registrarLibrosDescargadosXServidor(self, direccion_servidor, libro, user, direccion_cliente):
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

        servidor = self.conectar_servidores_descarga(direccion_servidor)
        servidor.registrarLibrosDescargados(libro)
        servidor.registrarClientesQueSolicitan(user, direccion_cliente)

        return True

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

        return True

    #  Registrar cuantas veces se ha caido un servidor de desccarga
    def registrarServidoresCaidos(self, direccion):
        match = False
        match2 = False
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

        return True

# Consola del Servidor Central
def consolaServidorCentral(s, yo):
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

    yo.shutdown()

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
    t = threading.Thread(target=consolaServidorCentral, args=([s, server]))
    t.start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Saliendo')
    
