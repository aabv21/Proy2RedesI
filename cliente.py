"""
    cliente.py

    Fecha: /04/2018
    Autor: Andres Buelvas
    carnet: 13-10184
    Materia: CI-4835 Redes De Computadoras I
    Proyecto #2: Cliente-Servidor
"""

from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import socket, threading, time

class Cliente():

    def __init__(self, servidor, direccion):
        self.servidor_central = servidor
        self.logueado = False
        self.user = ""
        self.passw = ""
        #self.name = ""
        self.direccion = direccion

    # loguearse en el servidor
    def login(self):
        terminar = False
        while not(terminar) and not(self.logueado):
            print("1) Loguearse \n2) Registrarse \n0) Salir")
            opcion = int(input(">>> "))
            if 0 <= opcion <= 2:
                if opcion == 1:
                    user, passw = self.datos()
                    todo_bien = self.servidor_central.consultarlogin(user, passw)
                    if todo_bien:
                        self.user, self.passw = user, passw
                        #self.name = socket.gethostname()
                        #self.direccion = socket.gethostbyname(self.name)
                        print("Usted se ha logueado :)\n")
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

                elif opcion == 0:
                    terminar = True

    # Solicita datos de inscripcion y registro
    def datos(self):
        user = input("\nIntroduzca el username: ")
        passw = input("Introduzca la password: ")
        return user, passw

    # menu del cliente
    def consola(self):
        terminar = False
        while not(terminar):
            print("1) LISTA_LIBROS \n2) SOLICITUD libro \n0) Salir")
            opcion = int(input(">>> "))
            if 0 <= opcion <= 2:
                if opcion == 1:
                    lista = self.servidor_central.solicitarListaServidores() 
                    print(lista)
                elif opcion == 2:
                    filename = input("Escriba el nombre del archivo: ")
                    pdf_binary = self.servidor_central.pedirLibro(filename, self.direccion)
                    self.recibir_pdf(pdf_binary, filename)
                else:
                    terminar = True

    # recibir el binary del pdf 
    def recibir_pdf(self, pdf_binary, filename):
        with open(filename, "wb") as f:
            f.write(pdf_binary.data)

# Direccion del servidor
def datosDelServidor():
    ip = input("Introduzca la direccion ip del servidor: ")
    return ip

# Conectarse con el servidor 
def conectar(ip):
    servidor = xmlrpc.client.ServerProxy(ip)
    return servidor

### Corrida del programa
if __name__ == '__main__':
    ip = input("Introduzca su direccion ip publica: ")

    #ip_server = datosDelServidor()
    servidor = conectar('http://192.168.1.140:8000') # Me comporto como cliente y me conecto con el servidor central

    cliente = Cliente(servidor, ip)
    cliente.login()
    cliente.consola()


 
