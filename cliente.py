"""
    cliente.py

    Fecha: /04/2018
    Autores: Andres Buelvas     13-10184
             Salvador         
    Materia: CI-4835 Redes De Computadoras I
    Proyecto #2: Cliente-Servidor
"""

# Importaciones
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import socket, threading
from time import sleep

class Cliente():
    """ Clase cliente que permite crear objetos de tipo Cliente
    """

    def __init__(self, servidor, direccion):
        """ Constructor de la Clase Cliente

        Cuando es creado el objeto Cliente este almacenara como atributos su direccion IP 
        una instancia del servidor central, un detector de logins, el user y password del
        cliente que ingreso.
        """
        self.servidor_central = servidor
        self.logueado = False
        self.user = ""
        self.passw = ""
        self.direccion = direccion

    # conectarse con el servidor de descarga
    def conectar_servidores_descarga(self, ip):
        """ Metodo que permite conectarse con servidores de descarga

        Este metodo debe recibe una direccion junto a su puerto (ej 127.0.0.1:8000). Este
        metodo intentara conectarse al servidor de descarga, si esto ocurre, entonces se 
        retorna una intancia del servidor de descarga.
        """
        servidor = xmlrpc.client.ServerProxy("http://"+ip) # Me comporto como cliente y me conecto con servidor de descarga
        return servidor

    # loguearse en el servidor
    def login(self):
        """ Menu del login

        Este metodo permite loguearse o registrarse, estos datos seran pasados al servidor central
        quien validara los datos respectivos
        """
        terminar = False
        while not(terminar) and not(self.logueado):
            print("1) Loguearse \n2) Registrarse")
            opcion = int(input(">>> "))
            if 0 < opcion <= 2:
                if opcion == 1:
                    user, passw = self.datos()
                    todo_bien = self.servidor_central.consultarlogin(user, passw)
                    if todo_bien:
                        self.user, self.passw = user, passw
                        print("Usted se ha logueado :)")
                        self.logueado = True
                    else:
                        print("Usuario o password incorrecto\n")

                elif opcion == 2:
                    user, passw = self.datos()
                    todo_bien = self.servidor_central.consultarRegistro(user)
                    if not(todo_bien):
                        listo = self.servidor_central.inscribirse(user, passw, self.direccion)
                        print("El usuario " + str(user) + " se ha registrado exitosamente\n")
                    else:
                        print("El username "+str(user)+" ya se encuentra en la base de datos\n")

                else:
                    terminar = True

    # Solicita datos de inscripcion y registro
    def datos(self):
        """ Metodo que solicita el user y password respectivo por pantalla
        """
        user = input("\nIntroduzca el username: ")
        passw = input("Introduzca la password: ")
        return user, passw

    # menu del cliente
    def consola(self):
        """ Menu del cliente

        Este metodo contendra todas las opciones que puede llevar a cabo el cliente, entre estos:
        solicitar la lista de libros que ofrece cada servidor de descarga y solicitar uno o varios 
        libros.

        Este metodo trabaja con hilos, por lo tanto, las acciones se llevaran a cabo de forma concurrente
        """
        terminar = False
        while not(terminar):
            print("\n1) LISTA_LIBROS \n2) SOLICITUD libro \n0) Salir")
            opcion = int(input(">>> "))
            if 0 <= opcion <= 2:
                if opcion == 1:
                    self.recibirListaLibros()
                elif opcion == 2:
                    filename = input("Escriba el nombre del archivo: ") #Solicito el nombre del pdf (Debe llevar el .pdf)
                    lista_de_servidores = self.servidor_central.ListaDeServidoresConLibro(filename)
                    if len(lista_de_servidores) == 0:
                        print("Ningun servidor posee el libro")
                    else:
                        t = threading.Thread(target=self.recibirLibro, args=([lista_de_servidores, filename]))
                        t.start()

                else:
                    terminar = True

    def verificacionEscritura(self, direccion, lista_bool):
        """ Verifica si ya ha sido actualizado la base de datos del servirdor descarga y central

        Este metodo recibe una direccion de un servidor descarga y un arreglo de direcciones, si 
        la direccion se encuentra en el arreglo, este retorna un booleano que le dice al servidor
        descarga y servidor que si es no necesario actualizar sus base de datos.
        """
        if len(lista_bool) > 0:
            for i in lista_bool:
                if i == direccion:
                    return True
        return False

    # hilo encargado de la descarga del libro
    def recibirLibro(self, servidores_con_el_libro, filename):
        """ Metodo que se encarga de recibir el binario del libro

        Este metodo recibe un arreglo de servidores descargas que poseen el libro y el nombre del
        archivo.

        Este metodo gestiona como debe llevarse a cabo las descargas, es decir, en cuales servidores
        descargas debe llevarse a cabo el proceso. Esta accion solo es posible con los datos que el
        servidor descarga disponga, que es el unico que sabe cuanto se ha descargado del libros

        Este metodo tambien permite actualizar la base de datos de los servidores descargas y servidor
        central, es decir, una vez se haya llevado a cabo el exito de la descarga entonces este mandara
        un mensaje al servidor central y este a su vez al servidor descarga informando que la descarga
        del libro se llevo a cabo con exito

        Este metodo invoca al metodo escribir_pdf() que es el se encarga de crear el libro.

        Si los servidores descargas estan caidos, entonces se levantara una excepcion que captura el error,
        posteriormente le envia un mensaje al servidor central para que actualice su base de datos
        """

        iteraciones = len(servidores_con_el_libro)
        porcentaje = 0
        buffer_actual_descargado = 0
        se_acabo = False
        lista_bool = []

        while not(se_acabo):

            # Caso cuando el libro esta en un solo servidor de descarga
            if len(servidores_con_el_libro) == 1:
                servidor_i = servidores_con_el_libro[0]

                try:
                    servidor = self.conectar_servidores_descarga(servidor_i) # conexion con el servidor descarga
                    size_total_libro = servidor.calcularSizeTotalLibro(filename)
                    binary_pdf, buffer_actual_descargado, porcentaje = servidor.leer_pdf(filename, self.user, self.direccion, buffer_actual_descargado)
                    self.escribir_pdf(binary_pdf, filename) 

                except (xmlrpc.client.Error,  KeyboardInterrupt, ConnectionRefusedError) as v:
                    sleep(1.5)
                    servidores_con_el_libro.remove(servidor_i)
                    self.servidor_central.registrarServidoresCaidos(servidor_i)

                if buffer_actual_descargado <= size_total_libro:
                    pass

                else:
                    aux = self.verificacionEscritura(servidor_i, lista_bool)
                    if not(aux):
                        lista_bool.append(servidor_i)
                        self.servidor_central.registrarLibrosDescargadosXServidor(servidor_i, filename, self.user, self.direccion)
                        self.servidor_central.registrarClientesAtendidos(servidor_i)
                    else:
                        pass
                    se_acabo = True 

            # Caso cuando el libro esta en dos servidores de descarga    
            elif len(servidores_con_el_libro) == 2:

                if porcentaje <= 50:
                    servidor_i = servidores_con_el_libro[0]
                    try:
                        servidor = self.conectar_servidores_descarga(servidor_i) # conexion con el servidor descarga
                        size_total_libro = servidor.calcularSizeTotalLibro(filename)
                        binary_pdf, buffer_actual_descargado, porcentaje = servidor.leer_pdf(filename, self.user, self.direccion, buffer_actual_descargado)
                        self.escribir_pdf(binary_pdf, filename) 

                    except (xmlrpc.client.Error,  KeyboardInterrupt, ConnectionRefusedError) as v:
                        sleep(1.5)
                        servidores_con_el_libro.remove(servidor_i)
                        self.servidor_central.registrarServidoresCaidos(servidor_i)

                    if porcentaje >= 50:
                        aux = self.verificacionEscritura(servidor_i, lista_bool)
                        if not(aux):
                            lista_bool.append(servidor_i)
                            self.servidor_central.registrarLibrosDescargadosXServidor(servidor_i, filename, self.user, self.direccion)
                            self.servidor_central.registrarClientesAtendidos(servidor_i)
                    else:
                        pass

                elif porcentaje > 50:
                    servidor_i = servidores_con_el_libro[1]
                    try:
                        servidor = self.conectar_servidores_descarga(servidor_i) # conexion con el servidor descarga
                        size_total_libro = servidor.calcularSizeTotalLibro(filename)
                        binary_pdf, buffer_actual_descargado, porcentaje = servidor.leer_pdf(filename, self.user, self.direccion, buffer_actual_descargado)
                        self.escribir_pdf(binary_pdf, filename)

                    except (xmlrpc.client.Error,  KeyboardInterrupt, ConnectionRefusedError) as v: 
                        sleep(1.5)
                        servidores_con_el_libro.remove(servidor_i)
                        self.servidor_central.registrarServidoresCaidos(servidor_i)

                    if buffer_actual_descargado <= size_total_libro:
                        pass
                    else:
                        aux = self.verificacionEscritura(servidor_i, lista_bool)
                        if not(aux):
                            lista_bool.append(servidor_i)
                            self.servidor_central.registrarLibrosDescargadosXServidor(servidor_i, filename, self.user, self.direccion)
                            self.servidor_central.registrarClientesAtendidos(servidor_i)
                        else: 
                            pass
                        se_acabo = True

            # Caso cuando el libro esta en 3 servidores descarga
            elif len(servidores_con_el_libro) == 3:

                if porcentaje <= 33:
                    servidor_i = servidores_con_el_libro[0]
                    try:
                        servidor = self.conectar_servidores_descarga(servidor_i) # conexion con el servidor descarga
                        size_total_libro = servidor.calcularSizeTotalLibro(filename)
                        binary_pdf, buffer_actual_descargado, porcentaje = servidor.leer_pdf(filename, self.user, self.direccion, buffer_actual_descargado)
                        self.escribir_pdf(binary_pdf, filename)

                    except (xmlrpc.client.Error,  KeyboardInterrupt, ConnectionRefusedError) as v:
                        sleep(1.5)
                        servidores_con_el_libro.remove(servidor_i)
                        self.servidor_central.registrarServidoresCaidos(servidor_i)  

                    if porcentaje >= 33:
                        aux = self.verificacionEscritura(servidor_i, lista_bool)
                        if not(aux):
                            lista_bool.append(servidor_i)
                            self.servidor_central.registrarLibrosDescargadosXServidor(servidor_i, filename, self.user, self.direccion)
                            self.servidor_central.registrarClientesAtendidos(servidor_i)
                    else:
                        pass

                elif 33 < porcentaje  <= 66:
                    servidor_i = servidores_con_el_libro[1]
                    try:
                        servidor = self.conectar_servidores_descarga(servidor_i) # conexion con el servidor descarga
                        size_total_libro = servidor.calcularSizeTotalLibro(filename)
                        binary_pdf, buffer_actual_descargado, porcentaje = servidor.leer_pdf(filename, self.user, self.direccion, buffer_actual_descargado)
                        self.escribir_pdf(binary_pdf, filename)

                    except (xmlrpc.client.Error,  KeyboardInterrupt, ConnectionRefusedError) as v:
                        sleep(1.5)
                        servidores_con_el_libro.remove(servidor_i)
                        self.servidor_central.registrarServidoresCaidos(servidor_i)  

                    if porcentaje >= 66:
                        aux = self.verificacionEscritura(servidor_i, lista_bool)
                        if not(aux):
                            lista_bool.append(servidor_i)
                            self.servidor_central.registrarLibrosDescargadosXServidor(servidor_i, filename, self.user, self.direccion)
                            self.servidor_central.registrarClientesAtendidos(servidor_i)
                    else:
                        pass

                elif porcentaje  > 66:
                    servidor_i = servidores_con_el_libro[2]
                    try:
                        servidor = self.conectar_servidores_descarga(servidor_i) # conexion con el servidor descarga
                        size_total_libro = servidor.calcularSizeTotalLibro(filename)
                        binary_pdf, buffer_actual_descargado, porcentaje = servidor.leer_pdf(filename, self.user, self.direccion, buffer_actual_descargado)
                        self.escribir_pdf(binary_pdf, filename) 

                    except (xmlrpc.client.Error,  KeyboardInterrupt, ConnectionRefusedError) as v:
                        sleep(1.5)
                        servidores_con_el_libro.remove(servidor_i)
                        self.servidor_central.registrarServidoresCaidos(servidor_i)

                    if buffer_actual_descargado <= size_total_libro:
                        pass
                    else:
                        aux = self.verificacionEscritura(servidor_i, lista_bool)
                        if not(aux):
                            lista_bool.append(servidor_i)
                            self.servidor_central.registrarLibrosDescargadosXServidor(servidor_i, filename, self.user, self.direccion)
                            self.servidor_central.registrarClientesAtendidos(servidor_i)
                        else:
                            pass
                        se_acabo = True

            elif len(servidores_con_el_libro) == 0:
                print("\n>>>> NINGUN SERVIDOR SE ENCUENTRA DISPONIBLE <<<<")        
                se_acabo = True

    # recibir el binary del pdf 
    def escribir_pdf(self, pdf_binary, filename):
        """ Metodo que permite la escritura del libro 

        Este metodo recibe el binario parcial de pdf y el nombre del archivo, con estos
        datos comienza la escritura del archivo
        """
        with open(filename, "ab") as f:
            f.write(pdf_binary.data)

    # hilo encargado de imprimir en pantalla el estado de las descargas
    def recibirListaLibros(self):
        """ Metodo que permite imprimir la lista de libros ofrecidas por los servidores
        descargas a traves del servidor central
        """
        lista = self.servidor_central.solicitarListaServidores() 
        print(lista)

# Conectarse con el servidor 
def conectar(ip):
    """ Funcion que permite conectarse con el Servidor central

    Esta funcion recibe la direccion ip con el puerto (ej 127.0.0.1:8000) e intentara conectarse
    con el servidor central.
    """
    servidor = xmlrpc.client.ServerProxy(ip)
    return servidor

### Corrida del programa
if __name__ == '__main__':
    ip = input("Introduzca su direccion ip publica: ")
    ip_server = input("Introduzca la direccion ip publica del servidor central: ")
    puerto = 8000

    servidor = conectar('http://'+str(ip_server)+":"+str(puerto)) # Me comporto como cliente y me conecto con el servidor central

    cliente = Cliente(servidor, ip)
    cliente.login() #menu del login
    cliente.consola() #menu de la consola del cliente


 
