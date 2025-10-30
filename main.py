import json
import os
import datetime
import uuid
import pandas as pd
from dateutil.relativedelta import relativedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="static")
CORS(app)

@app.route("/")
def serve_html():
    return send_from_directory(app.static_folder, "milhover_pet.html")

@app.route("/ping")
def ping():
    return jsonify({"status": "pong"}), 200

# Inicialización protegida
def ensure_data_dir():
    print("✅ ensure_data_dir ejecutado")

def initialize_data():
    print("✅ initialize_data ejecutado")

try:
    ensure_data_dir()
    initialize_data()
    print("✅ Inicialización completada")
except Exception as e:
    print(f"❌ Error en inicialización: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Servidor Flask iniciado en http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)



# Define la carpeta donde se guardarán los datos
DATA_DIR = 'datos'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
INGRESOS_FILE = os.path.join(DATA_DIR, 'ingresos.json')
GASTOS_FILE = os.path.join(DATA_DIR, 'gastos.json')
PRECIOS_FILE = os.path.join(DATA_DIR, 'precios.json')
COSTOS_FILE = os.path.join(DATA_DIR, 'costos.json')
STOCK_FILE = os.path.join(DATA_DIR, 'stock.json')
PEDIDOS_FILE = os.path.join(DATA_DIR, 'pedidos.json')
CLIENTES_FILE = os.path.join(DATA_DIR, 'clientes.json')
RAPPI_BANCO_FILE = os.path.join(DATA_DIR, 'rappi_banco.json')
VENCIMIENTOS_FILE = os.path.join(DATA_DIR, 'vencimientos.json')
PROVEEDORES_FILE = os.path.join(DATA_DIR, 'proveedores.json')

# Función auxiliar para asegurar que la carpeta de datos existe
def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

# Función auxiliar para leer datos de un archivo JSON
def read_data(filepath, default_value=None):
    if default_value is None:
        if filepath == GASTOS_FILE:
            default_value = {}
        elif filepath == COSTOS_FILE:
            default_value = {"ingredientes": [], "hamburguesas": []}
        elif filepath == STOCK_FILE:
            default_value = []
        else:
            default_value = []

    ensure_data_dir()
    if not os.path.exists(filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(default_value, f, indent=4, ensure_ascii=False)
        return default_value
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return default_value

# Función auxiliar para escribir datos en un archivo JSON
def write_data(filepath, data):
    ensure_data_dir()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Inicializa los archivos de datos si no existen
def initialize_data():
    read_data(USERS_FILE, default_value=[{"usuario": "admin", "contrasena": "admin", "rol": "admin", "frase_bienvenida": "¡Bienvenido, Admin!"}])
    read_data(INGRESOS_FILE)
    read_data(GASTOS_FILE)
    read_data(PRECIOS_FILE)
    read_data(COSTOS_FILE)
    read_data(STOCK_FILE)
    read_data(PEDIDOS_FILE)
    read_data(CLIENTES_FILE)
    read_data(VENCIMIENTOS_FILE)
    read_data(PROVEEDORES_FILE)

# --- Rutas de la API ---

@app.route('/api/data', methods=['GET'])
def get_all_data():
    data = {
        'users': read_data(USERS_FILE),
        'ingresos': read_data(INGRESOS_FILE),
        'gastos': read_data(GASTOS_FILE),
        'precios': read_data(PRECIOS_FILE),
        'costos': read_data(COSTOS_FILE),
        'stock': read_data(STOCK_FILE),
        'pedidos': read_data(PEDIDOS_FILE),
        'clientes': read_data(CLIENTES_FILE),
        'vencimientos': read_data(VENCIMIENTOS_FILE),
        'proveedores': read_data(PROVEEDORES_FILE)
    }
    return jsonify(data), 200

# --- Rutas para Usuarios ---
@app.route('/api/data/users/authenticate', methods=['POST'])
def authenticate_user():
    credentials = request.json
    username = credentials.get('username')
    password = credentials.get('password')
    users = read_data(USERS_FILE)
    user = next((u for u in users if u['usuario'] == username and u['contrasena'] == password), None)
    if user:
        return jsonify({"user": {"usuario": user['usuario'], "rol": user['rol'], "frase_bienvenida": user.get('frase_bienvenida', f"¡Bienvenido, {user['usuario']}!")}}), 200
    else:
        return jsonify({"error": "Credenciales inválidas"}), 401

@app.route('/api/data/users', methods=['POST'])
def create_user():
    new_user_data = request.json
    if not new_user_data.get('usuario') or not new_user_data.get('contrasena'):
        return jsonify({"error": "Usuario y contraseña son obligatorios."}), 400
    users = read_data(USERS_FILE)
    if any(u['usuario'] == new_user_data['usuario'] for u in users):
        return jsonify({"error": "El nombre de usuario ya existe."}), 409
    users.append(new_user_data)
    write_data(USERS_FILE, users)
    return jsonify({"message": "Usuario creado exitosamente."}), 201

@app.route('/api/data/users/<username>', methods=['PUT'])
def update_user(username):
    updated_data = request.json
    users = read_data(USERS_FILE)
    user_found = False
    for i, user in enumerate(users):
        if user['usuario'] == username:
            users[i].update(updated_data)
            user_found = True
            break
    if not user_found:
        return jsonify({"error": "Usuario no encontrado"}), 404
    write_data(USERS_FILE, users)
    return jsonify({"message": f"Usuario '{username}' actualizado exitosamente."}), 200

@app.route('/api/data/users/<username>', methods=['DELETE'])
def delete_user(username):
    users = read_data(USERS_FILE)
    initial_len = len(users)
    users = [u for u in users if u['usuario'] != username]
    if len(users) == initial_len:
        return jsonify({"error": "Usuario no encontrado"}), 404
    write_data(USERS_FILE, users)
    return jsonify({"message": "Usuario eliminado exitosamente."}), 200

# --- Rutas para Movimientos (Ingresos/Egresos) ---
@app.route('/api/data/ingresos', methods=['GET'])
def get_movimientos():
    return jsonify(read_data(INGRESOS_FILE)), 200

@app.route('/api/data/ingresos', methods=['POST'])
def add_movimiento():
    new_movimiento = request.json
    new_movimiento['id'] = str(uuid.uuid4())
    movimientos = read_data(INGRESOS_FILE)
    movimientos.append(new_movimiento)
    write_data(INGRESOS_FILE, movimientos)
    return jsonify(new_movimiento), 201

@app.route('/api/data/ingresos/<movimiento_id>', methods=['DELETE'])
def delete_movimiento(movimiento_id):
    movimientos = read_data(INGRESOS_FILE)
    initial_len = len(movimientos)
    movimientos = [m for m in movimientos if m.get('id') != movimiento_id]
    if len(movimientos) == initial_len:
        return jsonify({"error": "Movimiento no encontrado"}), 404
    write_data(INGRESOS_FILE, movimientos)
    return jsonify({"message": "Movimiento eliminado exitosamente"}), 200


# --- Rutas para Gastos ---
@app.route('/api/data/gastos/month/<month>/year/<year>', methods=['GET'])
def get_gastos_by_month_year(month, year):
    all_gastos = read_data(GASTOS_FILE)
    gastos_del_mes = all_gastos.get(year, {}).get(month, [])
    return jsonify(gastos_del_mes), 200

@app.route('/api/data/gastos/month/<month>/year/<year>', methods=['PUT'])
def update_gastos_by_month_year(month, year):
    updated_gastos_for_month = request.json
    all_gastos = read_data(GASTOS_FILE)
    if not isinstance(all_gastos, dict):
        all_gastos = {}
    current_gastos_for_month = all_gastos.get(year, {}).get(month, [])
    new_concepts = [item for item in updated_gastos_for_month if item['concepto'].lower() not in {g['concepto'].lower() for g in current_gastos_for_month}]
    if year not in all_gastos:
        all_gastos[year] = {}
    all_gastos[year][month] = updated_gastos_for_month
    if new_concepts:
        month_names = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        month_index = month_names.index(month)
        current_date = datetime.date(int(year), month_index + 1, 1)
        for _ in range(120):
            current_date += datetime.timedelta(days=32)
            current_date = current_date.replace(day=1)
            future_year, future_month_name = str(current_date.year), month_names[current_date.month - 1]
            if future_year not in all_gastos: all_gastos[future_year] = {}
            if future_month_name not in all_gastos[future_year]: all_gastos[future_year][future_month_name] = []
            future_month_gastos = all_gastos[future_year][future_month_name]
            future_concept_names = {g['concepto'].lower() for g in future_month_gastos}
            for new_concept in new_concepts:
                if new_concept['concepto'].lower() not in future_concept_names:
                    future_month_gastos.append({"concepto": new_concept['concepto'], "monto": "", "fecha": "", "pagado": "no"})
            all_gastos[future_year][future_month_name] = future_month_gastos
    write_data(GASTOS_FILE, all_gastos)
    return jsonify({'message': f'Gastos para {month} {year} actualizados'}), 200

# --- Rutas para Lista de Precios ---
@app.route('/api/data/precios', methods=['GET'])
def get_precios():
    return jsonify(read_data(PRECIOS_FILE)), 200

@app.route('/api/data/precios', methods=['POST'])
def add_precio_item():
    new_item = request.json
    if 'id' not in new_item or not new_item['id']:
        new_item['id'] = str(uuid.uuid4())
    precios = read_data(PRECIOS_FILE)
    precios.append(new_item)
    write_data(PRECIOS_FILE, precios)
    return jsonify(new_item), 201

@app.route('/api/data/precios/<item_id>', methods=['PUT'])
def update_precio_item(item_id):
    updated_data = request.json
    precios = read_data(PRECIOS_FILE)
    item_found = False
    for i, item in enumerate(precios):
        if item.get('id') == item_id:
            precios[i] = {**item, **updated_data}
            item_found = True
            break
    if not item_found:
        return jsonify({"error": "Ítem de precio no encontrado"}), 404
    write_data(PRECIOS_FILE, precios)
    return jsonify(precios[i]), 200

@app.route('/api/data/precios', methods=['PUT'])
def update_all_precios():
    updated_list = request.json
    write_data(PRECIOS_FILE, updated_list)
    return jsonify({"message": "Lista de precios actualizada exitosamente."}), 200

@app.route('/api/data/precios/<item_id>', methods=['DELETE'])
def delete_precio_item(item_id):
    precios = read_data(PRECIOS_FILE)
    ids_to_delete = set()
    def collect_children_ids(parent_id):
        ids_to_delete.add(parent_id)
        for item in precios:
            if item.get('padre_id') == parent_id and item.get('id') not in ids_to_delete:
                collect_children_ids(item.get('id'))
    item_found = any(item.get('id') == item_id for item in precios)
    if not item_found:
        return jsonify({"error": "Ítem de precio no encontrado"}), 404
    collect_children_ids(item_id)
    precios = [item for item in precios if item.get('id') not in ids_to_delete]
    write_data(PRECIOS_FILE, precios)
    return jsonify({"message": "Ítem(s) de precio eliminado(s) exitosamente"}), 200

# --- Rutas para Costos ---
@app.route('/api/data/costos', methods=['GET'])
def get_costos():
    costos_data = read_data(COSTOS_FILE)
    return jsonify(costos_data), 200

@app.route('/api/data/costos', methods=['POST'])
def update_costos():
    costos_data = request.json
    if 'ingredientes' not in costos_data or 'hamburguesas' not in costos_data:
        return jsonify({"error": "El formato de datos de costos es inválido."}), 400
    write_data(COSTOS_FILE, costos_data)
    return jsonify({"message": "Datos de costos actualizados exitosamente."}), 200

# --- Rutas para STOCK ---
@app.route('/api/data/stock', methods=['GET'])
def get_stock():
    return jsonify(read_data(STOCK_FILE)), 200

@app.route('/api/data/stock', methods=['POST'])
def add_stock_item():
    new_item = request.json
    
    # Validaciones básicas
    if 'descripcion' not in new_item or 'tipo' not in new_item:
        return jsonify({"error": "Descripción y tipo son obligatorios."}), 400
    
    if new_item['tipo'] == 'producto' and 'padre_id' not in new_item:
         return jsonify({"error": "Un producto debe tener un título padre."}), 400

    new_item['id'] = str(uuid.uuid4())
    
    # Asegurarnos que cantidad sea un número si es un producto
    if new_item['tipo'] == 'producto':
        try:
            new_item['cantidad'] = float(new_item.get('cantidad', 0))
        except (ValueError, TypeError):
             return jsonify({"error": "La cantidad debe ser un número."}), 400
    
    stock_data = read_data(STOCK_FILE)
    stock_data.append(new_item)
    write_data(STOCK_FILE, stock_data)
    return jsonify(new_item), 201

@app.route('/api/data/stock/<item_id>', methods=['PUT'])
def update_stock_item(item_id):
    updated_data = request.json
    stock_data = read_data(STOCK_FILE)
    item_found = False
    
    # Asegurarnos que cantidad sea un número si es un producto
    if updated_data.get('tipo') == 'producto':
        try:
            updated_data['cantidad'] = float(updated_data.get('cantidad', 0))
        except (ValueError, TypeError):
             return jsonify({"error": "La cantidad debe ser un número."}), 400
             
    for i, item in enumerate(stock_data):
        if item.get('id') == item_id:
            # Actualiza el item, preservando el 'id' original
            stock_data[i] = {**item, **updated_data, 'id': item_id}
            item_found = True
            break
    if not item_found:
        return jsonify({"error": "Ítem de stock no encontrado"}), 404
    
    write_data(STOCK_FILE, stock_data)
    return jsonify(stock_data[i]), 200

    # --- NUEVO: Dinero en Rappi y Banco ---
@app.route('/api/data/rappi-banco', methods=['GET'])
def get_rappi_banco():
    return jsonify(read_data(RAPPI_BANCO_FILE, default_value={"rappi": 0, "banco": 0})), 200

@app.route('/api/data/rappi-banco', methods=['PUT'])
def update_rappi_banco():
    data = request.json
    if not isinstance(data, dict) or "rappi" not in data or "banco" not in data:
        return jsonify({"error": "Formato inválido. Se espera {'rappi': x, 'banco': y}"}), 400
    write_data(RAPPI_BANCO_FILE, data)
    return jsonify({"message": "Datos actualizados exitosamente"}), 200


@app.route('/api/data/stock/<item_id>', methods=['DELETE'])
def delete_stock_item(item_id):
    stock_data = read_data(STOCK_FILE)
    
    ids_to_delete = set()
    
    # Función recursiva para encontrar el item y todos sus hijos
    def collect_children_ids(parent_id):
        ids_to_delete.add(parent_id)
        for item in stock_data:
            if item.get('padre_id') == parent_id and item.get('id') not in ids_to_delete:
                collect_children_ids(item.get('id'))

    item_found = any(item.get('id') == item_id for item in stock_data)
    if not item_found:
        return jsonify({"error": "Ítem de stock no encontrado"}), 404

    # Iniciar la recolección desde el item seleccionado
    collect_children_ids(item_id)
    
    # Filtrar la lista, quedándose solo con los items que NO están en el set de borrado
    stock_data = [item for item in stock_data if item.get('id') not in ids_to_delete]
    
    write_data(STOCK_FILE, stock_data)
    return jsonify({"message": "Ítem(s) de stock eliminado(s) exitosamente"}), 200

# --- Lógica para Clientes y Pedidos ---
@app.route('/api/data/clientes', methods=['GET'])
def get_clientes():
    return jsonify(read_data(CLIENTES_FILE)), 200

def manage_cliente_on_pedido_creation(pedido):
    clientes = read_data(CLIENTES_FILE, default_value=[])
    direccion = pedido.get('direccion', '').strip()
    if not direccion:
        return

    cliente_existente = next((c for c in clientes if c.get('direccion', '').strip().lower() == direccion.lower()), None)
    
    if not cliente_existente:
        nuevo_cliente = {
            'id': str(uuid.uuid4()),
            'numero': len(clientes) + 1,
            'direccion': direccion,
            'cantidad_pedidos': 0,
            'ultimo_pedido_fecha': None
        }
        clientes.append(nuevo_cliente)
        write_data(CLIENTES_FILE, clientes)

def update_cliente_on_pedido_status_change(pedido):
    clientes = read_data(CLIENTES_FILE, default_value=[])
    direccion = pedido.get('direccion', '').strip()
    if not direccion:
        return

    cliente_idx = -1
    for i, c in enumerate(clientes):
        if c.get('direccion', '').strip().lower() == direccion.lower():
            cliente_idx = i
            break

    if cliente_idx != -1:
        pedidos = read_data(PEDIDOS_FILE)
        pedidos_cliente = [p for p in pedidos if p.get('direccion', '').strip().lower() == direccion.lower() and p.get('estado') == 'entregado']
        
        clientes[cliente_idx]['cantidad_pedidos'] = len(pedidos_cliente)
        
        if pedidos_cliente:
            latest_pedido = max(pedidos_cliente, key=lambda p: p.get('fecha_entrega', ''))
            clientes[cliente_idx]['ultimo_pedido_fecha'] = latest_pedido.get('fecha_entrega')
        else:
            clientes[cliente_idx]['ultimo_pedido_fecha'] = None

        write_data(CLIENTES_FILE, clientes)

def modificar_stock_por_pedido(pedido, multiplicador):
    """
    Actualiza (descuenta o repone) el stock basado en los items de un pedido.
    multiplicador = -1 para descontar (venta nueva)
    multiplicador = +1 para reponer (venta eliminada)
    """
    # 1. Cargar los datos más recientes
    stock_data = read_data(STOCK_FILE)
    costos_data = read_data(COSTOS_FILE)
    
    # 2. Crear mapas para búsqueda rápida (convertir a minúsculas para evitar errores)
    stock_map = {str(item.get('descripcion', '')).lower(): item for item in stock_data}
    recetas_map = {str(h.get('nombre', '')).lower(): h for h in costos_data.get('hamburguesas', [])}
    ingredientes_base_map = {str(i.get('nombre', '')).lower(): i for i in costos_data.get('ingredientes', [])}

    # 3. Recorrer cada item del pedido
    for item_vendido in pedido.get('items', []):
        try:
            # Normalizar nombre y cantidad
            nombre_item_vendido = str(item_vendido.get('descripcion', '')).lower()
            cantidad_vendida = float(item_vendido.get('cantidad', 1))
        except (ValueError, TypeError):
            print(f"Error al procesar item: {item_vendido}")
            continue # Saltar este item si la cantidad no es válida

        # 4. PRIMERA VERIFICACIÓN: ¿Es una hamburguesa (está en el recetario)?
        if nombre_item_vendido in recetas_map:
            hamburguesa_receta = recetas_map[nombre_item_vendido]
            
            # Si es una hamburguesa, revisamos cada uno de sus ingredientes
            for ingrediente_en_receta in hamburguesa_receta.get('ingredientes', []):
                # El 'nombre' en la receta de la hamburguesa (ej. 'Carne')
                nombre_ingrediente_receta = str(ingrediente_en_receta.get('nombre', '')).lower()
                
                # Buscamos la definición base de ese ingrediente (para saber su 'usoPorHamburguesa')
                ingrediente_base = ingredientes_base_map.get(nombre_ingrediente_receta)
                
                if ingrediente_base:
                    # El 'nombre' del ingrediente base (ej. 'Carne Picada')
                    # Asumimos que el nombre del ingrediente base ES el que está en el stock
                    nombre_ingrediente_stock = str(ingrediente_base.get('nombre', '')).lower()
                    
                    # Verificamos si este ingrediente existe en nuestra despensa (Stock)
                    if nombre_ingrediente_stock in stock_map:
                        try:
                            # Calculamos cuánto modificar
                            uso_por_hamburguesa = float(ingrediente_base.get('usoPorHamburguesa', 0))
                            cantidad_a_modificar = (uso_por_hamburguesa * cantidad_vendida) * multiplicador
                            
                            # Actualizamos la cantidad en el stock
                            stock_map[nombre_ingrediente_stock]['cantidad'] = float(stock_map[nombre_ingrediente_stock].get('cantidad', 0)) + cantidad_a_modificar
                        except (ValueError, TypeError):
                            print(f"Error al calcular stock para ingrediente: {nombre_ingrediente_stock}")
                    else:
                        print(f"Advertencia: Ingrediente '{nombre_ingrediente_stock}' de receta no encontrado en STOCK.")
                else:
                    print(f"Advertencia: Ingrediente '{nombre_ingrediente_receta}' de receta no encontrado en COSTOS (ingredientes base).")

        # 5. SEGUNDA VERIFICACIÓN: ¿Es un item directo del stock (ej. Coca-Cola)?
        elif nombre_item_vendido in stock_map:
            try:
                # Descontamos o reponemos la cantidad vendida directamente
                cantidad_a_modificar = cantidad_vendida * multiplicador
                stock_map[nombre_item_vendido]['cantidad'] = float(stock_map[nombre_item_vendido].get('cantidad', 0)) + cantidad_a_modificar
            except (ValueError, TypeError):
                print(f"Error al calcular stock para item directo: {nombre_item_vendido}")
        
        # 6. Si no es hamburguesa ni item de stock, no hacemos nada (ej. "Delivery")
        else:
            print(f"Info: Item '{nombre_item_vendido}' no afecta stock (no es receta ni item de stock).")
            
    # 7. Finalmente, guardamos todos los cambios en nuestro archivo de stock
    write_data(STOCK_FILE, list(stock_map.values()))

@app.route('/api/data/pedidos', methods=['POST'])
def add_pedido():
    new_pedido = request.json
    new_pedido['id'] = str(uuid.uuid4())
    
    # --- MODIFICACIÓN INICIO ---
    # Forzamos el estado a 'entregado' y añadimos fechas al crear.
    # Esto asegura que el pedido se considere completado al instante.
    new_pedido['estado'] = 'entregado'
    now = datetime.datetime.now().isoformat()
    new_pedido['fecha_creacion'] = now
    new_pedido['fecha_entrega'] = now
    # --- MODIFICACIÓN FIN ---

    pedidos = read_data(PEDIDOS_FILE)
    pedidos.append(new_pedido)
    write_data(PEDIDOS_FILE, pedidos)
    
    # --- MODIFICACIÓN INICIO ---
    # Llamamos a las funciones para actualizar el stock y los datos del cliente
    # inmediatamente después de crear el pedido.
    modificar_stock_por_pedido(new_pedido, multiplicador=-1) # <-- CAMBIO AQUÍ
    manage_cliente_on_pedido_creation(new_pedido)
    update_cliente_on_pedido_status_change(new_pedido)
    # --- MODIFICACIÓN FIN ---

    return jsonify(new_pedido), 201


@app.route('/api/data/pedidos/<pedido_id>', methods=['PUT'])
def update_pedido(pedido_id):
    updated_data = request.json
    pedidos = read_data(PEDIDOS_FILE)
    item_found = False
    original_pedido = None
    
    for i, item in enumerate(pedidos):
        if item.get('id') == pedido_id:
            original_pedido = item.copy() # Guardar el estado del pedido antes de modificarlo
            
            # --- INICIO: NUEVA LÓGICA DE STOCK (EDITAR) ---
            # 1. Reponemos el stock del pedido original (tal como estaba ANTES de editar)
            modificar_stock_por_pedido(original_pedido, multiplicador=1)
            # --- FIN: NUEVA LÓGICA ---
            
            # Asignar fecha de entrega si se está marcando como 'entregado'
            if updated_data.get('estado') == 'entregado' and not item.get('fecha_entrega'):
                updated_data['fecha_entrega'] = datetime.datetime.now().isoformat()
            elif updated_data.get('estado') == 'pendiente':
                updated_data['fecha_entrega'] = None

            # Aplicar los cambios al pedido
            pedidos[i].update(updated_data)
            item_found = True
            
            # --- INICIO: NUEVA LÓGICA DE STOCK (EDITAR) ---
            # 2. Descontamos el stock del pedido actualizado (con los items NUEVOS)
            modificar_stock_por_pedido(pedidos[i], multiplicador=-1)
            # --- FIN: NUEVA LÓGICA DE STOCK ---
            
            # Lógica existente para actualizar datos del cliente
            if original_pedido.get('estado') != pedidos[i].get('estado'):
                update_cliente_on_pedido_status_change(pedidos[i])
            
            if original_pedido.get('direccion') != pedidos[i].get('direccion'):
                manage_cliente_on_pedido_creation(pedidos[i])

            break
            
    if not item_found:
        return jsonify({"error": "Pedido no encontrado"}), 404
        
    write_data(PEDIDOS_FILE, pedidos)
    return jsonify(pedidos[i]), 200
@app.route('/api/data/pedidos/<pedido_id>', methods=['DELETE'])
def delete_pedido(pedido_id):
    pedidos = read_data(PEDIDOS_FILE)
    
    pedido_a_eliminar = next((p for p in pedidos if p.get('id') == pedido_id), None)
    if not pedido_a_eliminar:
        return jsonify({"error": "Pedido no encontrado"}), 404

    # --- INICIO: NUEVA LÓGICA DE STOCK ---
    # Reponemos el stock ANTES de eliminar el pedido
    modificar_stock_por_pedido(pedido_a_eliminar, multiplicador=1) # <-- AGREGAMOS ESTA LÍNEA
    # --- FIN: NUEVA LÓGICA DE STOCK ---

    pedidos_actualizados = [item for item in pedidos if item.get('id') != pedido_id]
    
    write_data(PEDIDOS_FILE, pedidos_actualizados)
    
    # Actualizar datos del cliente por si acaso
    update_cliente_on_pedido_status_change(pedido_a_eliminar)

    return jsonify({"message": "Pedido eliminado exitosamente"}), 200

    # --- Rutas para Vencimientos ---

@app.route('/api/data/vencimientos', methods=['GET'])
def get_vencimientos():
    return jsonify(read_data(VENCIMIENTOS_FILE)), 200

@app.route('/api/data/vencimientos', methods=['POST'])
def add_vencimiento_item():
    new_item = request.json
    if 'id' not in new_item or not new_item['id']:
        new_item['id'] = str(uuid.uuid4())
    
    data = read_data(VENCIMIENTOS_FILE)
    data.append(new_item)
    write_data(VENCIMIENTOS_FILE, data)
    return jsonify(new_item), 201

@app.route('/api/data/vencimientos/<item_id>', methods=['PUT'])
def update_vencimiento_item(item_id):
    updated_data = request.json
    data = read_data(VENCIMIENTOS_FILE)
    item_found = False
    for i, item in enumerate(data):
        if item.get('id') == item_id:
            data[i] = {**item, **updated_data}
            item_found = True
            break
    if not item_found:
        return jsonify({"error": "Ítem de vencimiento no encontrado"}), 404
    write_data(VENCIMIENTOS_FILE, data)
    return jsonify(data[i]), 200

@app.route('/api/data/vencimientos/<item_id>', methods=['DELETE'])
def delete_vencimiento_item(item_id):
    data = read_data(VENCIMIENTOS_FILE)
    
    ids_to_delete = set()
    def collect_children_ids(parent_id):
        ids_to_delete.add(parent_id)
        for item in data:
            if item.get('padre_id') == parent_id and item.get('id') not in ids_to_delete:
                collect_children_ids(item.get('id'))

    item_found = any(item.get('id') == item_id for item in data)
    if not item_found:
        return jsonify({"error": "Ítem de vencimiento no encontrado"}), 404
        
    collect_children_ids(item_id)
    data = [item for item in data if item.get('id') not in ids_to_delete]
    
    write_data(VENCIMIENTOS_FILE, data)
    return jsonify({"message": "Ítem(s) de vencimiento eliminado(s) exitosamente"}), 200

    # --- Rutas para Proveedores ---

@app.route('/api/data/proveedores', methods=['GET'])
def get_proveedores():
    return jsonify(read_data(PROVEEDORES_FILE)), 200

@app.route('/api/data/proveedores', methods=['POST'])
def save_proveedores():
    data = request.json
    write_data(PROVEEDORES_FILE, data)
    return jsonify({"message": "Datos de proveedores guardados exitosamente."}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Servidor Flask iniciado en http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)



