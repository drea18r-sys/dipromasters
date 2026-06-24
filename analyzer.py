import hashlib
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def get_deterministic_hash(seed_str):
    """Generates a stable integer from a string for deterministic simulation."""
    return int(hashlib.md5(seed_str.encode('utf-8')).hexdigest(), 16)

def parse_tiktok_username(url):
    if not url:
        return "negocio_tiktok"
    # Match patterns like @username
    match = re.search(r'@([a-zA-Z0-9_\.]+)', url)
    if match:
        return match.group(1)
    # Match last path component if not starting with @
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    if path:
        return path.split('/')[-1]
    return "negocio_tiktok"

def parse_web_domain(url):
    if not url:
        return "negocio.com"
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return "negocio.com"

def analyze_website(url):
    """Performs real analysis on the website and fallbacks if down."""
    result = {
        'active': False,
        'ssl': False,
        'load_time': 5.0,
        'responsive': False,
        'meta_description': '',
        'seo_title': '',
        'has_whatsapp': False,
        'has_contact_form': False,
        'has_social_links': False,
        'broken_links': 0
    }
    
    if not url:
        return result
        
    formatted_url = url.strip()
    if not formatted_url.startswith(('http://', 'https://')):
        formatted_url = 'https://' + formatted_url
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
        
    try:
        # Check SSL
        parsed_url = urlparse(formatted_url)
        if parsed_url.scheme == 'https':
            result['ssl'] = True
            
        # Make requests call
        response = requests.get(formatted_url, timeout=5, headers=headers)
        result['active'] = (response.status_code == 200)
        
        if result['active']:
            # Load time
            result['load_time'] = round(response.elapsed.total_seconds(), 2)
            
            # Parse content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Title
            if soup.title:
                result['seo_title'] = soup.title.string.strip() if soup.title.string else ''
                
            # Meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                result['meta_description'] = meta_desc.get('content').strip()
                
            # Responsive viewport check
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            if viewport and 'width=device-width' in viewport.get('content', ''):
                result['responsive'] = True
                
            # WhatsApp float widget check
            html_content = response.text.lower()
            if 'wa.me' in html_content or 'api.whatsapp.com' in html_content or 'whatsapp' in html_content:
                result['has_whatsapp'] = True
                
            # Contact form check
            forms = soup.find_all('form')
            for form in forms:
                action = form.get('action', '').lower()
                form_id = form.get('id', '').lower()
                form_class = ''.join(form.get('class', [])).lower()
                if 'contact' in action or 'contact' in form_id or 'contact' in form_class or form.find('input', type='email'):
                    result['has_contact_form'] = True
                    break
                    
            # Social links check
            for a in soup.find_all('a', href=True):
                href = a['href'].lower()
                if 'tiktok.com' in href or 'instagram.com' in href or 'facebook.com' in href or 'youtube.com' in href:
                    result['has_social_links'] = True
                    break
                    
            # Basic broken links detection (simulated as 0 for this diagnostic)
            result['broken_links'] = 0
            
    except Exception as e:
        # Fallback if connection fails (e.g. DNS or Timeout)
        # Try HTTP if HTTPS failed
        if formatted_url.startswith('https://'):
            http_url = formatted_url.replace('https://', 'http://', 1)
            try:
                response = requests.get(http_url, timeout=5, headers=headers)
                result['active'] = (response.status_code == 200)
                result['ssl'] = False
                result['load_time'] = round(response.elapsed.total_seconds(), 2)
                # Parse title etc...
                soup = BeautifulSoup(response.text, 'html.parser')
                if soup.title: result['seo_title'] = soup.title.string.strip() if soup.title.string else ''
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc and meta_desc.get('content'): result['meta_description'] = meta_desc.get('content').strip()
                viewport = soup.find('meta', attrs={'name': 'viewport'})
                if viewport and 'width=device-width' in viewport.get('content', ''): result['responsive'] = True
                html_content = response.text.lower()
                if 'wa.me' in html_content or 'api.whatsapp.com' in html_content or 'whatsapp' in html_content: result['has_whatsapp'] = True
                result['has_contact_form'] = len(soup.find_all('form')) > 0
                return result
            except:
                pass
        
        result['active'] = False
        
    return result

def run_diagnostic(nombre, email, telefono, tiktok_url, web_url, google_maps_term):
    # Parsers
    tiktok_user = parse_tiktok_username(tiktok_url)
    domain = parse_web_domain(web_url)
    
    # Generate Seed based on name & term
    seed_str = f"{nombre}_{tiktok_user}_{domain}_{google_maps_term}".lower()
    seed = get_deterministic_hash(seed_str)
    
    # ------------------
    # AREA 1: TIKTOK (Scraping / Simulated Híbrido)
    # ------------------
    # Generate metrics deterministically based on seed
    followers = (seed % 15000) + 120  # Range: 120 - 15,120 followers
    # Engagement rate: 0.2% - 5.2%
    engagement = round(0.2 + (seed % 50) / 10.0, 2)
    # Frecuencia de publicación (últimos 30 días): 1 - 25 posts
    posts_month = (seed % 24) + 1
    # Link en bio: Sí/No
    has_link_in_bio = (seed % 3 != 0) # 66% chance of having a link
    bio_destination = "sitio_web" if has_link_in_bio and (seed % 2 == 0) else ("linktree" if has_link_in_bio else "ninguno")
    # Hashtags
    uses_hashtags = (seed % 5 != 0) # 80% chance
    # Responde a comentarios: Sí/No
    responds_comments = (seed % 2 == 0)
    # Calidad de video
    video_quality = "Excelente (FullHD)" if seed % 3 == 0 else ("Aceptable" if seed % 3 == 1 else "Baja (Cámara de móvil)")
    
    # ------------------
    # AREA 2: SITIO WEB (Análisis real + Fallback)
    # ------------------
    web_analysis = analyze_website(web_url)
    
    # If website url was provided but site was not active, double check or simulate
    # For demo purposes, we will respect the actual requests, but if they enter a mock url (like 'mi-tienda-lenta.com'),
    # we can simulate it if it fails to connect to make it interesting.
    # Let's say: if domain ends with '.local' or fails and seems like a mock, we simulate.
    # To keep it extremely robust: if web_url is provided but request fails, we'll mark as down.
    # This is realistic!
    
    # ------------------
    # AREA 3: GOOGLE REVIEWS (Scraping / Simulated Híbrido)
    # ------------------
    # Average rating: 2.1 - 4.9 stars
    google_rating = round(2.1 + (seed % 29) / 10.0, 1)
    # Total reviews: 2 - 250
    google_total_reviews = (seed % 248) + 2
    # Reviews last 30 days: 0 - 15
    google_recent_reviews = seed % 16
    # Owner responds: Sí/No
    owner_responds_google = (seed % 3 == 0)
    # Active GMB profile: Sí/No
    gmb_active = (seed % 8 != 0) # 87.5% active
    # Negative review percent (1-2 stars): 0% - 45%
    negative_review_pct = seed % 46
    # Trend
    trend = "Mejora" if google_recent_reviews > 5 and google_rating >= 4.0 else ("Estable" if google_rating >= 3.5 else "Empeora")
    
    # ---------------------------------------------
    # PUNTUACIÓN Y DINERO PERDIDO POR ÁREA
    # ---------------------------------------------
    
    # TikTok Score (Max 40)
    tk_pts_followers = 15 if followers > 10000 else (10 if followers >= 5000 else (5 if followers >= 1000 else 1))
    tk_pts_engagement = 15 if engagement > 3.0 else (10 if engagement >= 1.5 else (5 if engagement >= 0.5 else 1))
    tk_pts_posts = 10 if posts_month > 15 else (7 if posts_month >= 8 else (3 if posts_month >= 4 else 0))
    tiktok_score = tk_pts_followers + tk_pts_engagement + tk_pts_posts
    
    # TikTok Money Lost
    money_lost_tk = 0.0
    if engagement < 2.0:
        money_lost_tk += (2.0 - engagement) * 500
    if not has_link_in_bio:
        money_lost_tk += 300
    if not responds_comments:
        money_lost_tk += 150
    if posts_month < 8:
        money_lost_tk += 200
        
    # Web Score (Max 35)
    web_score = 0
    money_lost_web = 0.0
    
    if not web_url:
        # Client did not input website -> treated as having no website (down / critical loss)
        web_score = 0
        money_lost_web = 1000.0  # Web caída / inexistente
    else:
        if not web_analysis['active']:
            # Website input but down
            web_score = 0
            money_lost_web = 1000.0
        else:
            # Active + SSL
            pts_ssl = 10 if web_analysis['ssl'] else 5
            # Speed
            speed = web_analysis['load_time']
            pts_speed = 10 if speed < 2.0 else (7 if speed <= 3.0 else (3 if speed <= 5.0 else 0))
            # Responsive
            pts_resp = 5 if web_analysis['responsive'] else 0
            # SEO/conversion elements
            pts_conv = 0
            if web_analysis['has_whatsapp']: pts_conv += 3
            if web_analysis['has_contact_form']: pts_conv += 3
            if web_analysis['meta_description'] and web_analysis['seo_title']: pts_conv += 4
            
            web_score = pts_ssl + pts_speed + pts_resp + pts_conv
            
            # Money Lost Web
            if speed > 3.0:
                money_lost_web += (speed - 3.0) * 200
            if not web_analysis['has_whatsapp']:
                money_lost_web += 400
            if not web_analysis['ssl']:
                money_lost_web += 200
            if not web_analysis['meta_description']:
                money_lost_web += 250
            if not web_analysis['responsive']:
                money_lost_web += 500
                
    # Google Reviews Score (Max 25)
    g_pts_rating = 10 if google_rating >= 4.5 else (7 if google_rating >= 4.0 else (4 if google_rating >= 3.0 else 1))
    g_pts_count = 8 if google_total_reviews >= 50 else (5 if google_total_reviews >= 10 else (2 if google_total_reviews >= 5 else 0))
    g_pts_owner = 7 if owner_responds_google and gmb_active else 0
    
    # If GMB is not active at all, score is heavily reduced
    if not gmb_active:
        google_score = 0
    else:
        google_score = g_pts_rating + g_pts_count + g_pts_owner
        
    # Google Money Lost
    money_lost_google = 0.0
    if not gmb_active:
        money_lost_google = 800.0  # Sin ficha GMB
    else:
        if google_total_reviews < 10:
            money_lost_google += 300
        if google_rating < 4.0:
            money_lost_google += 500
        if not owner_responds_google:
            money_lost_google += 200
        if negative_review_pct >= 30:
            money_lost_google += 400

    # Total Score and Total Money Lost
    total_score = tiktok_score + web_score + google_score
    money_lost_total = money_lost_tk + money_lost_web + money_lost_google
    
    # ---------------------------------------------
    # CLASIFICACIÓN DE PERFIL DEL CLIENTE
    # ---------------------------------------------
    perfil = ""
    if not web_url or not tiktok_url:
        perfil = "🔗 Desconectado Digital"
    elif google_total_reviews < 10 or google_rating < 4.0 or not gmb_active:
        perfil = "🤫 Fantasma Digital"
    elif followers < 1000 and posts_month < 4 and google_total_reviews < 5:
        perfil = "🌱 Principiante Digital"
    elif followers > 1000 and posts_month < 4:
        perfil = "😴 Inactivo con Audiencia"
    elif followers >= 1000 and followers <= 10000 and engagement < 3.0:
        perfil = "🚀 Estancado con Potencial"
    elif followers > 10000 and web_score >= 25:
        perfil = "🏆 Competidor Fuerte"
    else:
        # Fallback
        perfil = "🚀 Estancado con Potencial"
        
    # ---------------------------------------------
    # RECOMENDACIONES DE ACUERDO A LOS DETALLES
    # ---------------------------------------------
    recommendations = []
    
    # TikTok recommendations
    if posts_month < 8:
        recommendations.append("Plan de contenido semanal para TikTok (Publica menos de 8 veces/mes)")
    if not has_link_in_bio:
        recommendations.append("Configurar enlace comercial en bio (Linktree/Beacons)")
    if engagement < 1.5:
        recommendations.append("Estrategia de contenido disruptivo + Campaña en TikTok Ads")
    if not responds_comments:
        recommendations.append("Servicio de Community Manager para responder interacciones")
    if video_quality == "Baja (Cámara de móvil)":
        recommendations.append("Mejora en producción de video y uso de audios en tendencia")
        
    # Web recommendations
    if web_url:
        if not web_analysis['active']:
            recommendations.append("Mantenimiento web urgente (Tu sitio web está caído)")
        else:
            if not web_analysis['ssl']:
                recommendations.append("Instalar Certificado SSL y forzar redirección HTTPS")
            if web_analysis['load_time'] > 3.0:
                recommendations.append("Optimización de velocidad de carga de la web (WPO)")
            if not web_analysis['responsive']:
                recommendations.append("Rediseño web responsivo (Adaptado a dispositivos móviles)")
            if not web_analysis['has_whatsapp']:
                recommendations.append("Instalación de widget de WhatsApp flotante")
            if not web_analysis['meta_description']:
                recommendations.append("SEO On-Page básico (Títulos y Meta descripciones faltantes)")
    else:
        recommendations.append("Diseño y desarrollo de sitio web corporativo profesional")
        
    # Google Reviews recommendations
    if not gmb_active:
        recommendations.append("Creación y verificación de la ficha de Google My Business (GMB)")
    else:
        if google_total_reviews < 10:
            recommendations.append("Campaña automatizada para generación de reseñas de clientes")
        if google_rating < 4.0:
            recommendations.append("Estrategia de reputación online y gestión de crisis")
        if not owner_responds_google:
            recommendations.append("Gestión de comunidad para responder opiniones de Google Reviews")
        if negative_review_pct >= 30:
            recommendations.append("Plan de recuperación de reputación (Eliminar/Mitigar impacto de reseñas 1-2 estrellas)")

    # ---------------------------------------------
    # COMPETENCIA (TIKTOK Y GOOGLE REVIEWS)
    # ---------------------------------------------
    # Generate 3 similar local competitors
    comp_prefix = google_maps_term.split()[0] if google_maps_term else "Competidor"
    competitors = [
        {
            'name': f"{comp_prefix} Pro",
            'tiktok_followers': int(followers * 1.5),
            'tiktok_engagement': round(engagement * 1.2, 2),
            'google_rating': min(4.9, google_rating + 0.4),
            'google_reviews': int(google_total_reviews * 1.8)
        },
        {
            'name': f"{comp_prefix} Local",
            'tiktok_followers': int(followers * 0.9),
            'tiktok_engagement': round(engagement * 0.8, 2),
            'google_rating': max(3.0, google_rating - 0.2),
            'google_reviews': int(google_total_reviews * 0.7)
        },
        {
            'name': f"Grupo {comp_prefix}",
            'tiktok_followers': int(followers * 2.2),
            'tiktok_engagement': round(engagement * 1.4, 2),
            'google_rating': min(5.0, google_rating + 0.6),
            'google_reviews': int(google_total_reviews * 2.5)
        }
    ]

    return {
        'lead_info': {
            'nombre': nombre,
            'email': email,
            'telefono': telefono,
            'tiktok_url': tiktok_url,
            'web_url': web_url,
            'google_maps_term': google_maps_term,
            'perfil': perfil
        },
        'tiktok_metrics': {
            'username': tiktok_user,
            'followers': followers,
            'engagement': engagement,
            'posts_month': posts_month,
            'has_link_in_bio': has_link_in_bio,
            'bio_destination': bio_destination,
            'uses_hashtags': uses_hashtags,
            'responds_comments': responds_comments,
            'video_quality': video_quality,
            'score': tiktok_score,
            'money_lost': round(money_lost_tk, 2)
        },
        'web_metrics': {
            'domain': domain,
            'active': web_analysis['active'] if web_url else False,
            'ssl': web_analysis['ssl'] if web_url else False,
            'load_time': web_analysis['load_time'] if web_url else 0.0,
            'responsive': web_analysis['responsive'] if web_url else False,
            'seo_title': web_analysis['seo_title'] if web_url else '',
            'meta_description': web_analysis['meta_description'] if web_url else '',
            'has_whatsapp': web_analysis['has_whatsapp'] if web_url else False,
            'has_contact_form': web_analysis['has_contact_form'] if web_url else False,
            'has_social_links': web_analysis['has_social_links'] if web_url else False,
            'broken_links': web_analysis['broken_links'] if web_url else 0,
            'score': web_score,
            'money_lost': round(money_lost_web, 2)
        },
        'google_metrics': {
            'term': google_maps_term,
            'rating': google_rating,
            'total_reviews': google_total_reviews,
            'recent_reviews': google_recent_reviews,
            'owner_responds': owner_responds_google,
            'gmb_active': gmb_active,
            'negative_review_pct': negative_review_pct,
            'trend': trend,
            'score': google_score,
            'money_lost': round(money_lost_google, 2)
        },
        'global_metrics': {
            'score': total_score,
            'money_lost_total': round(money_lost_total, 2)
        },
        'recommendations': recommendations,
        'competitors': competitors
    }
