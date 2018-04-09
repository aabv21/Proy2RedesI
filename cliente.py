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
        self.direccion = direccion

    # conectarse con el servidor de descarga
    def conectar_servidores_descarga(self, ip):
        servidor = xmlrpc.client.ServerProxy("http://"+ip) # Me comporto como cliente y me conecto con servidor de descarga
        return servidor

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

    # hilo encargado de la descarga del libro
    def recibirLibro(self, servidores_con_el_libro, filename):

        iteraciones = len(servidores_con_el_libro)
        porcentaje = 0
        buffer_actual_descargado = 0
        se_acabo = False

        while not(se_acabo):

            # Caso cuando el libro esta en un solo servidor de descarga
            if iteraciones == 1:
                servidor_i = servidores_con_el_libro[0]
                servidor = self.conectar_servidores_descarga(servidor_i) # conexion con el servidor descarga
                binary_pdf, buffer_actual_descargado, porcentaje = servidor.leer_pdf(filename, self.user, self.direccion, buffer_actual_descargado)
                size_total_libro = servidor.calcularSizeTotalLibro(filename)
                self.escribir_pdf(binary_pdf, filename) 

                if buffer_actual_descargado <= size_total_libro:
                    pass

                else:
                    se_acabo = True 
                    self.servidor_central.registrarLibrosDescargadosXServidor(servidor_i, filename, self.user)
                    self.servidor_central.registrarClientesAtendidos(servidor_i)

            # Caso cuando el libro esta en dos servidores de descarga    
            elif iteraciones == 2:

                if porcentaje <= 50:
                    servidor_i = servidores_con_el_libro[0]
                    servidor = self.conectar_servidores_descarga(servidor_i) # conexion con el servidor descarga
                    binary_pdf, buffer_actual_descargado, porcentaje = servidor.leer_pdf(filename, self.user, self.direccion, buffer_actual_descargado)
                    size_total_libro = servidor.calcularSizeTotalLibro(filename)
                    self.escribir_pdf(binary_pdf, filename) 

                    if porcentaje >= 50:
                        self.servidor_central.registrarLibrosDescargadosXServidor(servidor_i, filename, self.user)
                        self.servidor_central.registrarClientesAtendidos(servidor_i)
                    else:
                        pass

                elif porcentaje > 50:
                    servidor_i = servidores_con_el_libro[1]
                    servidor = self.conectar_servidores_descarga(servidor_i) # conexion con el servidor descarga
                    binary_pdf, buffer_actual_descargado, porcentaje = servidor.leer_pdf(filename, self.user, self.direccion, buffer_actual_descargado)
                    size_total_libro = servidor.calcularSizeTotalLibro(filename)
                    self.escribir_pdf(binary_pdf, filename) 

                    if buffer_actual_descargado <= size_total_libro:
                        pass
                    else:
                        self.servidor_central.registrarLibrosDescargadosXServidor(servidor_i, filename, self.user)
                        self.servidor_central.registrarClientesAtendidos(servidor_i)
                        se_acabo = True

            # Caso cuando el libro esta en 3 servidores descarga
            elif iteraciones == 3:

                if porcentaje <= 33:
                    servidor_i = servidores_con_el_libro[0]
                    servidor = self.conectar_servidores_descarga(servidor_i) # conexion con el servidor descarga
                    binary_pdf, buffer_actual_descargado, porcentaje = servidor.leer_pdf(filename, self.user, self.direccion, buffer_actual_descargado)
                    size_total_libro = servidor.calcularSizeTotalLibro(filename)
                    self.escribir_pdf(binary_pdf, filename) 

                    if porcentaje >= 33:
                        self.servidor_central.servidorregistrarLibrosDescargadosXServidor(servidor_i, filename, self.user)
                        self.servidor_central.registrarClientesAtendidos(servidor_i)
                    else:
                        pass

                elif 33 < porcentaje  <= 66:
                    servidor_i = servidores_con_el_libro[1]
                    servidor = self.conectar_servidores_descarga(servidor_i) # conexion con el servidor descarga
                    binary_pdf, buffer_actual_descargado, porcentaje = servidor.leer_pdf(filename, self.user, self.direccion, buffer_actual_descargado)
                    size_total_libro = servidor.calcularSizeTotalLibro(filename)
                    self.escribir_pdf(binary_pdf, filename) 

                    if porcentaje >= 66:
                        self.servidor_central.registrarLibrosDescargadosXServidor(servidor_i, filename, self.user)
                        self.servidor_central.registrarClientesAtendidos(servidor_i)
                    else:
                        pass

                elif porcentaje  > 66:
                    servidor_i = servidores_con_el_libro[2]
                    servidor = self.conectar_servidores_descarga(servidor_i) # conexion con el servidor descarga
                    binary_pdf, buffer_actual_descargado, porcentaje = servidor.leer_pdf(filename, self.user, self.direccion, buffer_actual_descargado)
                    size_total_libro = servidor.calcularSizeTotalLibro(filename)
                    self.escribir_pdf(binary_pdf, filename) 

                    if buffer_actual_descargado <= size_total_libro:
                        pass
                    else:
                        self.servidor_central.registrarLibrosDescargadosXServidor(servidor_i, filename, self.user)
                        self.servidor_central.registrarClientesAtendidos(servidor_i)
                        se_acabo = True

    # recibir el binary del pdf 
    def escribir_pdf(self, pdf_binary, filename):
        with open(filename, "ab") as f:
            f.write(pdf_binary.data)

    # hilo encargado de imprimir en pantalla el estado de las descargas
    def recibirListaLibros(self):
        lista = self.servidor_central.solicitarListaServidores() 
        print(lista)

# Conectarse con el servidor 
def conectar(ip):
    servidor = xmlrpc.client.ServerProxy(ip)
    return servidor

### Corrida del programa
if __name__ == '__main__':
    ip = input("Introduzca su direccion ip publica: ")
    ip_server = input("Introduzca la direccion ip publica del servidor central: ")
    puerto = 8000

    servidor = conectar('http://'+str(ip_server)+":"+str(puerto)) # Me comporto como cliente y me conecto con el servidor central

    cliente = Cliente(servidor, ip)
    cliente.login()
    cliente.consola()


 
