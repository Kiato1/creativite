from fpdf import FPDF, XPos, YPos

def generar_documento_final(nombre_archivo, empresa, idioma, incluir_frais, tva=0, manutencion=0, diversos=0, transporte=0):
    # Diccionario de idiomas para etiquetas dinámicas
    lang = {
        "ES": {
            "fac": "FACTURA:", "fec": "FECHA:", "cli": "CLIENTE:",
            "tva": "TVA:", "man": "Manutention et Dépotage:", "div": "Marchandises Diverses:",
            "tra": "Frais Transport Saint-Domingue:", "tot": "TOTAL GENERAL:",
            "firm_c": "Firma Cliente", "firm_a": "Firma Autorizada"
        },
        "FR": {
            "fac": "FACTURE:", "fec": "DATE:", "cli": "CLIENT:",
            "tva": "TVA:", "man": "Manutention et Dépotage:", "div": "Marchandises Diverses:",
            "tra": "Frais Transport Saint-Domingue:", "tot": "TOTAL GENERAL:",
            "firm_c": "Signature Client", "firm_a": "Signature Autorisée"
        }
    }
    
    l = lang[idioma]
    moneda = "EUR" if empresa == "CREATIVITE" else "RD$"
    
    # Cálculos matemáticos correctos
    subtotal_productos = sum(lista_subtotales)
    total_frais = tva + manutencion + diversos + transporte
    total_final = subtotal_productos + (total_frais if incluir_frais else 0)
    
    # Inicializar PDF usando la clase FacturaIELC que ya tienes definida
    pdf = FacturaIELC(empresa=empresa, idioma=idioma)
    pdf.add_page()
    
    # Datos de encabezado de Factura
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, f"{l['fac']} {factura_final}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 8, f"{l['fec']} {fecha_limpia}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 8, f"{l['cli']} {nombre_apellido1} {nombre_apellido2}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)
    
    # Reutiliza tu función interna para dibujar la tabla de ítems cargados en las listas
    # Creando un DataFrame temporal con los productos actuales en memoria
    import pandas as pd
    df_temporal = pd.DataFrame({
        "Producto": almacen_producto,
        "Cantidad": almacen_cantidad,
        "Precio": precio_unit,
        "Subtotal": lista_subtotales
    })
    pdf.tabla_productos(df_temporal)
    pdf.ln(5)
    
    # --- SECCIÓN DE CARGOS ADICIONALES (FRAIS) ---
    pdf.set_font("helvetica", "", 11)
    
    # 1. TVA
    pdf.cell(140, 8, l['tva'], 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
    pdf.cell(40, 8, f"{tva:,.2f}" if incluir_frais else "0.00", 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
    
    # 2. Manutention
    pdf.cell(140, 8, l['man'], 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
    pdf.cell(40, 8, f"{manutencion:,.2f}" if incluir_frais else "0.00", 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
    
    # 3. Diversos
    pdf.cell(140, 8, l['div'], 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
    pdf.cell(40, 8, f"{diversos:,.2f}" if incluir_frais else "0.00", 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
    
    # 4. Cargo Exclusivo de Transporte para CREATIVITE
    if empresa == "CREATIVITE":
        pdf.cell(140, 8, l['tra'], 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
        pdf.cell(40, 8, f"{transporte:,.2f}" if incluir_frais else "0.00", 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
        
    # --- TOTAL GENERAL ---
    pdf.set_font("helvetica", "B", 13)
    pdf.cell(140, 10, l['tot'], 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
    pdf.cell(40, 10, f"{moneda} {total_final:,.2f}", 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
    
    # --- SECCIÓN DE FIRMAS ---
    pdf.ln(20)
    y = pdf.get_y()
    pdf.line(20, y, 70, y)
    pdf.set_xy(20, y + 2)
    pdf.cell(50, 5, l['firm_c'], 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align="C")
    
    pdf.line(130, y, 180, y)
    pdf.set_xy(130, y + 2)
    pdf.cell(50, 5, l['firm_a'], 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    # Guardar archivo generado
    pdf.output(nombre_archivo)
    print(f">> Archivo guardado con éxito: {nombre_archivo}")
