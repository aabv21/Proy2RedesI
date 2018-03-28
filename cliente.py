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

class Cliente(threading.Thread):

    def __init__(self, cliente):
        threading.Thread.__init__(self)
        self.cliente = cliente
        self.logueado = False

    def login(self):
        terminar = False
        while not(terminar):
            print("1) Loguearse \n2) Registrarse \n0) Salir")
            opcion = int(input(">>> "))
            if 0 <= opcion <= 2:
                if opcion == 1:
                    user, passw = self.datos()
                    todo_bien = self.cliente.consultarlogin(user, passw)
                    if todo_bien:
                        print("Usted se ha logueado :)\n")
                        self.logueado = True
                    else:
                        print("Usuario o password incorrecto\n")

                elif opcion == 2:
                    user, passw = self.datos()
                    todo_bien = self.cliente.consultarRegistro(user)
                    if not(todo_bien):
                        listo = self.cliente.inscribirse(user, passw)
                        print("El usuario " + str(user) + " se ha registrado exitosamente\n")
                    else:
                        print("El username "+str(user)+" ya se encuentra en la base de datos\n")

                elif opcion == 0:
                    terminar = True

    def datos(self):
        user = input("\nIntroduzca el username: ")
        passw = input("Introduzca la password: ")
        return user, passw

    def consola(self):
        terminar = False
        while not(terminar):
            print("1) LISTA_LIBROS \n2) SOLICITUD libro \n0) Salir")
            opcion = int(input(">>> "))
            if 0 <= opcion <= 2:
                if opcion == 1:
                    print("LISTA_LIBROS ")
                elif opcion == 2:
                    print("SOLICITUD libro")
                else:
                    terminar = True

    def hacerOperaciones(self):
        print(self.cliente.add(3, 2))
        print(self.cliente.system.listMethods())


def datosDelServidor():
    ip = input("Introduzca la direccion ip del servidor: ")
    return ip

def conectar(ip):
    cliente = xmlrpc.client.ServerProxy(ip)
    return cliente

### Corrida del programa
if __name__ == '__main__':

    #ip_server = datosDelServidor()
    instancia = conectar('http://localhost:8000')

    cliente = Cliente(instancia)
    cliente.start()
    cliente.login()


 
