from flask import Flask, request, send_file, render_template_string
from fpdf import FPDF, XPos, YPos
import pandas as pd
import datetime
import random
import os
import io
import zipfile

app = Flask(__name__)

class FacturaIELC(FPDF):

    def __init__(self, empresa="IELC", idioma="ES"):
        super().__init__()
        self.empresa = empresa
        self.idioma = idioma

    def header(self):
        info_creativite = (
            "SASU CREATIVITE ABSOLUE I.E\n"
            "Tour MIQUEL BD LEGETIMUS\n"
            "97110 POINTE-A-PITRE\n"
            "TEL: 0590 02 57 87\n"
            "CEL: +590 690 19 98 54\n"
            "SIRET: 954 074 373"
        )
        info_ielc = (
            "Los Rios\n"
            "Calle Primera #25\n"
            "Sector La Esperanza\n"
            "Santo Domingo Este\n"
            "(809) 979-6057\n"
            "RNC 132-60856-7"
        )

        logo = os.path.join("LOGO", "logo_creativite.png" if self.empresa == "CREATIVITE" else "logo_ielc.png")
        info_text = info_creativite if self.empresa == "CREATIVITE" else info_ielc

        if os.path.exists(logo):
            self.image(logo, 10, 10, 55)

        self.set_xy(130, 10)
        self.set_font("helvetica", "", 8)
        self.set_text_color(100, 100, 100)
        self.multi_cell(70, 3.5, info_text, align="R")
        self.set_y(45)

    def tabla_productos(self, df_productos):
        headers = {
            "ES": ["Descripción", "Precio", "Cant.", "Subtotal"],
            "FR": ["Description du Produit", "Prix", "Qté", "Sous-total"]
        }
        h = headers[self.idioma]

        self.set_font("helvetica", "B", 10)
        self.set_fill_color(240, 240, 240)

        self.cell(80, 8, h[0], 1, new_x=XPos.RIGHT, new_y=YPos.TOP, align="C", fill=True)
        self.cell(30, 8, h[1], 1, new_x=XPos.RIGHT, new_y=YPos.TOP, align="C", fill=True)
        self.cell(30, 8, h[2], 1, new_x=XPos.RIGHT, new_y=YPos.TOP, align="C", fill=True)
        self.cell(40, 8, h[3], 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)

        self.set_font("helvetica", "", 10)
        for _, fila in df_productos.iterrows():
            self.cell(80, 7, str(fila["Producto"]), 1, new_x=XPos.RIGHT, new_y=YPos.TOP)
            self.cell(30, 7, f"{fila['Precio']:,.2f}", 1, new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
            self.cell(30, 7, str(fila["Cantidad"]), 1, new_x=XPos.RIGHT, new_y=YPos.TOP, align="C")
            self.cell(40, 7, f"{fila['Subtotal']:,.2f}", 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")


def construir_pdf(empresa, idioma, num_fac, fecha, cliente, df, tva, manutencion, diversos, transporte, incluir_frais):
    moneda = "EUR" if empresa == "CREATIVITE" else "RD$"
    subtotal = df["Subtotal"].sum()
    
    total_frais = tva + manutencion + diversos + transporte
    total_general = subtotal + (total_frais if incluir_frais else 0)

    pdf = FacturaIELC(empresa=empresa, idioma=idioma)
    pdf.add_page()

    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, f"FACTURA: {num_fac}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 8, f"FECHA: {fecha}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 8, f"CLIENTE: {cliente}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)

    pdf.tabla_productos(df)
    pdf.ln(5)

    pdf.set_font("helvetica", "", 11)
    pdf.cell(140, 8, "TVA:", 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
    pdf.cell(40, 8, f"{tva:,.2f}" if incluir_frais else "0.00", 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

    pdf.cell(140, 8, "Manutention et Dépotage:", 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
    pdf.cell(40, 8, f"{manutencion:,.2f}" if incluir_frais else "0.00", 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

    pdf.cell(140, 8, "Marchandises Diverses:", 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
    pdf.cell(40, 8, f"{diversos:,.2f}" if incluir_frais else "0.00", 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

    # Muestra el cargo con el nombre exacto solicitado si la empresa activa es CREATIVITE
    if empresa == "CREATIVITE":
        pdf.cell(140, 8, "Frais Transport Saint-Domingue:", 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
        pdf.cell(40, 8, f"{transporte:,.2f}" if incluir_frais else "0.00", 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

    pdf.set_font("helvetica", "B", 13)
    pdf.cell(140, 10, "TOTAL GENERAL:", 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align="R")
    pdf.cell(40, 10, f"{moneda} {total_general:,.2f}", 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

    pdf.ln(20)
    y = pdf.get_y()
    pdf.line(20, y, 70, y)
    pdf.set_xy(20, y + 2)
    pdf.cell(50, 5, "Firma Cliente", new_x=XPos.RIGHT, new_y=YPos.TOP, align="C")
    pdf.line(130, y, 180, y)
    pdf.set_xy(130, y + 2)
    pdf.cell(50, 5, "Firma Autorizada", new_x=XPos.RIGHT, new_y=YPos.TOP, align="C")

    return bytes(pdf.output())


HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generador de Facturas - IELC & CREATIVITE</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary: #1a237e;
            --primary-light: #e8eaf6;
            --secondary: #0d47a1;
            --bg: #f5f7fa;
            --surface: #ffffff;
            --text: #37474f;
            --text-light: #78909c;
            --border: #cfd8dc;
            --success: #2e7d32;
            --danger: #c62828;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, sans-serif; }
        body { background-color: var(--bg); color: var(--text); padding: 2rem 1rem; line-height: 1.5; }
        .container { max-width: 700px; margin: 0 auto; }
        
        .header { text-align: center; margin-bottom: 2rem; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; padding: 2.5rem 1rem; border-radius: 16px; box-shadow: 0 4px 20px rgba(26,35,126,0.15); }
        .header h1 { font-size: 1.8rem; font-weight: 600; margin-bottom: 0.5rem; }
        .header p { color: rgba(255,255,255,0.8); font-size: 0.95rem; }

        .card { background: var(--surface); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 12px rgba(0,0,0,0.04); border: 1px solid rgba(207,216,220,0.5); }
        .card-title { font-size: 1.1rem; color: var(--primary); font-weight: 600; margin-bottom: 1.25rem; display: flex; align-items: center; gap: 0.5rem; border-bottom: 2px solid var(--primary-light); padding-bottom: 0.5rem; }

        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
        @media (max-width: 480px) { 
            .grid-2, .grid-3 { grid-template-columns: 1fr; } 
        }

        .field { margin-bottom: 1rem; display: flex; flex-direction: column; gap: 0.35rem; }
        label { font-size: 0.85rem; font-weight: 600; color: var(--text); }
        input, select { padding: 0.65rem 0.8rem; border: 1px solid var(--border); border-radius: 8px; font-size: 0.95rem; color: var(--text); transition: all 0.2s; background-color: #fafafa; }
        input:focus, select:focus { outline: none; border-color: var(--primary); background-color: #fff; box-shadow: 0 0 0 3px rgba(26,35,126,0.1); }

        .btn { width: 100%; padding: 0.8rem; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 0.5rem; transition: all 0.2s; }
        .btn-primary { background-color: var(--primary); color: white; }
        .btn-primary:hover { background-color: var(--secondary); transform: translateY(-1px); }
        .btn-secondary { background-color: var(--primary-light); color: var(--primary); }
        .btn-secondary:hover { background-color: #c5cae9; }
        .btn-danger { background-color: #ffebee; color: var(--danger); padding: 0.5rem; }
        .btn-danger:hover { background-color: #ffcdd2; }

        .product-row { display: grid; grid-template-columns: 2.5fr 1fr 1.2fr auto; gap: 0.5rem; align-items: end; background: #f8f9fa; padding: 0.75rem; border-radius: 10px; margin-bottom: 0.5rem; border: 1px dashed var(--border); }
        @media (max-width: 480px) { .product-row { grid-template-columns: 1fr; gap: 0.5rem; } }

        #lista-productos { margin-top: 0.5rem; max-height: 250px; overflow-y: auto; }
        
        .alert { padding: 1rem; border-radius: 8px; margin-top: 1rem; display: none; font-size: 0.95rem; align-items: center; gap: 0.5rem; }
        .alert-error { background-color: #ffebee; color: var(--danger); border: 1px solid #ffcdd2; }
        .alert-loading { background-color: var(--primary-light); color: var(--primary); border: 1px solid #c5cae9; }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h1><i class="fa-solid fa-file-invoice-dollar"></i> Facturación Inteligente</h1>
        <p>IELC (Dominicana) & CREATIVITE ABSOLUE (Guadalupe)</p>
    </div>

    <div class="card">
        <div class="field">
            <label><i class="fa-solid fa-building"></i> Entidad Emisora</label>
            <select id="empresa" onchange="alternarCamposEmpresa()">
                <option value="IELC">De León Import / IELC (RD$ - ES)</option>
                <option value="CREATIVITE">Creativite Absolue (EUR - FR)</option>
            </select>
        </div>
    </div>

    <div class="card">
        <div class="card-title"><i class="fa-solid fa-user"></i> Datos del Cliente</div>
        <div class="grid-2">
            <div class="field"><label>Nombre</label><input id="nombre" type="text" placeholder="Ej. Juan"></div>
            <div class="field"><label>Apellido</label><input id="apellido" type="text" placeholder="Ej. Pérez"></div>
        </div>
    </div>

    <div class="card">
        <div class="card-title"><i class="fa-solid fa-hand-holding-dollar"></i> Cargos Adicionales (Frais)</div>
        <div class="grid-3">
            <div class="field"><label>TVA</label><input id="tva" type="number" step="0.01" value="0"></div>
            <div class="field"><label>Manutention</label><input id="manutencion" type="number" step="0.01" value="0"></div>
            <div class="field"><label>Diversos</label><input id="diversos" type="number" step="0.01" value="0"></div>
        </div>
        <div class="field" id="contenedor-transporte" style="margin-top: 1rem;">
            <label>Frais Transport Saint-Domingue</label>
            <input id="transporte" type="number" step="0.01" value="0">
        </div>
    </div>

    <div class="card">
        <div class="card-title"><i class="fa-solid fa-box"></i> Productos / Servicios</div>
        <div id="lista-productos"></div>
        <button class="btn btn-secondary" style="margin-top: 1rem;" onclick="agregarFilaProducto()">
            <i class="fa-solid fa-plus"></i> Añadir Producto
        </button>
    </div>

    <button class="btn btn-primary" onclick="generarFacturas()">
        <i class="fa-solid fa-download"></i> Generar y Descargar Facturas (.ZIP)
    </button>

    <div id="alert-error" class="alert alert-error"></div>
    <div id="alert-loading" class="alert alert-loading">
        <i class="fa-solid fa-circle-notch fa-spin"></i> Procesando y empaquetando PDFs, por favor espere...
    </div>
</div>

<script>
function alternarCamposEmpresa() {
    const empresa = document.getElementById('empresa').value;
    const contenedorTransporte = document.getElementById('contenedor-transporte');
    if (empresa === 'CREATIVITE') {
        contenedorTransporte.style.display = 'flex';
    } else {
        contenedorTransporte.style.display = 'none';
        document.getElementById('transporte').value = 0;
    }
}

function agregarFilaProducto() {
    const contenedor = document.getElementById('lista-productos');
    const div = document.createElement('div');
    div.className = 'product-row';
    div.innerHTML = `
        <div class="field" style="margin:0"><label style="font-size:0.75rem">Descripción</label><input type="text" class="p-nombre" placeholder="Producto"></div>
        <div class="field" style="margin:0"><label style="font-size:0.75rem">Cant.</label><input type="number" class="p-cant" value="1" min="1"></div>
        <div class="field" style="margin:0"><label style="font-size:0.75rem">Precio</label><input type="number" class="p-precio" value="0" step="0.01"></div>
        <button class="btn btn-danger" onclick="this.parentElement.remove()"><i class="fa-solid fa-trash"></i></button>
    `;
    contenedor.appendChild(div);
}

agregarFilaProducto();
alternarCamposEmpresa();

async function generarFacturas() {
    const errorDiv = document.getElementById('alert-error');
    const loadingDiv = document.getElementById('alert-loading');
    errorDiv.style.display = 'none';
    loadingDiv.style.display = 'flex';

    try {
        const productos = [];
        const filas = document.querySelectorAll('.product-row');
        
        filas.forEach(f => {
            const nombre = f.querySelector('.p-nombre').value.trim();
            const cant = parseInt(f.querySelector('.p-cant').value) || 0;
            const precio = parseFloat(f.querySelector('.p-precio').value) || 0;
            if(nombre) {
                productos.push({ nombre, cant, precio, subtotal: cant * precio });
            }
        });

        if(productos.length === 0) {
            throw new Error("Debe agregar al menos un producto válido.");
        }

        const payload = {
            empresa: document.getElementById('empresa').value,
            nombre: document.getElementById('nombre').value.trim() || "Cliente",
            apellido: document.getElementById('apellido').value.trim() || "General",
            tva: parseFloat(document.getElementById('tva').value) || 0,
            manutencion: parseFloat(document.getElementById('manutencion').value) || 0,
            diversos: parseFloat(document.getElementById('diversos').value) || 0,
            transporte: parseFloat(document.getElementById('transporte').value) || 0,
            productos: productos
        };

        const response = await fetch('/generar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error("Error en el servidor al generar el ZIP.");

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Facturas_${payload.empresa}.zip`;
        document.body.appendChild(a);
        a.click();
        a.remove();
    } catch (e) {
        errorDiv.style.display = 'flex';
        errorDiv.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> Error: ${e.message}`;
    } finally {
        loadingDiv.style.display = 'none';
    }
}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/generar", methods=["POST"])
def generar():
    data = request.get_json()

    empresa = data["empresa"]
    idioma = "FR" if empresa == "CREATIVITE" else "ES"
    nombre = f"{data['nombre']} {data['apellido']}"
    num_fac = f"FAC-{random.randint(10000, 99999)}"
    fecha = datetime.datetime.now().strftime("%d/%m/%Y")
    tva = float(data.get("tva", 0))
    manutencion = float(data.get("manutencion", 0))
    diversos = float(data.get("diversos", 0))
    transporte = float(data.get("transporte", 0)) if empresa == "CREATIVITE" else 0.0

    df = pd.DataFrame([{
        "Producto": p["nombre"],
        "Cantidad": p["cant"],
        "Precio": p["precio"],
        "Subtotal": p["subtotal"]
    } for p in data["productos"]])

    pdf_con = construir_pdf(empresa, idioma, num_fac, fecha, nombre, df, tva, manutencion, diversos, transporte, True)
    pdf_sin = construir_pdf(empresa, idioma, num_fac, fecha, nombre, df, tva, manutencion, diversos, transporte, False)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr(f"Factura_{num_fac}_con_frais.pdf", pdf_con)
        zf.writestr(f"Factura_{num_fac}_sin_frais.pdf", pdf_sin)
    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="facturas.zip"
    )

if __name__ == "__main__":
    app.run(debug=True)
