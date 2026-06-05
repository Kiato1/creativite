# =====================================================================
# MÓDULO: LEÓN IMPORT (Actualización: Sin Diversos + Factura Única)
# =====================================================================

def calcular_totales_leon_import(subtotal_productos, tva_porcentaje, manutencion_fijo):
    """
    Calcula el total general para León Import.
    SE ELIMINÓ EL CARGO DE GASTOS DIVERSOS DEL SISTEMA.
    """
    monto_tva = subtotal_productos * (tva_porcentaje / 100.0)
    
    # El total ahora solo suma Subtotal + IVA + Manutención
    total_general = subtotal_productos + monto_tva + manutencion_fijo
    
    resultados = {
        "Fecha": obtener_fecha_actual(), 
        "Subtotal_Productos": round(subtotal_productos, 2),
        "IVA_Calculado": round(monto_tva, 2),
        "Gastos_Manutencion": round(manutencion_fijo, 2),
        "TOTAL_GENERAL": round(total_general, 2)
    }
    
    return resultados

def mapear_columnas_leon_espanol(dataframe_modulo):
    """
    Mapeo de columnas optimizado. Se eliminó la columna de Diversos.
    """
    columnas_espanol = {
        'Fecha': 'Fecha',
        'Factura': 'Factura',
        'Cliente': 'Cliente',
        'Telefono5': 'Teléfono',
        'Subtotal_Prod': 'Subtotal Productos',
        'TVA': 'IVA / Impuesto',
        'Manutencion': 'Gastos de Manutención',
        'TOTAL_GENERAL': 'TOTAL GENERAL'
    }
    # Filtramos para asegurarnos de que si 'Diversos' existe en el DataFrame original, se descarte
    columnas_existentes = [col for col in dataframe_modulo.columns if col != 'Diversos']
    df_filtrado = dataframe_modulo[columnas_existentes]
    
    return df_filtrado.rename(columns=columnas_espanol)

def imprimir_factura_unica_leon(dataframe_ventas, id_factura=None):
    """
    Controla la impresión para que estrictamente se emita UNA SOLA factura.
    Si no se pasa un id_factura, por defecto toma la última del registro.
    """
    if dataframe_ventas.empty:
        print("No hay datos disponibles para imprimir.")
        return
    
    # Aplicar el filtro de columnas en español (sin diversos)
    df_espanol = mapear_columnas_leon_espanol(dataframe_ventas)
    
    # Selección de la factura única
    if id_factura:
        factura_a_imprimir = df_espanol[df_espanol['Factura'] == id_factura]
        if factura_a_imprimir.empty:
            print(f"No se encontró la factura {id_factura}. Tomando la última registrada.")
            factura_a_imprimir = df_espanol.iloc[[-1]]
    else:
        # Por defecto, toma estrictamente la última fila (la factura más reciente)
        factura_a_imprimir = df_espanol.iloc[[-1]]
    
    # --- LOGICA DE IMPRESIÓN (Aquí conectas con tu generador de PDF / Consola) ---
    print(f"=== IMPRIMIENDO FACTURA ÚNICA [LEÓN IMPORT] ===")
    for index, fila in factura_a_imprimir.iterrows():
        print(f"Factura: {fila['Factura']} | Cliente: {fila['Cliente']}")
        print(f"Subtotal: {fila['Subtotal Productos']} | Manutención: {fila['Gastos de Manutención']}")
        print(f"Total General: {fila['TOTAL GENERAL']}")
    print(f"===============================================")
    
    return factura_a_imprimir

# =====================================================================
# FIN DEL MÓDULO: LEÓN IMPORT
# =====================================================================
