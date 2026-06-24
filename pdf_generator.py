import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# Palette
PRIMARY_COLOR = colors.HexColor('#272B8B')
SECONDARY_COLOR = colors.HexColor('#F58220')
ACCENT_COLOR = colors.HexColor('#F58220')
TEXT_MAIN = colors.HexColor('#1A2332')
TEXT_MUTED = colors.HexColor('#5A6C7D')
LIGHT_BG = colors.HexColor('#F7F9FC')
SUCCESS_COLOR = colors.HexColor('#2ECC71')
WARNING_COLOR = colors.HexColor('#F39C12')
DANGER_COLOR = colors.HexColor('#E74C3C')

class NumberedCanvas(canvas.Canvas):
    """Canvas to add running header, footer and page numbers dynamically."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        self.saveState()
        
        # Don't draw headers/footers on the cover page (page 1)
        if self._pageNumber > 1:
            # Header
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(PRIMARY_COLOR)
            self.drawString(54, 750, "DIPROMASTERS - DIAGNÓSTICO DIGITAL DE NEGOCIO")
            self.setStrokeColor(SECONDARY_COLOR)
            self.setLineWidth(0.5)
            self.line(54, 742, letter[0]-54, 742)
            
            # Footer
            self.setFont("Helvetica", 8)
            self.setFillColor(TEXT_MUTED)
            self.drawString(54, 36, "Informe Confidencial para uso interno y comercial.")
            self.drawRightString(letter[0]-54, 36, f"Página {self._pageNumber} de {page_count}")
            self.line(54, 48, letter[0]-54, 48)
            
        self.restoreState()

def generate_pdf_report(diagnostic_data, output_path):
    """Generates a professional PDF report for Dipromasters diagnostic."""
    
    # Setup document
    # Margins: 0.75 inch (54 points)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=32,
        leading=38,
        textColor=PRIMARY_COLOR,
        alignment=0, # Left aligned
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=14,
        leading=18,
        textColor=SECONDARY_COLOR,
        alignment=0,
        spaceAfter=30
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY_COLOR,
        spaceBefore=15,
        spaceAfter=15,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=SECONDARY_COLOR,
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=TEXT_MAIN,
        spaceAfter=10
    )
    
    bold_body_style = ParagraphStyle(
        'Body_Bold_Custom',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    muted_style = ParagraphStyle(
        'Muted_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12,
        textColor=TEXT_MUTED,
        spaceAfter=8
    )
    
    recommendation_style = ParagraphStyle(
        'Rec_Style',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=TEXT_MAIN,
        spaceAfter=6
    )

    story = []
    
    # -------------------------------------------------------------------------
    # PORTADA (COVER PAGE)
    # -------------------------------------------------------------------------
    story.append(Spacer(1, 40))
    # Colored top bar
    cover_bar_data = [['']]
    cover_bar_table = Table(cover_bar_data, colWidths=[letter[0]-108], rowHeights=[15])
    cover_bar_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PRIMARY_COLOR),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(cover_bar_table)
    story.append(Spacer(1, 40))
    
    logo_path = os.path.join(os.path.dirname(__file__), 'static', 'logo.png')
    if os.path.exists(logo_path):
        try:
            # Render logo with a nice scale (250 width, 100 height)
            story.append(Image(logo_path, width=250, height=100))
            story.append(Spacer(1, 20))
        except Exception as e:
            print(f"[PDF] Error loading logo: {str(e)}")
            story.append(Paragraph("DIPROMASTERS", title_style))
    else:
        story.append(Paragraph("DIPROMASTERS", title_style))
        
    story.append(Paragraph("DIAGNÓSTICO DIGITAL & AUDITORÍA DE RENDIMIENTO", subtitle_style))
    
    # Intro info
    lead_info = diagnostic_data['lead_info']
    glob_metrics = diagnostic_data['global_metrics']
    
    info_data = [
        [Paragraph("<b>Cliente:</b>", body_style), Paragraph(lead_info['nombre'], body_style)],
        [Paragraph("<b>Email:</b>", body_style), Paragraph(lead_info['email'], body_style)],
        [Paragraph("<b>Teléfono:</b>", body_style), Paragraph(lead_info['telefono'], body_style)],
        [Paragraph("<b>TikTok:</b>", body_style), Paragraph(lead_info['tiktok_url'] or "No Provisto", body_style)],
        [Paragraph("<b>Sitio Web:</b>", body_style), Paragraph(lead_info['web_url'] or "No Provisto", body_style)],
        [Paragraph("<b>Google Maps / Negocio:</b>", body_style), Paragraph(lead_info['google_maps_term'], body_style)],
        [Paragraph("<b>Fecha:</b>", body_style), Paragraph(datetime.now().strftime('%d/%m/%Y'), body_style)]
    ]
    
    info_table = Table(info_data, colWidths=[150, letter[0]-258])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#E1E8ED')),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 100))
    
    # CTA on cover
    cta_cover_style = ParagraphStyle(
        'CTACover',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=PRIMARY_COLOR,
        alignment=1 # Centered
    )
    story.append(Paragraph("Preparado exclusivamente por el equipo de consultoría de Dipromasters", cta_cover_style))
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # RESUMEN EJECUTIVO
    # -------------------------------------------------------------------------
    story.append(Paragraph("Resumen Ejecutivo", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY_COLOR, spaceAfter=15))
    
    score = glob_metrics['score']
    status_text = "Excelente" if score >= 80 else ("Mejorable" if score >= 60 else ("Preocupante" if score >= 40 else "Crítico"))
    status_color = SUCCESS_COLOR if score >= 80 else (WARNING_COLOR if score >= 60 else (DANGER_COLOR if score >= 40 else DANGER_COLOR))
    
    # Score layout table
    summary_data = [
        [
            Paragraph("<b>PUNTUACIÓN GLOBAL</b>", bold_body_style),
            Paragraph("<b>DINERO PERDIDO AL MES</b>", bold_body_style),
            Paragraph("<b>PERFIL DIGITAL</b>", bold_body_style)
        ],
        [
            Paragraph(f"<font size=32 color='{status_color}'><b>{score}/100</b></font><br/>Estado: <b>{status_text}</b>", body_style),
            Paragraph(f"<font size=28 color='#E74C3C'><b>${glob_metrics['money_lost_total']} USD</b></font><br/>pérdida mensual estimada", body_style),
            Paragraph(f"<font size=14 color='#2C3E7A'><b>{lead_info['perfil']}</b></font><br/>Servicio sugerido: <b>{get_recommended_service(lead_info['perfil'])}</b>", body_style)
        ]
    ]
    summary_table = Table(summary_data, colWidths=[(letter[0]-108)/3]*3)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E1E8ED')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E1E8ED')),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Financial breakdown
    tk_metrics = diagnostic_data['tiktok_metrics']
    web_metrics = diagnostic_data['web_metrics']
    google_metrics = diagnostic_data['google_metrics']
    
    story.append(Paragraph("Desglose del Costo de Oportunidad", h2_style))
    loss_data = [
        [Paragraph("<b>Área de Análisis</b>", bold_body_style), Paragraph("<b>Puntuación</b>", bold_body_style), Paragraph("<b>Fuga Mensual Estimada</b>", bold_body_style)],
        [Paragraph("<b>TikTok Ads & Contenido</b>", body_style), Paragraph(f"{tk_metrics['score']}/40", body_style), Paragraph(f"${tk_metrics['money_lost']} USD", body_style)],
        [Paragraph("<b>Sitio Web y Conversión</b>", body_style), Paragraph(f"{web_metrics['score']}/35", body_style), Paragraph(f"${web_metrics['money_lost']} USD", body_style)],
        [Paragraph("<b>Google Reviews y SEO Local</b>", body_style), Paragraph(f"{google_metrics['score']}/25", body_style), Paragraph(f"${google_metrics['money_lost']} USD", body_style)],
        [Paragraph("<b>TOTAL PERDIDO</b>", bold_body_style), Paragraph(f"{score}/100", bold_body_style), Paragraph(f"<font color='#E74C3C'><b>${glob_metrics['money_lost_total']} USD</b></font>", bold_body_style)]
    ]
    loss_table = Table(loss_data, colWidths=[200, 100, letter[0]-408])
    loss_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, LIGHT_BG]),
        ('LINEBELOW', (0,-1), (-1,-1), 1.5, PRIMARY_COLOR),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#FDEDEC')),
    ]))
    
    # Set text colors in table header manually using Paragraph styles
    header_style = ParagraphStyle('Header_Col', parent=bold_body_style, textColor=colors.white)
    loss_data[0] = [Paragraph("<b>Área de Análisis</b>", header_style), Paragraph("<b>Puntuación</b>", header_style), Paragraph("<b>Fuga Mensual</b>", header_style)]
    loss_table = Table(loss_data, colWidths=[200, 100, letter[0]-408])
    loss_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, LIGHT_BG]),
        ('LINEBELOW', (0,-1), (-1,-1), 1.5, PRIMARY_COLOR),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#FDEDEC')),
    ]))
    
    story.append(loss_table)
    story.append(Spacer(1, 10))
    story.append(Paragraph("<i>* El dinero perdido representa la estimación de ingresos perdidos por bajas conversiones web, penalizaciones de reputación online, visibilidad nula en SEO Local y falta de engagement en redes sociales.</i>", muted_style))
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # DETALLE POR ÁREA
    # -------------------------------------------------------------------------
    story.append(Paragraph("Detalle de Auditoría por Áreas", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY_COLOR, spaceAfter=15))
    
    # 1. TIKTOK
    story.append(Paragraph("1. TikTok Ads & Tráfico de Contenido", h2_style))
    tk_active_str = "Sí" if tk_metrics['has_link_in_bio'] else "No"
    tk_comments_str = "Sí" if tk_metrics['responds_comments'] else "No"
    
    tk_items = [
        [Paragraph("<b>Indicador</b>", bold_body_style), Paragraph("<b>Estado/Valor</b>", bold_body_style)],
        [Paragraph("Número de seguidores", body_style), Paragraph(f"{tk_metrics['followers']:,}", body_style)],
        [Paragraph("Frecuencia de publicación (últimos 30 días)", body_style), Paragraph(f"{tk_metrics['posts_month']} posts", body_style)],
        [Paragraph("Engagement promedio", body_style), Paragraph(f"{tk_metrics['engagement']}%", body_style)],
        [Paragraph("Enlace comercial en bio", body_style), Paragraph(f"{tk_active_str} ({tk_metrics['bio_destination']})", body_style)],
        [Paragraph("Responde a comentarios", body_style), Paragraph(tk_comments_str, body_style)],
        [Paragraph("Calidad visual detectada", body_style), Paragraph(tk_metrics['video_quality'], body_style)]
    ]
    tk_table = Table(tk_items, colWidths=[250, letter[0]-358])
    tk_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#E1E8ED')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(tk_table)
    story.append(Spacer(1, 15))
    
    # 2. SITIO WEB
    story.append(Paragraph("2. Sitio Web y Optimización de Conversión", h2_style))
    
    web_active_str = "🟢 Activo" if web_metrics['active'] else "🔴 Caído / Inexistente"
    web_ssl_str = "🟢 Activo (HTTPS)" if web_metrics['ssl'] else "🔴 Inseguro (HTTP)"
    web_resp_str = "Sí" if web_metrics['responsive'] else "No"
    web_wa_str = "Instalado" if web_metrics['has_whatsapp'] else "No instalado"
    web_form_str = "Detectado" if web_metrics['has_contact_form'] else "No detectado"
    web_desc_str = "Completado" if web_metrics['meta_description'] else "Pendiente / Vacío"
    
    web_items = [
        [Paragraph("<b>Indicador</b>", bold_body_style), Paragraph("<b>Estado/Valor</b>", bold_body_style)],
        [Paragraph("Estado del sitio", body_style), Paragraph(web_active_str, body_style)],
        [Paragraph("Certificado de seguridad SSL", body_style), Paragraph(web_ssl_str, body_style)],
        [Paragraph("Velocidad de carga inicial", body_style), Paragraph(f"{web_metrics['load_time']} segundos", body_style)],
        [Paragraph("Optimizado para móviles (Responsive)", body_style), Paragraph(web_resp_str, body_style)],
        [Paragraph("Botón de WhatsApp flotante", body_style), Paragraph(web_wa_str, body_style)],
        [Paragraph("Formulario de captación activo", body_style), Paragraph(web_form_str, body_style)],
        [Paragraph("Meta Descripción (SEO)", body_style), Paragraph(web_desc_str, body_style)]
    ]
    web_table = Table(web_items, colWidths=[250, letter[0]-358])
    web_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#E1E8ED')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(web_table)
    story.append(Spacer(1, 15))
    
    # 3. GOOGLE REVIEWS
    story.append(Paragraph("3. Reseñas de Google y Reputación Local", h2_style))
    
    gmb_str = "Activa" if google_metrics['gmb_active'] else "Inactiva / No reclamada"
    g_owner_str = "Sí" if google_metrics['owner_responds'] else "No"
    
    google_items = [
        [Paragraph("<b>Indicador</b>", bold_body_style), Paragraph("<b>Estado/Valor</b>", bold_body_style)],
        [Paragraph("Ficha de Google My Business", body_style), Paragraph(gmb_str, body_style)],
        [Paragraph("Calificación promedio", body_style), Paragraph(f"{google_metrics['rating']} estrellas / 5.0", body_style)],
        [Paragraph("Cantidad total de reseñas", body_style), Paragraph(f"{google_metrics['total_reviews']} opiniones", body_style)],
        [Paragraph("Reseñas recibidas (últimos 30 días)", body_style), Paragraph(f"{google_metrics['recent_reviews']}", body_style)],
        [Paragraph("El propietario responde reseñas", body_style), Paragraph(g_owner_str, body_style)],
        [Paragraph("Porcentaje de reseñas negativas", body_style), Paragraph(f"{google_metrics['negative_review_pct']}%", body_style)],
        [Paragraph("Tendencia de reputación", body_style), Paragraph(google_metrics['trend'], body_style)]
    ]
    google_table = Table(google_items, colWidths=[250, letter[0]-358])
    google_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#E1E8ED')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(google_table)
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # COMPARATIVA CON COMPETENCIA
    # -------------------------------------------------------------------------
    story.append(Paragraph("Comparativa con la Competencia Local", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY_COLOR, spaceAfter=15))
    story.append(Paragraph("Analizamos a los principales competidores del sector geográfico del cliente para medir la brecha comercial:", body_style))
    
    comp_headers = [
        Paragraph("<b>Empresa</b>", header_style),
        Paragraph("<b>Seguidores TikTok</b>", header_style),
        Paragraph("<b>Engagement</b>", header_style),
        Paragraph("<b>Calificación Google</b>", header_style),
        Paragraph("<b>Opiniones Google</b>", header_style)
    ]
    
    comp_rows = [comp_headers]
    
    # Customer row
    comp_rows.append([
        Paragraph(f"<b>{lead_info['google_maps_term']} (Tú)</b>", bold_body_style),
        Paragraph(f"{tk_metrics['followers']:,}", body_style),
        Paragraph(f"{tk_metrics['engagement']}%", body_style),
        Paragraph(f"{google_metrics['rating']} ⭐", body_style),
        Paragraph(f"{google_metrics['total_reviews']}", body_style)
    ])
    
    for comp in diagnostic_data['competitors']:
        comp_rows.append([
            Paragraph(comp['name'], body_style),
            Paragraph(f"{comp['tiktok_followers']:,}", body_style),
            Paragraph(f"{comp['tiktok_engagement']}%", body_style),
            Paragraph(f"{comp['google_rating']} ⭐", body_style),
            Paragraph(f"{comp['google_reviews']}", body_style)
        ])
        
    comp_table = Table(comp_rows, colWidths=[150, 100, 80, 100, 74])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E1E8ED')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E1E8ED')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#FCF3CF')) # Highlight client row in yellow
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 30))
    
    # -------------------------------------------------------------------------
    # RECOMENDACIONES PRIORIZADAS
    # -------------------------------------------------------------------------
    story.append(Paragraph("Plan de Acción Priorizado", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY_COLOR, spaceAfter=15))
    
    story.append(Paragraph("Recomendamos implementar las siguientes acciones correctivas de inmediato para frenar las fugas de dinero:", body_style))
    
    for idx, rec in enumerate(diagnostic_data['recommendations'], 1):
        # Assign urgency
        urgency = "ALTA"
        urg_color = "red"
        if "WhatsApp" in rec or "bio" in rec or "reseñas" in rec:
            urgency = "MEDIA"
            urg_color = "orange"
        if "Rediseño" in rec or "Estrategia" in rec or "móviles" in rec:
            urgency = "CRÍTICA"
            urg_color = "darkred"
            
        story.append(Paragraph(
            f"<b>{idx}. [{urgency}]</b> {rec}", 
            recommendation_style
        ))
        
    story.append(Spacer(1, 40))
    
    # -------------------------------------------------------------------------
    # CALL TO ACTION (CTA)
    # -------------------------------------------------------------------------
    cta_box_data = [
        [
            Paragraph(
                "<font color='white' size=14><b>¿Cómo solucionar estos problemas hoy mismo?</b></font><br/><br/>"
                "<font color='white'>Dipromasters ofrece soluciones personalizadas e integrales de aceleración digital. "
                "Hemos diseñado un plan a la medida para detener tus pérdidas estimadas e iniciar tu escala de clientes.<br/><br/>"
                "<b>Agenda tu consultoría gratuita de 15 minutos con un experto llamando o enviando WhatsApp al +34 600 000 000 o escribiendo a contacto@dipromasters.com.</b></font>",
                ParagraphStyle('CTABoxText', parent=body_style, textColor=colors.white, leading=16)
            )
        ]
    ]
    cta_table = Table(cta_box_data, colWidths=[letter[0]-108])
    cta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PRIMARY_COLOR),
        ('PADDING', (0,0), (-1,-1), 18),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, SECONDARY_COLOR),
    ]))
    
    story.append(KeepTogether([cta_table]))
    
    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)

def get_recommended_service(perfil):
    services = {
        "🌱 Principiante Digital": "Pack de Despegue Digital",
        "🚀 Estancado con Potencial": "Estrategia de Contenido + TikTok Ads",
        "🏆 Competidor Fuerte": "Optimización Web + Automatización",
        "😴 Inactivo con Audiencia": "Community Manager + Reactivación",
        "🤫 Fantasma Digital": "Gestión de Reputación + SEO Local",
        "🔗 Desconectado Digital": "Integración Omnicanal"
    }
    return services.get(perfil, "Plan de Consultoría Personalizado")
