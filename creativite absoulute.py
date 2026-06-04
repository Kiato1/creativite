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
frais_tva = []
manut_depot = []
march_div = []
frais_transport_sd = []  # Nombre interno asignado para la lista
Total = []                   

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
                break 
            except ValueError:
                print(">> Error: Ingresa un número entero para la cantidad.")

        # Validación de COSTO
        while True:
            try:
                c = float(input("¿Cuál es el costo por unidad?: "))
                break 
            except ValueError:
                print(">> Error: Ingresa un monto numérico para el costo.")

        # Validación de PESO
        while True:
            try:
                p = float(input("¿Cuál es el peso en kg?: "))
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
    
    tva, depot, div, transport_sd = 0.0, 0.0, 0.0, 0.0
    
    while True:
        entrada = input("Monto de TVA (o escribe 'salir' para omitir cargos): ").lower()
        if entrada == 'salir':
            frais_tva.append(0.0)
            manut_depot.append(0.0)
            march_div.append(0.0)
            frais_transport_sd.append(0.0)
            return 
        
        try:
            tva = float(entrada)
            depot = float(input("Monto por Manutention et Dépotage: "))
            div = float(input("Monto por Marchandises Diverses: "))
            # Nombre de la etiqueta exacto solicitado en consola
            transport_sd = float(input("Monto por Frais Transport Saint-Domingue: ")) 
            
            frais_tva.append(tva)
            manut_depot.append(depot)
            march_div.append(div)
            frais_transport_sd.append(transport_sd)
            break
        except ValueError:
            print(">> Error: Ingresa montos numéricos válidos.")

      
print("\n===== INTRODUCCIÓN DE PRODUCTOS =====")
solicitud_articulo()

# Solicitar los cargos adicionales
solicitud_frais()

# ---------------------------------------------------------
# CÁLCULO Y RESUMEN FINAL CON LOS FRAIS SUMADOS
# ---------------------------------------------------------
subtotal_productos = sum(lista_subtotales)
total_frais = sum(frais_tva) + sum(manut_depot) + sum(march_div) + sum(frais_transport_sd)
total_general_con_frais = subtotal_productos + total_frais

print("\n===== RESUMEN DE FACTURA =====")
print(f"Cliente: {nombre_apellido1} {nombre_apellido2}")
print(f"Teléfono: {telefono}")
print(f"Productos registrados: {almacen_producto}")
print(f"Subtotal Productos: {subtotal_productos:,.2f}")
print(f"Total Cargos Adicionales (Frais): {total_frais:,.2f}")
print(f"TOTAL GENERAL (Con Frais): {total_general_con_frais:,.2f}")
