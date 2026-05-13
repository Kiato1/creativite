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


def construir_pdf(empresa, idioma, num_fac, fecha, cliente, df, tva, manutencion, diversos, incluir_frais):
    moneda = "EUR" if empresa == "CREATIVITE" else "RD$"
    subtotal = df["Subtotal"].sum()
    total_frais = tva + manutencion + diversos
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
<title>Generador de Facturas</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #0f0f13;
    --surface: #1a1a22;
    --border: #2a2a36;
    --accent: #6c63ff;
    --accent2: #ff6584;
    --text: #e8e8f0;
    --muted: #6b6b80;
  }

  body {
    font-family: 'DM Sans', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    padding: 2rem 1rem;
  }

  .container {
    max-width: 680px;
    margin: 0 auto;
  }

  h1 {
    font-size: 1.8rem;
    font-weight: 600;
    letter-spacing: -0.03em;
    margin-bottom: 0.25rem;
  }

  .subtitle {
    color: var(--muted);
    font-size: 0.9rem;
    margin-bottom: 2rem;
  }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
  }

  .card-title {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--accent);
    margin-bottom: 1rem;
  }

  .row { display: flex; gap: 0.75rem; flex-wrap: wrap; }

  .field { display: flex; flex-direction: column; gap: 0.4rem; flex: 1; min-width: 140px; }

  label { font-size: 0.8rem; color: var(--muted); }

  input, select {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    padding: 0.6rem 0.8rem;
    transition: border-color 0.2s;
    width: 100%;
  }

  input:focus, select:focus {
    outline: none;
    border-color: var(--accent);
  }

  select option { background: var(--surface); }

  .add-row { display: flex; gap: 0.5rem; align-items: flex-end; }
  .add-row .field { flex: 1; }

  .btn {
    background: var(--accent);
    border: none;
    border-radius: 8px;
    color: white;
    cursor: pointer;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    font-weight: 500;
    padding: 0.6rem 1.2rem;
    transition: opacity 0.2s, transform 0.1s;
    white-space: nowrap;
  }

  .btn:hover { opacity: 0.85; }
  .btn:active { transform: scale(0.98); }
  .btn-danger { background: #ff4444; }

  #tabla-productos {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
    font-size: 0.85rem;
  }

  #tabla-productos th {
    color: var(--muted);
    font-weight: 500;
    padding: 0.5rem;
    text-align: left;
    border-bottom: 1px solid var(--border);
  }

  #tabla-productos td {
    padding: 0.5rem;
    border-bottom: 1px solid var(--border);
    font-family: 'DM Mono', monospace;
  }

  #tabla-productos tr:last-child td { border-bottom: none; }

  .btn-generar {
    width: 100%;
    padding: 0.9rem;
    font-size: 1rem;
    border-radius: 10px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    margin-top: 0.5rem;
  }

  .msg { text-align: center; padding: 0.75rem; border-radius: 8px; margin-top: 1rem; font-size: 0.9rem; }
  .msg.ok { background: #1a3a2a; color: #4ade80; border: 1px solid #2a5a3a; }
  .msg.err { background: #3a1a1a; color: #f87171; border: 1px solid #5a2a2a; }

  .total-preview {
    font-family: 'DM Mono', monospace;
    font-size: 1.1rem;
    color: var(--accent);
    text-align: right;
    margin-top: 0.75rem;
  }
</style>
</head>
<body>
<div class="container">
  <h1>Generador de Facturas</h1>
  <p class="subtitle">IELC & Creativite Absolue</p>

  <div class="card">
    <div class="card-title">Empresa</div>
    <div class="field">
      <select id="empresa">
        <option value="IELC">De León Import (Dominicana)</option>
        <option value="CREATIVITE">Creativite Absolue (Guadalupe)</option>
      </select>
    </div>
  </div>

  <div class="card">
    <div class="card-title">Cliente</div>
    <div class="row">
      <div class="field"><label>Nombre</label><input id="nombre" placeholder="Nombre"></div>
      <div class="field"><label>Apellido</label><input id="apellido" placeholder="Apellido"></div>
    </div>
    <div class="field" style="margin-top:0.75rem">
      <label>Teléfono</label><input id="telefono" placeholder="Teléfono">
    </div>
  </div>

  <div class="card">
    <div class="card-title">Productos</div>
    <div class="add-row">
      <div class="field"><label>Producto</label><input id="prod-nombre" placeholder="Nombre del producto"></div>
      <div class="field" style="max-width:80px"><label>Cant.</label><input id="prod-cant" type="number" value="1" min="1"></div>
      <div class="field" style="max-width:120px"><label>Precio</label><input id="prod-precio" type="number" step="0.01" placeholder="0.00"></div>
      <button class="btn" onclick="agregarProducto()">+ Añadir</button>
    </div>
    <table id="tabla-productos">
      <thead><tr><th>Producto</th><th>Cant.</th><th>Precio</th><th>Subtotal</th><th></th></tr></thead>
      <tbody id="tbody"></tbody>
    </table>
    <div class="total-preview" id="total-preview"></div>
  </div>

  <div class="card">
    <div class="card-title">Cargos Adicionales (Frais)</div>
    <div class="row">
      <div class="field"><label>TVA</label><input id="tva" type="number" step="0.01" value="0"></div>
      <div class="field"><label>Manutention et Dépotage</label><input id="manutencion" type="number" step="0.01" value="0"></div>
      <div class="field"><label>Marchandises Diverses</label><input id="diversos" type="number" step="0.01" value="0"></div>
    </div>
  </div>

  <button class="btn btn-generar" onclick="generarFacturas()">GENERAR 2 FACTURAS (ZIP)</button>
  <div id="msg"></div>
</div>

<script>
let productos = [];

function agregarProducto() {
  const nombre = document.getElementById('prod-nombre').value.trim();
  const cant = parseInt(document.getElementById('prod-cant').value);
  const precio = parseFloat(document.getElementById('prod-precio').value);

  if (!nombre || isNaN(cant) || isNaN(precio)) {
    alert('Completa todos los campos del producto');
    return;
  }

  productos.push({ nombre, cant, precio, subtotal: cant * precio });
  renderTabla();

  document.getElementById('prod-nombre').value = '';
  document.getElementById('prod-precio').value = '';
  document.getElementById('prod-cant').value = '1';
}

function eliminar(i) {
  productos.splice(i, 1);
  renderTabla();
}

function renderTabla() {
  const tbody = document.getElementById('tbody');
  tbody.innerHTML = productos.map((p, i) => `
    <tr>
      <td>${p.nombre}</td>
      <td>${p.cant}</td>
      <td>${p.precio.toLocaleString('es-DO', {minimumFractionDigits:2})}</td>
      <td>${p.subtotal.toLocaleString('es-DO', {minimumFractionDigits:2})}</td>
      <td><button class="btn btn-danger" style="padding:0.2rem 0.6rem;font-size:0.75rem" onclick="eliminar(${i})">×</button></td>
    </tr>
  `).join('');

  const total = productos.reduce((a, p) => a + p.subtotal, 0);
  document.getElementById('total-preview').textContent = productos.length ? `Subtotal: ${total.toLocaleString('es-DO', {minimumFractionDigits:2})}` : '';
}

async function generarFacturas() {
  if (!productos.length) { alert('Agrega al menos un producto'); return; }

  const msg = document.getElementById('msg');
  msg.innerHTML = '<div class="msg ok">Generando facturas...</div>';

  const data = {
    empresa: document.getElementById('empresa').value,
    nombre: document.getElementById('nombre').value,
    apellido: document.getElementById('apellido').value,
    productos: productos,
    tva: parseFloat(document.getElementById('tva').value) || 0,
    manutencion: parseFloat(document.getElementById('manutencion').value) || 0,
    diversos: parseFloat(document.getElementById('diversos').value) || 0,
  };

  try {
    const res = await fetch('/generar', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    });

    if (!res.ok) throw new Error('Error del servidor');

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'facturas.zip';
    a.click();
    URL.revokeObjectURL(url);

    msg.innerHTML = '<div class="msg ok">✓ 2 facturas descargadas correctamente</div>';
  } catch(e) {
    msg.innerHTML = `<div class="msg err">Error: ${e.message}</div>`;
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

    df = pd.DataFrame([{
        "Producto": p["nombre"],
        "Cantidad": p["cant"],
        "Precio": p["precio"],
        "Subtotal": p["subtotal"]
    } for p in data["productos"]])

    pdf_con = construir_pdf(empresa, idioma, num_fac, fecha, nombre, df, tva, manutencion, diversos, True)
    pdf_sin = construir_pdf(empresa, idioma, num_fac, fecha, nombre, df, tva, manutencion, diversos, False)

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
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
