from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
from docxtpl import DocxTemplate
from datetime import datetime
import os

# 🔹 Importar scraper
from scraper import actualizar_convocatorias, RUTA_EXCEL

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'Salida_generada'
app.config['DATA_FOLDER'] = 'data'   # Carpeta para datos como el Excel

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)

ruta_plantilla = "plantilla.docx"

# -------------------------
# Rutas principales
# -------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/subir", methods=["GET", "POST"])
def subir_excel():
    mensaje = ""
    archivos_generados = []

    if request.method == "POST":
        archivo = request.files["archivo_excel"]
        if archivo.filename.endswith(".xlsx"):
            ruta = os.path.join(app.config['UPLOAD_FOLDER'], archivo.filename)
            archivo.save(ruta)

            try:
                xl = pd.ExcelFile(ruta)
                hoja_valida = None
                for hoja in xl.sheet_names:
                    df_temp = xl.parse(hoja)
                    if 'Nombre del proyecto' in df_temp.columns:
                        hoja_valida = hoja
                        break

                if hoja_valida:
                    df = xl.parse(hoja_valida)    
                    df.columns = df.columns.str.strip()
                    for i, datos in df.iterrows():
                        contexto = {
                            "fecha_de_hoy": datetime.today().strftime('%d/%m/%Y'),
                            "unidad": str(datos.get("Unidad", "")).strip(),
                            "nombre_proyecto": str(datos.get("Nombre del proyecto", "")).strip(),
                            "financiador": str(datos.get("Financiador", "")).strip(),
                            "aliados_externos": str(datos.get("Aliados externos", "")).strip()
                        }

                        origen = str(datos.get("Origen de la Financiación", "")).strip().lower()
                        contexto.update({
                            "publica": "✔" if "pública" in origen else "",
                            "privada": "✔" if "privada" in origen else "",
                            "ong": "✔" if "ong" in origen else "",
                            "nacional": "✔" if "nacional" in origen else "",
                            "internacional": "✔" if "internacional" in origen else "",
                            "multilateral": "✔" if "multilateral" in origen else "",
                        })

                        doc = DocxTemplate(ruta_plantilla)
                        doc.render(contexto)

                        nombre_archivo = f"Ficha_{contexto['nombre_proyecto'][:30].replace(' ', '_').replace('/', '-')}_{i}.docx"
                        ruta_final = os.path.join(app.config['OUTPUT_FOLDER'], nombre_archivo)
                        doc.save(ruta_final)
                        archivos_generados.append(nombre_archivo)

                    mensaje = f"✅ {len(archivos_generados)} documentos generados correctamente."
                else:
                    mensaje = "⚠️ No se encontró una hoja con la columna 'Nombre del proyecto'."
            except Exception as e:
                mensaje = f"⚠️ Error: {str(e)}"
        else:
            mensaje = "❌ Solo se permiten archivos .xlsx"

    return render_template("subir.html", mensaje=mensaje, archivos=archivos_generados)

@app.route("/documentos")
def documentos():
    archivos = os.listdir(app.config['OUTPUT_FOLDER'])
    return render_template("documentos.html", archivos=archivos)

@app.route("/descargar/<nombre>")
def descargar(nombre):
    ruta = os.path.join(app.config['OUTPUT_FOLDER'], nombre)
    return send_file(ruta, as_attachment=True)

@app.route("/vista-previa/<nombre>")
def vista_previa(nombre):
    ruta = os.path.join(app.config['OUTPUT_FOLDER'], nombre)
    return send_file(ruta)

@app.route("/buscador")
def buscador():
    return render_template("buscador.html")

@app.route("/alertas")
def alertas():
    return render_template("alertas.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/login")
def login():
    return render_template("login.html")

# -------------------------
# Convocatorias Minciencias
# -------------------------
@app.route("/actualizar_convocatorias")
def actualizar():
    resultado = actualizar_convocatorias(RUTA_EXCEL)
    return jsonify(resultado)

@app.route("/descargar_convocatorias")
def descargar_convocatorias():
    if os.path.exists(RUTA_EXCEL):
        return send_file(RUTA_EXCEL, as_attachment=True)
    return jsonify({"status": "error", "mensaje": "❌ No se encontró el archivo Excel"}), 404

# -------------------------
# API para análisis
# -------------------------
@app.route("/api/analisis")
def api_analisis():
    ruta_archivo = os.path.join(app.config['DATA_FOLDER'], "convocatorias_minciencias.xlsx")

    paginas = ["MinCiencias"]
    existentes = []
    nuevas = []

    try:
        df = pd.read_excel(ruta_archivo)

        # Total convocatorias
        existentes.append(len(df))

        # Convocatorias nuevas
        if "Estado" in df.columns:
            nuevas.append(df[df["Estado"].str.lower() == "nueva"].shape[0])
        else:
            nuevas.append(0)

    except Exception as e:
        print(f"⚠️ Error leyendo Excel de MinCiencias: {e}")
        existentes.append(0)
        nuevas.append(0)

    return jsonify({
        "paginas": paginas,
        "existentes": existentes,
        "nuevas": nuevas
    })

# -------------------------
# Página de análisis
# -------------------------
@app.route("/analisis")
def analisis():
    return render_template("analisis.html")

# -------------------------
if __name__ == "__main__":
    # En Render se usa el puerto 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)





