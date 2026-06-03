import flet as ft
import pandas as pd
from generador_pdf import FacturaIELC
from fpdf import XPos, YPos
import datetime
import random
import os

def main(page: ft.Page):

    page.title = \"Sistema de Facturación IELC & CREATIVITE\"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = \"#f5f7fa\"

    if not os.path.exists(\"assets\"):
        os.makedirs(\"assets\")

    if not os.path.exists(\"LOGO\"):
        os.makedirs(\"LOGO\")

    lista_productos = []

    fecha_actual = datetime.datetime.now().strftime(\"%d/%m/%Y\")

    # -----------------------------
    # SELECTOR EMPRESA
    # -----------------------------
    empresa_select = ft.Dropdown(
        label=\"Seleccionar Empresa\",
        width=400,
        options=[
            ft.dropdown.Option(\"IELC\", \"De León Import (Dominicana)\"),
            ft.dropdown.Option(\"CREATIVITE\", \"Creativite Absolue (Guadalupe)\"),
        ],
        value=\"IELC\",
        on_change=lambda e: alternar_visibilidad_transporte(e)
    )

    # -----------------------------
    # CLIENTE
    # -----------------------------
    nombre = ft.TextField(label=\"Nombre\", width=195, border_radius=10)
    apellido = ft.TextField(label=\"Apellido\", width=195, border_radius=10)
    telefono = ft.TextField(label=\"Teléfono\", width=195, border_radius=10)

    # -----------------------------
    # PRODUCTO INDIVIDUAL
    # -----------------------------
    prod_nombre = ft.TextField(label=\"Nombre del Producto\", width=250, border_radius=10)
    prod_cant = ft.TextField(label=\"Cant\", width=70, value=\"1\", border_radius=10)
    prod_precio = ft.TextField(label=\"Precio\", width=100, border_radius=10)

    # -----------------------------
    # FRAIS (Campos de entrada en la UI)
    # -----------------------------
    tva_input = ft.TextField(label=\"TVA\", width=100, value=\"0\", border_radius=10)
    manutencion_input = ft.TextField(label=\"Manutention\", width=110, value=\"0\", border_radius=10)
    diversos_input = ft.TextField(label=\"Diversos\", width=100, value=\"0\", border_radius=10)
    # Corrección: Se agrega el nuevo campo de transporte oculto por defecto
    transporte_input = ft.TextField(label=\"Frais Transport\", width=110, value=\"0\", border_radius=10, visible=False)

    # Tabla Visual
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text(\"Producto\")),
            ft.DataColumn(ft.Text(\"Cant\")),
            ft.DataColumn(ft.Text(\"Precio\")),
            ft.DataColumn(ft.Text(\"Subtotal\")),
        ],
        rows=[]
    )

    def alternar_visibilidad_transporte(e):
        if empresa_select.value == \"CREATIVITE\":
            transporte_input.visible = True
        else:
            transporte_input.visible = False
            transporte_input.value = \"0\"
        page.update()

    def agregar_item(e):
        if not prod_nombre.value or not prod_precio.value:
            return

        try:
            cant = int(prod_cant.value)
            precio = float(prod_precio.value)
            subtotal = cant * precio

            lista_productos.append({
                \"Producto\": prod_nombre.value,
                \"Cantidad\": cant,
                \"Precio\": precio,
                \"Subtotal\": subtotal
            })

            tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(prod_nombre.value)),
                        ft.DataCell(ft.Text(str(cant))),
                        ft.DataCell(ft.Text(f\"{precio:,.2f}\")),
                        ft.DataCell(ft.Text(f\"{subtotal:,.2f}\")),
                    ]
                )
            )

            prod_nombre.value = \"\"
            prod_cant.value = \"1\"
            prod_precio.value = \"\"
            page.update()

        except ValueError:
            pass

    def procesar_factura(e):
        if not lista_productos:
            return

        df = pd.DataFrame(lista_productos)
        subtotal_productos = df[\"Subtotal\"].sum()

        tva = float(tva_input.value or 0)
        manutencion = float(manutencion_input.value or 0)
        diversos = float(diversos_input.value or 0)
        transporte = float(transporte_input.value or 0) if empresa_select.value == \"CREATIVITE\" else 0.0

        # Corrección: Se agrupan y suman estrictamente todos los cargos adicionales
        total_frais = tva + manutencion + diversos + transporte

        num_fac = f\"FAC-{random.randint(10000, 99999)}\"
        moneda = \"EUR\" if empresa_select.value == \"CREATIVITE\" else \"RD$\"
        idioma = \"FR\" if empresa_select.value == \"CREATIVITE\" else \"ES\"

        def construir_pdf(incluir_frais):
            pdf = FacturaIELC(empresa=empresa_select.value, idioma=idioma)
            pdf.add_page()
            pdf.set_font(\"helvetica\", \"B\", 12)

            pdf.cell(0, 8, f\"FACTURA: {num_fac}\", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(0, 8, f\"FECHA: {fecha_actual}\", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(0, 8, f\"CLIENTE: {nombre.value} {apellido.value}\", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)
            
            pdf.tabla_productos(df)
            
            total_general = subtotal_productos + (total_frais if incluir_frais else 0)

            pdf.ln(5)
            pdf.set_font(\"helvetica\", \"\", 11)
            pdf.cell(140, 8, \"TVA:\", 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align=\"R\")
            pdf.cell(40, 8, f\"{tva:,.2f}\" if incluir_frais else \"0.00\", 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align=\"R\")

            pdf.cell(140, 8, \"Manutention et Dépotage:\", 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align=\"R\")
            pdf.cell(40, 8, f"{manutencion:,.2f}\" if incluir_frais else \"0.00\", 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align=\"R\")

            pdf.cell(140, 8, \"Marchandises Diverses:\", 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align=\"R\")
            pdf.cell(40, 8, f\"{diversos:,.2f}\" if incluir_frais else \"0.00\", 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align=\"R\")

            # Corrección: Renderizar la celda de transporte en el PDF final si es Creativite
            if empresa_select.value == \"CREATIVITE\":
                pdf.cell(140, 8, \"Frais Transport:\", 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align=\"R\")
                pdf.cell(40, 8, f\"{transporte:,.2f}\" if incluir_frais else \"0.00\", 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align=\"R\")

            pdf.set_font(\"helvetica\", \"B\", 13)
            pdf.cell(140, 10, \"TOTAL GENERAL:\", 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align=\"R\")
            pdf.cell(40, 10, f\"{moneda} {total_general:,.2f}\", 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align=\"R\")

            pdf.ln(20)
            y = pdf.get_y()
            pdf.line(20, y, 70, y)
            pdf.set_xy(20, y + 2)
            pdf.cell(50, 5, "Firma Cliente", new_x=XPos.RIGHT, new_y=YPos.TOP, align="C")
            pdf.line(130, y, 180, y)
            pdf.set_xy(130, y + 2)
            pdf.cell(50, 5, "Firma Autorizada", new_x=XPos.RIGHT, new_y=YPos.TOP, align="C")

            return pdf

        pdf_con = construir_pdf(incluir_frais=True)
        pdf_con.output(os.path.join(\"assets\", f\"Factura_{num_fac}_con_frais.pdf\"))

        pdf_sin = construir_pdf(incluir_frais=False)
        pdf_sin.output(os.path.join(\"assets\", f\"Factura_{num_fac}_sin_frais.pdf\"))

        lista_productos.clear()
        tabla.rows.clear()
        nombre.value = \"\"
        apellido.value = \"\"
        telefono.value = \"\"
        tva_input.value = \"0\"
        manutencion_input.value = \"0\"
        diversos_input.value = \"0\"
        transporte_input.value = \"0\"
        page.update()

    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text(\"GENERADOR DE FACTURAS\", font_family=\"helvetica\", size=24, weight=\"bold\", color=\"#1a237e\"),
                    empresa_select,
                    ft.Divider(),
                    ft.Row([nombre, apellido, telefono], alignment=\"center\"),
                    ft.Divider(),
                    ft.Row([prod_nombre, prod_cant, prod_precio, ft.IconButton(ft.Icons.ADD, on_click=agregar_item)]),
                    # Corrección: Se añade transporte_input a la fila visual de los cargos
                    ft.Row([tva_input, manutencion_input, diversos_input, transporte_input], alignment=\"center\"),
                    ft.Container(
                        content=tabla,
                        border=ft.Border(
                            left=ft.BorderSide(1, \"#eee\"),
                            top=ft.BorderSide(1, \"#eee\"),
                            right=ft.BorderSide(1, \"#eee\"),
                            bottom=ft.BorderSide(1, \"#eee\"),
                        ),
                        padding=10
                    ),
                    ft.ElevatedButton(
                        \"GENERAR FACTURA\",
                        on_click=procesar_factura,
                        bgcolor=\"#1a237e\",
                        color=\"white\",
                        width=300,
                        height=50
                    )
                ],
                horizontal_alignment=\"center\"
            ),
            padding=30,
            bgcolor=\"white\",\n            border_radius=15,
            width=650
        )
    )

if __name__ == \"__main__\":
    ft.app(
        target=main,
        assets_dir=\"assets\",
        view=ft.AppView.WEB_BROWSER
    )
