import flet as ft
import pandas as pd
from generador_pdf import FacturaIELC
from fpdf import XPos, YPos
import datetime
import random
import os

def main(page: ft.Page):

    page.title = "Sistema de Facturación IELC & CREATIVITE"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = "#f5f7fa"

    if not os.path.exists("assets"):
        os.makedirs("assets")

    if not os.path.exists("LOGO"):
        os.makedirs("LOGO")

    lista_productos = []

    fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y")

    # -----------------------------
    # SELECTOR EMPRESA
    # -----------------------------
    empresa_select = ft.Dropdown(
        label="Seleccionar Empresa",
        width=400,
        options=[
            ft.dropdown.Option("IELC", "De León Import (Dominicana)"),
            ft.dropdown.Option("CREATIVITE", "Creativite Absolue (Guadalupe)"),
        ],
        value="IELC"
    )

    # -----------------------------
    # CLIENTE
    # -----------------------------
    nombre = ft.TextField(label="Nombre", width=195, border_radius=10)
    apellido = ft.TextField(label="Apellido", width=195, border_radius=10)
    telefono = ft.TextField(label="Teléfono", width=400, border_radius=10)

    # -----------------------------
    # PRODUCTOS
    # -----------------------------
    prod_nombre = ft.TextField(label="Producto", expand=True, border_radius=10)
    prod_cant = ft.TextField(label="Cant.", width=70, value="1", border_radius=10)
    prod_precio = ft.TextField(label="Precio", width=110, border_radius=10, prefix=ft.Text("$ "))

    # -----------------------------
    # FRAIS
    # -----------------------------
    tva_input = ft.TextField(label="TVA", width=120, value="0", border_radius=10)
    manutencion_input = ft.TextField(label="Manutention", width=130, value="0", border_radius=10)
    diversos_input = ft.TextField(label="Diversos", width=120, value="0", border_radius=10)

    # -----------------------------
    # TABLA
    # -----------------------------
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Producto")),
            ft.DataColumn(ft.Text("Subtotal"))
        ],
        rows=[]
    )

    # -----------------------------
    # AGREGAR PRODUCTO
    # -----------------------------
    def agregar_item(e):

        try:

            sub = int(prod_cant.value) * float(prod_precio.value)

            lista_productos.append({
                "Producto": prod_nombre.value,
                "Cantidad": int(prod_cant.value),
                "Precio": float(prod_precio.value),
                "Subtotal": sub
            })

            tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(prod_nombre.value)),
                    ft.DataCell(ft.Text(f"{sub:,.2f}"))
                ])
            )

            prod_nombre.value = ""
            prod_precio.value = ""
            page.update()

        except Exception as ex:

            page.snack_bar = ft.SnackBar(ft.Text(f"Error agregando producto: {ex}"))
            page.snack_bar.open = True
            page.update()

    # -----------------------------
    # GENERAR FACTURA
    # -----------------------------
    def procesar_factura(e):

        if not lista_productos:
            return

        try:

            df = pd.DataFrame(lista_productos)
            num_fac = f"FAC-{random.randint(10000, 99999)}"
            idioma = "FR" if empresa_select.value == "CREATIVITE" else "ES"
            moneda = "EUR" if empresa_select.value == "CREATIVITE" else "RD$"

            subtotal_productos = df["Subtotal"].sum()
            tva = float(tva_input.value or 0)
            manutencion = float(manutencion_input.value or 0)
            diversos = float(diversos_input.value or 0)
            total_frais = tva + manutencion + diversos

            # -----------------------------
            # FUNCIÓN INTERNA: construye un PDF
            # -----------------------------
            def construir_pdf(incluir_frais):

                pdf = FacturaIELC(empresa=empresa_select.value, idioma=idioma)
                pdf.add_page()

                pdf.set_font("helvetica", "B", 12)

                pdf.cell(0, 8, f"FACTURA: {num_fac}",
                         new_x=XPos.LMARGIN, new_y=YPos.NEXT)

                pdf.cell(0, 8, f"FECHA: {fecha_actual}",
                         new_x=XPos.LMARGIN, new_y=YPos.NEXT)

                pdf.cell(0, 8, f"CLIENTE: {nombre.value} {apellido.value}",
                         new_x=XPos.LMARGIN, new_y=YPos.NEXT)

                pdf.ln(5)
                pdf.tabla_productos(df)

                total_general = subtotal_productos + (total_frais if incluir_frais else 0)

                pdf.ln(5)

                pdf.cell(140, 8, "TVA:", 0,
                         new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
                pdf.cell(40, 8,
                         f"{tva:,.2f}" if incluir_frais else "0.00",
                         1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

                pdf.cell(140, 8, "Manutention et Dépotage:", 0,
                         new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
                pdf.cell(40, 8,
                         f"{manutencion:,.2f}" if incluir_frais else "0.00",
                         1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

                pdf.cell(140, 8, "Marchandises Diverses:", 0,
                         new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
                pdf.cell(40, 8,
                         f"{diversos:,.2f}" if incluir_frais else "0.00",
                         1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

                pdf.set_font("helvetica", "B", 13)

                pdf.cell(140, 10, "TOTAL GENERAL:", 0,
                         new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
                pdf.cell(40, 10, f"{moneda} {total_general:,.2f}",
                         1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

                return pdf

            # -----------------------------
            # GUARDAR LOS DOS PDFs
            # -----------------------------
            archivos = [
                (True,  f"Factura_{num_fac}_con_frais.pdf"),
                (False, f"Factura_{num_fac}_sin_frais.pdf"),
            ]

            for incluir_frais, nombre_archivo in archivos:
                ruta = os.path.join("/tmp", nombre_archivo)
                construir_pdf(incluir_frais).output(ruta)

            # -----------------------------
            # MENSAJE
            # -----------------------------
            page.snack_bar = ft.SnackBar(
                ft.Text(f"2 facturas generadas: {num_fac}"),
                bgcolor="green"
            )
            page.snack_bar.open = True
            page.update()

            # -----------------------------
            # DESCARGA / APERTURA
            # -----------------------------
            for _, nombre_archivo in archivos:
               page.launch_url(f"/{nombre_archivo}")

        except Exception as ex:

            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"))
            page.snack_bar.open = True
            page.update()

    # -----------------------------
    # INTERFAZ
    # -----------------------------
    page.add(

        ft.Container(

            content=ft.Column(

                [

                    ft.Text("Generador de Facturas", size=28, weight="bold"),

                    empresa_select,

                    ft.Row([nombre, apellido], alignment="center"),

                    telefono,

                    ft.Divider(),

                    ft.Row([
                        prod_nombre,
                        prod_cant,
                        prod_precio,
                        ft.IconButton(ft.Icons.ADD, on_click=agregar_item)
                    ]),

                    ft.Row(
                        [tva_input, manutencion_input, diversos_input],
                        alignment="center"
                    ),

                    ft.Container(
                        content=tabla,
                        border=ft.Border(
                            left=ft.BorderSide(1, "#eee"),
                            top=ft.BorderSide(1, "#eee"),
                            right=ft.BorderSide(1, "#eee"),
                            bottom=ft.BorderSide(1, "#eee"),
                        ),
                        padding=10
                    ),

                    ft.ElevatedButton(
                        "GENERAR FACTURA",
                        on_click=procesar_factura,
                        bgcolor="#1a237e",
                        color="white",
                        width=300,
                        height=50
                    )
                ],

                horizontal_alignment="center"
            ),

            padding=30,
            bgcolor="white",
            border_radius=15,
            width=650
        )
    )

if __name__ == "__main__":

    ft.app(
        target=main,
        assets_dir="assets",
        view=ft.AppView.WEB_BROWSER
    )
