import os
from fpdf import FPDF


class FacturaIELC(FPDF):

    def __init__(self, empresa="IELC", idioma="ES"):
        super().__init__()
        self.empresa = empresa
        self.idioma = idioma

    def header(self):

        if self.empresa == "CREATIVITE":

            logo = os.path.join(
                "LOGO",
                "logo_creativite.png"
            )

            info_text = (
                "SASU CREATIVITE ABSOLUE I.E\n"
                "Tour MIQUEL BD LEGETIMUS\n"
                "97110 POINTE-A-PITRE\n"
                "TEL: 0590 02 57 87\n"
                "CEL: +590 690 19 98 54\n"
                "SIRET: 954 074 373"
            )

        else:

            logo = os.path.join(
                "LOGO",
                "logo_ielc.png"
            )

            info_text = (
                "Los Rios\n"
                "Calle Primera #25\n"
                "Sector La Esperanza\n"
                "Santo Domingo Este\n"
                "(809) 979-6057\n"
                "RNC 132-60856-7"
            )

        self.image(logo, 10, 10, 55)

        self.set_xy(130, 10)

        self.set_font(
            "helvetica",
            "",
            8
        )

        self.set_text_color(
            100,
            100,
            100
        )

        self.multi_cell(
            70,
            3.5,
            info_text,
            align="R"
        )

        self.set_y(45)

    def tabla_productos(self, df_productos):

        headers = {
            "ES": [
                "Descripción",
                "Precio",
                "Cant.",
                "Subtotal"
            ],

            "FR": [
                "Description du Produit",
                "Prix",
                "Qté",
                "Sous-total"
            ]
        }

        h = headers[self.idioma]

        self.set_font(
            "helvetica",
            "B",
            10
        )

        self.set_fill_color(
            240,
            240,
            240
        )

        self.cell(80, 8, h[0], 1, 0, "C", True)
        self.cell(30, 8, h[1], 1, 0, "C", True)
        self.cell(30, 8, h[2], 1, 0, "C", True)
        self.cell(40, 8, h[3], 1, 1, "C", True)

        self.set_font(
            "helvetica",
            "",
            10
        )

        for _, fila in df_productos.iterrows():

            self.cell(
                80,
                7,
                str(fila["Producto"]),
                1
            )

            self.cell(
                30,
                7,
                f"{fila['Precio']:,.2f}",
                1,
                0,
                "R"
            )

            self.cell(
                30,
                7,
                str(fila["Cantidad"]),
                1,
                0,
                "C"
            )

            self.cell(
                40,
                7,
                f"{fila['Subtotal']:,.2f}",
                1,
                1,
                "R"
            )