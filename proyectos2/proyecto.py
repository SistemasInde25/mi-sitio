from flask import Flask, request, jsonify, render_template_string
import sqlite3

app = Flask(__name__)

DB = "proyectos.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cc TEXT,
            descripcion TEXT,
            nombre TEXT,
            razon_social TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def lectura():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT cc, descripcion, nombre, razon_social FROM proyectos')
    datos = c.fetchall()
    conn.close()

    html = '''
    <!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Proyectos - Lectura</title>
    <style>table {width: 100%;border-collapse: collapse;margin-top:20px;}
    th, td {border: 1px solid #ccc;padding:8px;text-align:left;}
    th {background:#f2f2f2;}
    </style></head><body>
    <h1>Tabla de Proyectos (Solo Lectura)</h1>
    <a href="/edit">Ir a edición</a>
    <table><thead><tr>
    <th>CC</th><th>Descripción</th><th>Nombre Proyecto y Desarrollo</th><th>Razón Social</th>
    </tr></thead><tbody>
    {% for fila in datos %}
      <tr>
        <td>{{ fila[0] }}</td>
        <td>{{ fila[1] }}</td>
        <td>{{ fila[2] }}</td>
        <td>{{ fila[3] }}</td>
      </tr>
    {% endfor %}
    </tbody></table>
    </body></html>
    '''
    return render_template_string(html, datos=datos)

@app.route('/edit', methods=['GET', 'POST'])
def editar():
    if request.method == 'POST':
        proyectos = request.json.get('proyectos', [])
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute('DELETE FROM proyectos')
        for fila in proyectos:
            c.execute('INSERT INTO proyectos (cc, descripcion, nombre, razon_social) VALUES (?, ?, ?, ?)', fila)
        conn.commit()
        conn.close()
        return jsonify({'status': 'ok'})

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT cc, descripcion, nombre, razon_social FROM proyectos')
    datos = c.fetchall()
    conn.close()

    html = '''
    <!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Proyectos - Edición</title>
    <style>table {width: 100%;border-collapse: collapse;margin-top:20px;}
    th, td {border: 1px solid #ccc;padding:8px;text-align:left;}
    th {background:#f2f2f2;}
    input {width: 100%;box-sizing: border-box;padding:4px;}
    .btn {margin-top:10px;padding:10px 15px;font-size:14px;cursor:pointer;}
    </style>
    </head><body>
    <h1>Tabla de Proyectos (Editable)</h1>
    <button onclick="agregarFila()" class="btn">Agregar Fila</button>
    <button onclick="guardarCambios()" class="btn">Guardar Cambios</button>
    <a href="/" class="btn" style="text-decoration:none;">Regresar a Lectura</a>
    <table><thead><tr>
    <th>CC</th><th>Descripción</th><th>Nombre Proyecto y Desarrollo</th><th>Razón Social</th>
    </tr></thead><tbody id="tabla-editable"></tbody></table>
    <script>
    let datos = {{ datos|tojson }};
    const tabla = document.getElementById('tabla-editable');

    function renderTabla(){
      tabla.innerHTML = '';
      datos.forEach((fila, i) => {
        const tr = document.createElement('tr');
        fila.forEach((valor, j) => {
          const td = document.createElement('td');
          const input = document.createElement('input');
          input.value = valor || '';
          input.oninput = () => { datos[i][j] = input.value; };
          td.appendChild(input);
          tr.appendChild(td);
        });
        tabla.appendChild(tr);
      });
    }

    function agregarFila(){
      datos.push(['', '', '', '']);
      renderTabla();
    }

    async function guardarCambios(){
      const res = await fetch('/edit', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ proyectos: datos })
      });
      if(res.ok){
        alert('Cambios guardados.');
      } else {
        alert('Error al guardar.');
      }
    }

    renderTabla();
    </script>
    </body></html>
    '''
    return render_template_string(html, datos=datos)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
