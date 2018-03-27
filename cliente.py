"""
    
    cliente.py

    Fecha: /04/2018
    Autor: Andres Buelvas
    carnet: 13-10184
    Materia: CI-4835 Redes De Computadoras I
    Proyecto #2: Cliente-Servidor

"""

import xmlrpc.client

### Corrida del programa
cliente = xmlrpc.client.ServerProxy("http://localhost:8000/")
print(cliente.add(3,2))
print(cliente.system.listMethods())



 
