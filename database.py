import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'dipromasters.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabla Principal de Leads
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL,
            telefono TEXT NOT NULL,
            tiktok_url TEXT,
            web_url TEXT,
            google_maps_url TEXT,
            tiktok_score INTEGER,
            web_score INTEGER,
            google_score INTEGER,
            total_score INTEGER,
            perfil TEXT,
            money_lost_tiktok REAL,
            money_lost_web REAL,
            money_lost_google REAL,
            money_lost_total REAL,
            recommendations TEXT, -- Guardado como JSON string
            analysis_json TEXT, -- Guardado completo del análisis para carga instantánea
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip TEXT,
            estado_seguimiento TEXT DEFAULT 'Nuevo'
        )
    ''')
    
    # Tabla de Seguimiento
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seguimiento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            comentarios TEXT NOT NULL,
            usuario TEXT DEFAULT 'Asesor Dipromasters',
            FOREIGN KEY(lead_id) REFERENCES leads(id) ON DELETE CASCADE
        )
    ''')
    
    # Tabla de Estadísticas Mensuales
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estadisticas_mensuales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes TEXT NOT NULL, -- Formato 'YYYY-MM'
            problema TEXT NOT NULL,
            cantidad INTEGER DEFAULT 1,
            UNIQUE(mes, problema)
        )
    ''')
    
    # Insertar algunas estadísticas iniciales ficticias para que el panel de la agencia tenga datos históricos
    cursor.execute("SELECT COUNT(*) FROM estadisticas_mensuales")
    if cursor.fetchone()[0] == 0:
        mes_actual = datetime.now().strftime('%Y-%m')
        stats_data = [
            (mes_actual, 'Sin SSL', 12),
            (mes_actual, 'Web Lenta', 18),
            (mes_actual, 'Bajo Engagement TikTok', 24),
            (mes_actual, 'Sin Ficha GMB', 8),
            (mes_actual, 'Falta Botón WhatsApp', 15),
            (mes_actual, 'Calificación Google < 4.0', 10)
        ]
        cursor.executemany('''
            INSERT INTO estadisticas_mensuales (mes, problema, cantidad) 
            VALUES (?, ?, ?)
        ''', stats_data)
        
        # También podemos insertar un par de leads de ejemplo
        cursor.execute("SELECT COUNT(*) FROM leads")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO leads (nombre, email, telefono, tiktok_url, web_url, google_maps_url, 
                                  tiktok_score, web_score, google_score, total_score, perfil, 
                                  money_lost_tiktok, money_lost_web, money_lost_google, money_lost_total, 
                                  recommendations, analysis_json, ip, estado_seguimiento)
                VALUES (
                    'Juan Pérez', 'juan@tacosdeliciosos.com', '+34 600 123 456', 
                    'https://tiktok.com/@tacosdeliciosos', 'http://tacosdeliciosos.com', 'Tacos Deliciosos Madrid',
                    12, 10, 15, 37, 'Fantasma Digital',
                    850.0, 1200.0, 1000.0, 3050.0,
                    '["Crear y optimizar la ficha de Google My Business", "Migrar a HTTPS (instalar SSL)", "Instalar widget de WhatsApp flotante", "Aumentar frecuencia de publicación en TikTok"]',
                    '{}', '127.0.0.1', 'Nuevo'
                )
            ''')
            lead_id = cursor.lastrowid
            cursor.execute('''
                INSERT INTO seguimiento (lead_id, comentarios, usuario)
                VALUES (?, 'Lead registrado automáticamente mediante diagnóstico web.', 'Sistema')
            ''', (lead_id,))
            
    conn.commit()
    conn.close()

def save_lead(nombre, email, telefono, tiktok_url, web_url, google_maps_url, 
              tiktok_score, web_score, google_score, total_score, perfil, 
              money_lost_tiktok, money_lost_web, money_lost_google, money_lost_total, 
              recommendations, analysis_data, ip):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    recs_json = json.dumps(recommendations)
    analysis_json_str = json.dumps(analysis_data)
    
    cursor.execute('''
        INSERT INTO leads (
            nombre, email, telefono, tiktok_url, web_url, google_maps_url,
            tiktok_score, web_score, google_score, total_score, perfil,
            money_lost_tiktok, money_lost_web, money_lost_google, money_lost_total,
            recommendations, analysis_json, ip
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        nombre, email, telefono, tiktok_url, web_url, google_maps_url,
        tiktok_score, web_score, google_score, total_score, perfil,
        money_lost_tiktok, money_lost_web, money_lost_google, money_lost_total,
        recs_json, analysis_json_str, ip
    ))

    
    lead_id = cursor.lastrowid
    
    # Agregar nota inicial de seguimiento
    cursor.execute('''
        INSERT INTO seguimiento (lead_id, comentarios, usuario)
        VALUES (?, 'Lead registrado e informe de diagnóstico generado.', 'Sistema')
    ''', (lead_id,))
    
    # Actualizar estadísticas del mes
    mes_actual = datetime.now().strftime('%Y-%m')
    for rec in recommendations:
        cursor.execute('''
            INSERT INTO estadisticas_mensuales (mes, problema, cantidad)
            VALUES (?, ?, 1)
            ON CONFLICT(mes, problema) DO UPDATE SET cantidad = cantidad + 1
        ''', (mes_actual, rec))
        
    conn.commit()
    conn.close()
    return lead_id

def get_lead(lead_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM leads WHERE id = ?', (lead_id,))
    lead = cursor.fetchone()
    conn.close()
    return lead

def get_lead_seguimiento(lead_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM seguimiento WHERE lead_id = ? ORDER BY fecha DESC', (lead_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_seguimiento_note(lead_id, comentarios, usuario='Asesor Dipromasters'):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO seguimiento (lead_id, comentarios, usuario)
        VALUES (?, ?, ?)
    ''', (lead_id, comentarios, usuario))
    conn.commit()
    conn.close()

def update_lead_status(lead_id, estado_seguimiento):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE leads
        SET estado_seguimiento = ?
        WHERE id = ?
    ''', (estado_seguimiento, lead_id))
    
    # Agregar nota de cambio de estado
    comentario = f"Estado cambiado a: {estado_seguimiento}"
    cursor.execute('''
        INSERT INTO seguimiento (lead_id, comentarios, usuario)
        VALUES (?, ?, 'Sistema')
    ''', (lead_id, comentario))
    
    conn.commit()
    conn.close()

def get_all_leads(perfil=None, estado=None, score_min=None, score_max=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM leads WHERE 1=1'
    params = []
    
    if perfil:
        query += ' AND perfil = ?'
        params.append(perfil)
    if estado:
        query += ' AND estado_seguimiento = ?'
        params.append(estado)
    if score_min is not None:
        query += ' AND total_score >= ?'
        params.append(score_min)
    if score_max is not None:
        query += ' AND total_score <= ?'
        params.append(score_max)
        
    query += ' ORDER BY fecha DESC'
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_agency_metrics():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    mes_actual = datetime.now().strftime('%Y-%m')
    
    # Total de leads creados
    cursor.execute('SELECT COUNT(*) FROM leads')
    total_leads = cursor.fetchone()[0]
    
    # Diagnósticos en el mes actual
    cursor.execute("SELECT COUNT(*) FROM leads WHERE strftime('%Y-%m', fecha) = ?", (mes_actual,))
    leads_mes = cursor.fetchone()[0]
    
    # Leads calientes (puntuación menor de 60 Y dinero perdido mayor a $1000)
    cursor.execute('SELECT COUNT(*) FROM leads WHERE total_score < 60 AND money_lost_total > 1000')
    leads_calientes = cursor.fetchone()[0]
    
    # Tasa de cierre (leads con estado_seguimiento = 'Cerrado' sobre total con estado distinto de 'Nuevo')
    cursor.execute("SELECT COUNT(*) FROM leads WHERE estado_seguimiento = 'Cerrado'")
    cerrados = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM leads WHERE estado_seguimiento IN ('Contactado', 'Cerrado', 'Descartado')")
    gestionados = cursor.fetchone()[0]
    
    tasa_cierre = round((cerrados / gestionados * 100), 1) if gestionados > 0 else 0.0
    
    # Top problemas del mes
    cursor.execute('''
        SELECT problema, cantidad 
        FROM estadisticas_mensuales 
        WHERE mes = ? 
        ORDER BY cantidad DESC 
        LIMIT 5
    ''', (mes_actual,))
    top_problemas = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        'total_leads': total_leads,
        'leads_mes': leads_mes,
        'leads_calientes': leads_calientes,
        'tasa_cierre': tasa_cierre,
        'top_problemas': top_problemas
    }
