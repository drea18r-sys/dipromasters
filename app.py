import os
import json
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, Response
from database import init_db, save_lead, get_lead, get_all_leads, get_agency_metrics, get_lead_seguimiento, add_seguimiento_note, update_lead_status
from analyzer import run_diagnostic
from pdf_generator import generate_pdf_report
from notifier import send_telegram_notification, send_client_email

app = Flask(__name__)
REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')

def check_auth(username, password):
    """Verifica si las credenciales de la agencia son correctas."""
    admin_user = os.environ.get('AGENCY_USER', 'admin')
    admin_pass = os.environ.get('AGENCY_PASSWORD', 'dipromasters2026')
    return username == admin_user and password == admin_pass

def authenticate():
    """Envía respuesta 401 que activa el prompt de login en el navegador."""
    return Response(
        'Acceso denegado. Introduce el usuario y contraseña correctos de Dipromasters.', 401,
        {'WWW-Authenticate': 'Basic realm="Acceso Panel de Agencia Dipromasters"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Asegurar que existe la carpeta para reportes
os.makedirs(REPORTS_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    telefono = request.form.get('telefono')
    tiktok_url = request.form.get('tiktok_url', '')
    web_url = request.form.get('web_url', '')
    google_maps_term = request.form.get('google_maps_term')
    
    ip = request.remote_addr or '127.0.0.1'
    
    # Ejecutar análisis completo
    analysis_results = run_diagnostic(
        nombre=nombre,
        email=email,
        telefono=telefono,
        tiktok_url=tiktok_url,
        web_url=web_url,
        google_maps_term=google_maps_term
    )
    
    # Guardar en base de datos
    lead_id = save_lead(
        nombre=nombre,
        email=email,
        telefono=telefono,
        tiktok_url=tiktok_url,
        web_url=web_url,
        google_maps_url=google_maps_term,
        tiktok_score=analysis_results['tiktok_metrics']['score'],
        web_score=analysis_results['web_metrics']['score'],
        google_score=analysis_results['google_metrics']['score'],
        total_score=analysis_results['global_metrics']['score'],
        perfil=analysis_results['lead_info']['perfil'],
        money_lost_tiktok=analysis_results['tiktok_metrics']['money_lost'],
        money_lost_web=analysis_results['web_metrics']['money_lost'],
        money_lost_google=analysis_results['google_metrics']['money_lost'],
        money_lost_total=analysis_results['global_metrics']['money_lost_total'],
        recommendations=analysis_results['recommendations'],
        analysis_data=analysis_results,
        ip=ip
    )
    
    # Generar el PDF
    pdf_path = os.path.join(REPORTS_DIR, f"reporte_{lead_id}.pdf")
    try:
        generate_pdf_report(analysis_results, pdf_path)
    except Exception as e:
        print(f"[App] Error generating PDF for lead {lead_id}: {str(e)}")
        
    # Enviar notificación Telegram
    try:
        send_telegram_notification(analysis_results)
    except Exception as e:
        print(f"[App] Error sending Telegram message: {str(e)}")
        
    # Enviar Email con el PDF adjunto
    try:
        dashboard_url = url_for('dashboard', lead_id=lead_id, _external=True)
        send_client_email(analysis_results, pdf_path, dashboard_url)
    except Exception as e:
        print(f"[App] Error sending SMTP email: {str(e)}")
        
    return redirect(url_for('dashboard', lead_id=lead_id))

@app.route('/dashboard/<int:lead_id>')
def dashboard(lead_id):
    lead_row = get_lead(lead_id)
    if not lead_row:
        return "El diagnóstico solicitado no existe", 404
        
    # Intentar cargar datos completos del JSON persistido
    try:
        analysis_data = json.loads(lead_row['analysis_json'])
        # Si está vacío (caso del mock inicial) lo generamos en caliente
        if not analysis_data or analysis_data == {}:
            analysis_data = run_diagnostic(
                nombre=lead_row['nombre'],
                email=lead_row['email'],
                telefono=lead_row['telefono'],
                tiktok_url=lead_row['tiktok_url'],
                web_url=lead_row['web_url'],
                google_maps_term=lead_row['google_maps_url']
            )
    except Exception as e:
        print(f"[Dashboard] Error parsing analysis JSON: {str(e)}")
        # Fallback regeneración
        analysis_data = run_diagnostic(
            nombre=lead_row['nombre'],
            email=lead_row['email'],
            telefono=lead_row['telefono'],
            tiktok_url=lead_row['tiktok_url'],
            web_url=lead_row['web_url'],
            google_maps_term=lead_row['google_maps_url']
        )
        
    score = analysis_data['global_metrics']['score']
    status_text = "Excelente" if score >= 80 else ("Mejorable" if score >= 60 else ("Preocupante" if score >= 40 else "Crítico"))
    
    return render_template(
        'dashboard.html',
        data=analysis_data,
        lead_id=lead_id,
        status_text=status_text
    )

@app.route('/download-pdf/<int:lead_id>')
def download_pdf(lead_id):
    lead_row = get_lead(lead_id)
    if not lead_row:
        return "El diagnóstico no existe", 404
        
    pdf_path = os.path.join(REPORTS_DIR, f"reporte_{lead_id}.pdf")
    
    # Regenerar el PDF si por algún motivo no existe en el disco
    if not os.path.exists(pdf_path):
        try:
            analysis_data = json.loads(lead_row['analysis_json'])
            if not analysis_data or analysis_data == {}:
                analysis_data = run_diagnostic(
                    nombre=lead_row['nombre'],
                    email=lead_row['email'],
                    telefono=lead_row['telefono'],
                    tiktok_url=lead_row['tiktok_url'],
                    web_url=lead_row['web_url'],
                    google_maps_term=lead_row['google_maps_url']
                )
            generate_pdf_report(analysis_data, pdf_path)
        except Exception as e:
            return f"Error al generar el reporte en PDF: {str(e)}", 500
            
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f"reporte_diagnostico_{lead_row['nombre'].replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )

@app.route('/agency')
@requires_auth
def agency():
    profile = request.args.get('profile')
    status = request.args.get('status')
    score_max = request.args.get('score_max')
    
    if score_max:
        try:
            score_max = int(score_max)
        except ValueError:
            score_max = None
            
    leads = get_all_leads(perfil=profile, estado=status, score_max=score_max)
    metrics = get_agency_metrics()
    
    return render_template(
        'agency.html',
        leads=leads,
        metrics=metrics
    )

@app.route('/get-followup/<int:lead_id>')
@requires_auth
def get_followup(lead_id):
    rows = get_lead_seguimiento(lead_id)
    notes = []
    for row in rows:
        notes.append({
            'id': row['id'],
            'fecha': row['fecha'],
            'comentarios': row['comentarios'],
            'usuario': row['usuario']
        })
    return jsonify({'notes': notes})

@app.route('/add-followup/<int:lead_id>', methods=['POST'])
@requires_auth
def add_followup(lead_id):
    data = request.get_json()
    comentarios = data.get('comentarios')
    if not comentarios:
        return jsonify({'success': False, 'error': 'El comentario no puede estar vacío'}), 400
        
    add_seguimiento_note(lead_id, comentarios)
    return jsonify({'success': True})

@app.route('/update-status/<int:lead_id>', methods=['POST'])
@requires_auth
def update_status(lead_id):
    data = request.get_json()
    estado = data.get('estado_seguimiento')
    if not estado:
        return jsonify({'success': False, 'error': 'El estado no puede estar vacío'}), 400
        
    update_lead_status(lead_id, estado)
    return jsonify({'success': True})

# Inicializar la base de datos al importar el módulo para producción (Gunicorn)
init_db()

if __name__ == '__main__':
    # Ejecutar la app localmente en modo debug
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)
