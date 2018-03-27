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

class Servidor:

    def add(self, x, y):
        return x + y


### Corrida del programa
server = SimpleXMLRPCServer(("localhost", 8000))

server.register_instance(Servidor())
server.register_introspection_functions()
#server.register_multicall_functions()
#server.register_function(add)
server.serve_forever()
"""
try:
      server.serve_forever()
  except KeyboardInterrerupt:
      print( Tecla de interrucion recivida. Saliendo")
      sys.exit(0)  
"""
    
