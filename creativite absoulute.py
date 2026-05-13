import random
import datetime
# Fecha y Factura
ahora = datetime.datetime.now()
fecha_limpia = ahora.strftime("%d/%m/%Y")
print(f"Fecha: {fecha_limpia}")

prefijo = "FAC"
numero_random = random.randint(10000, 99999)
factura_final = f"{prefijo}-{numero_random}"

print(f"Número de factura: {factura_final}\n")

# Datos del Cliente
nombre_apellido1 = input("Nombre: ".capitalize())
nombre_apellido2 = input("Apellido: ".capitalize())
telefono = input("Número de teléfono: ")

# Almacenes de información
almacen_producto = []
almacen_cantidad = []
precio_unit = []
peso_de_producto = []
lista_subtotales = []
frais_tva=[]
manut_depot=[]
march_div=[]
Total=[]                   

def solicitud_articulo():
    while True:
        print("\n--- Registro de Producto ---")
        A = input("Introduce el producto (o 'salir'): ")
        if A.lower() == "salir":
            break
        
        # Validación de CANTIDAD
        while True:
            try:
                q = int(input("¿Qué cantidad?: "))
                break # Sale del mini-bucle si es un número válido
            except ValueError:
                print(">> Error: Ingresa un número entero para la cantidad.")

        # Validación de COSTO
        while True:
            try:
                c = float(input("¿Cuál es el costo por unidad?: "))
                break # Sale si es un número (acepta decimales)
            except ValueError:
                print(">> Error: Ingresa un número válido para el costo.")

        # Validación de PESO
        while True:
            try:
                p = float(input("¿Cuál es el peso del artículo?: "))
                break
            except ValueError:
                print(">> Error: Ingresa un número válido para el peso.")

        # Cálculos y Guardado
        subtotal = q * c
    
        
        almacen_producto.append(A)
        precio_unit.append(c)                
        peso_de_producto.append(p) 
        almacen_cantidad.append(q)
        lista_subtotales.append(subtotal)
        
        print(f"Subtotal: {subtotal}")


def solicitud_frais():
    print("\n----- CARGOS ADICIONALES (FRAIS) -----")
    
    tva, depot, div = 0.0, 0.0, 0.0
    
    while True:
        entrada = input("Monto de TVA (o escribe 'salir' para omitir cargos): ").lower()
        if entrada == 'salir':
            
            frais_tva.append(0.0)
            manut_depot.append(0.0)
            march_div.append(0.0)
            return 
        
        try:
            tva = float(entrada)
            depot = float(input("Monto por Manutention et Dépotage: "))
            div = float(input("Monto por Marchandises Diverses: "))
            
            frais_tva.append(tva)
            manut_depot.append(depot)
            march_div.append(div)
            break
        except ValueError:
            print(">> Error: Ingresa montos numéricos válidos.")

    
      
print("\n===== INTRODUCCIÓN DE PRODUCTOS =====")
solicitud_articulo()

print('\n===== RESUMEN DE FACTURA =====')
print(f"Cliente: {nombre_apellido1} {nombre_apellido2}")
print(f"Productos: {almacen_producto}")
print(f"Subtotales por ítem: {lista_subtotales}")
print(f"TOTAL GENERAL: {sum(lista_subtotales)}")

solicitud_frais()




