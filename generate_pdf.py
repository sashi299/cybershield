import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas

PDF_PATH = r"C:\Users\hp\Documents\cybershield\CyberShield_Presentation.pdf"

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_decorations(self, page_count):
        self.saveState()
        # Draw top accent bar
        self.setFillColor(colors.HexColor("#06B6D4"))
        self.rect(0, 8.5 * inch - 5, 11 * inch, 5, fill=1, stroke=0)
        
        # Draw bottom bar
        self.setFillColor(colors.HexColor("#0F172A"))
        self.rect(0, 0, 11 * inch, 0.4 * inch, fill=1, stroke=0)
        
        # Draw bottom line
        self.setStrokeColor(colors.HexColor("#1E293B"))
        self.setLineWidth(1)
        self.line(0.5 * inch, 0.4 * inch, 10.5 * inch, 0.4 * inch)
        
        # Footer text
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#38BDF8"))
        self.drawString(0.6 * inch, 0.15 * inch, "CYBERSHIELD | Real-Time AI Threat Protection Engine")
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        page_str = f"Slide {self._pageNumber} of {page_count}"
        self.drawRightString(10.4 * inch, 0.15 * inch, page_str)
        self.restoreState()


def build_presentation_pdf():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=landscape(letter),
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.5 * inch
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    style_badge = ParagraphStyle(
        'Badge',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#06B6D4"),
        spaceAfter=4,
        textTransform='uppercase'
    )

    style_title = ParagraphStyle(
        'SlideTitle',
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=2
    )

    style_subtitle = ParagraphStyle(
        'SlideSubtitle',
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=10
    )

    style_card_title = ParagraphStyle(
        'CardTitle',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#0284C7"),
        spaceAfter=6
    )

    style_card_title_danger = ParagraphStyle(
        'CardTitleDanger',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#DC2626"),
        spaceAfter=6
    )

    style_card_title_success = ParagraphStyle(
        'CardTitleSuccess',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#059669"),
        spaceAfter=6
    )

    style_bullet = ParagraphStyle(
        'CardBullet',
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=4
    )

    style_speaker_note = ParagraphStyle(
        'SpeakerNote',
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#334155")
    )

    style_speaker_header = ParagraphStyle(
        'SpeakerNoteHeader',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0284C7"),
        spaceAfter=2
    )

    story = []

    def make_card(title, bullets, mode="default"):
        p_title_style = style_card_title
        bg_color = colors.HexColor("#F8FAFC")
        border_color = colors.HexColor("#CBD5E1")
        
        if mode == "danger":
            p_title_style = style_card_title_danger
            bg_color = colors.HexColor("#FEF2F2")
            border_color = colors.HexColor("#FCA5A5")
        elif mode == "success":
            p_title_style = style_card_title_success
            bg_color = colors.HexColor("#ECFDF5")
            border_color = colors.HexColor("#6EE7B7")
        elif mode == "highlight":
            bg_color = colors.HexColor("#F0F9FF")
            border_color = colors.HexColor("#7DD3FC")

        elements = [Paragraph(title, p_title_style)]
        for b in bullets:
            elements.append(Paragraph(f"• {b}", style_bullet))

        card_table = Table([[elements]], colWidths=[4.7 * inch])
        card_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('BOX', (0, 0), (-1, -1), 1, border_color),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        return card_table

    def make_triple_card(title, bullets, mode="default"):
        p_title_style = style_card_title
        bg_color = colors.HexColor("#F8FAFC")
        border_color = colors.HexColor("#CBD5E1")
        
        if mode == "danger":
            p_title_style = style_card_title_danger
            bg_color = colors.HexColor("#FEF2F2")
            border_color = colors.HexColor("#FCA5A5")
        elif mode == "success":
            p_title_style = style_card_title_success
            bg_color = colors.HexColor("#ECFDF5")
            border_color = colors.HexColor("#6EE7B7")
        elif mode == "highlight":
            bg_color = colors.HexColor("#F0F9FF")
            border_color = colors.HexColor("#7DD3FC")

        elements = [Paragraph(title, p_title_style)]
        for b in bullets:
            elements.append(Paragraph(f"• {b}", style_bullet))

        card_table = Table([[elements]], colWidths=[3.1 * inch])
        card_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('BOX', (0, 0), (-1, -1), 1, border_color),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        return card_table

    def make_speaker_note(note_text):
        content = [
            Paragraph("🎙️ SPEAKER NOTES / PRESENTATION SCRIPT:", style_speaker_header),
            Paragraph(f'"{note_text}"', style_speaker_note)
        ]
        t = Table([[content]], colWidths=[9.8 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#0284C7")),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        return t

    # -------------------------------------------------------------
    # SLIDE 1: Title Slide
    # -------------------------------------------------------------
    title_hero = [
        Spacer(1, 0.4 * inch),
        Paragraph("🛡️ CYBERSHIELD", ParagraphStyle('HeroTitle', fontName='Helvetica-Bold', fontSize=36, leading=42, textColor=colors.HexColor("#0F172A"), alignment=1)),
        Spacer(1, 6),
        Paragraph("Real-Time AI-Powered Phishing, Smishing & Fraud Protection Engine", ParagraphStyle('HeroSub', fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=colors.HexColor("#0284C7"), alignment=1)),
        Spacer(1, 6),
        Paragraph("Autonomous Lockscreen & In-App Security for Messaging Ecosystems", ParagraphStyle('HeroTag', fontName='Helvetica', fontSize=11, leading=15, textColor=colors.HexColor("#64748B"), alignment=1)),
        Spacer(1, 0.4 * inch),
    ]
    
    meta_table = Table([
        [
            Paragraph("<b>Track</b>: Cybersecurity & AI / ML", style_bullet),
            Paragraph("<b>Platform</b>: Flutter + Native Android + React 19", style_bullet),
            Paragraph("<b>Inference Latency</b>: &lt;10ms Hybrid Core", style_bullet)
        ]
    ], colWidths=[3.2 * inch, 3.8 * inch, 2.8 * inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F0F9FF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#38BDF8")),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    title_hero.append(meta_table)
    title_hero.append(Spacer(1, 0.5 * inch))
    title_hero.append(make_speaker_note(
        "Good morning judges and mentors. Today, we are proud to present CyberShield — an intelligent, real-time protection system designed to safeguard users from the rapidly growing menace of phishing, WhatsApp smishing, and fraudulent QR codes."
    ))
    story.extend(title_hero)
    story.append(PageBreak())

    # -------------------------------------------------------------
    # SLIDE 2: Problem Statement
    # -------------------------------------------------------------
    story.append(Paragraph("CHALLENGE & MARKET NEED", style_badge))
    story.append(Paragraph("🚨 The Epidemic of Social Engineering & Smishing", style_title))
    story.append(Paragraph("Why existing cybersecurity tools fail everyday mobile users", style_subtitle))
    
    c1 = make_card("📱 Smishing & WhatsApp Fraud Surge", [
        "Over <b>3.4 billion phishing messages</b> are sent globally every day.",
        "Attackers impersonate trusted banks, courier delivery updates, electricity disconnections, and lottery schemes.",
        "Manufactured urgency forces victims into hasty actions ('Account suspended in 2 hours')."
    ], "danger")
    
    c2 = make_card("📷 The Rise of Quishing (QR Phishing)", [
        "Fraudulent QR codes placed over legitimate merchant payment stands and public parking meters.",
        "Bypasses standard email/browser gateways since QR codes conceal the true underlying URL from the human eye."
    ], "danger")

    c3 = make_card("⏳ The Failure of Manual Security Checkers", [
        "Existing scanners require users to <i>manually copy-paste</i> links into a browser website.",
        "Victims click first due to urgency or trust — by then, credentials or OTPs are already compromised."
    ], "highlight")

    c4 = make_card("❓ Black-Box Confusion", [
        "Legacy security apps show cryptic risk percentages without explaining <i>why</i> a link is harmful.",
        "Non-technical users receive no clear, actionable instructions on what immediate steps to take."
    ], "highlight")

    grid2 = Table([[c1, c2], [c3, c4]], colWidths=[4.9 * inch, 4.9 * inch])
    grid2.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    story.append(grid2)
    story.append(Spacer(1, 10))
    story.append(make_speaker_note(
        "Phishing has moved to mobile messaging. Traditional security tools fail because they expect the user to be suspicious first and copy-paste links. But social engineering relies on panic. We need a system that detects threats autonomously the millisecond they arrive."
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # SLIDE 3: Proposed Solution
    # -------------------------------------------------------------
    story.append(Paragraph("CORE SOLUTION", style_badge))
    story.append(Paragraph("💡 CyberShield: Autonomous Zero-Friction Defense", style_title))
    story.append(Paragraph("Proactive background intelligence bridging threat arrival and user action", style_subtitle))

    t1 = make_triple_card("⚡ Background Auto-Intercept", [
        "Native Android service silently monitors incoming WhatsApp, Telegram & SMS notifications.",
        "<b>Zero user friction</b>: scans run in the background without needing the app to be open.",
        "Instant high-priority lockscreen alerts with custom vibration patterns."
    ], "highlight")

    t2 = make_triple_card("🧠 Dual-Engine Hybrid AI", [
        "<b>70% Deterministic Rules</b>: Catches typosquatting, DGA domains, blacklisted TLDs, and OTP traps.",
        "<b>30% NLP Machine Learning</b>: TF-IDF vectorizer identifying semantic coercion and phishing syntax."
    ], "success")

    t3 = make_triple_card("🔍 Explainable AI (XAI)", [
        "Clear color-coded verdicts: <b>SAFE</b>, <b>SUSPICIOUS</b>, <b>DANGEROUS</b>.",
        "Itemizes exact Red Flag triggers (e.g. Typosquatting, Missing HTTPS) and gives concrete safety recommendations."
    ], "highlight")

    grid3 = Table([[t1, t2, t3]], colWidths=[3.25 * inch, 3.25 * inch, 3.25 * inch])
    grid3.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(grid3)
    story.append(Spacer(1, 20))
    story.append(make_speaker_note(
        "CyberShield transforms mobile security from reactive to autonomous. It runs quietly in the background, intercepts incoming messages, executes hybrid AI inference in under 10 milliseconds, and warns you immediately if a threat is detected."
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # SLIDE 4: Key Features & USP
    # -------------------------------------------------------------
    story.append(Paragraph("PRODUCT FEATURES", style_badge))
    story.append(Paragraph("🌟 Key Features & Unique Selling Propositions", style_title))
    story.append(Paragraph("Comprehensive multi-vector threat protection across digital ecosystems", style_subtitle))

    f1 = make_card("💬 WhatsApp & Messaging Auto-Shield", [
        "Monitors WhatsApp, WhatsApp Business, Telegram, SMS, Gmail, and Instagram.",
        "Configured with <code>VISIBILITY_PUBLIC</code> to ensure threat details are never masked by Android's 'Content Hidden' lockscreen policy."
    ])

    f2 = make_card("🌐 Deep URL Security Heuristics", [
        "Real-time live DNS resolution verifying active domains vs sinkholes.",
        "Catches deceptive brand typosquatting (e.g. <code>paypal-verify.xyz</code>, <code>sbi-reward.online</code>).",
        "Detects IP-based hosts, excessive subdomains, and URL shortener abuse."
    ])

    f3 = make_card("📷 Smart Hardware QR Scanner", [
        "Direct camera hardware stream with flash toggle, camera flip, and gallery image decoding.",
        "Intelligently auto-routes between website URLs and raw text payloads without throwing exceptions."
    ])

    f4 = make_card("📋 1-Tap Clipboard Quick Check & History", [
        "Scan copied links or text snippets straight from the system clipboard with a single tap.",
        "SQLite-backed persistent history log enabling incident review and audit trails."
    ])

    grid4 = Table([[f1, f2], [f3, f4]], colWidths=[4.9 * inch, 4.9 * inch])
    grid4.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    story.append(grid4)
    story.append(Spacer(1, 10))
    story.append(make_speaker_note(
        "CyberShield covers every threat vector — whether it's an incoming text, a banking link, a compromised QR code at a store, or a link copied from social media. Everything is analyzed with uniform intelligence."
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # SLIDE 5: Architecture
    # -------------------------------------------------------------
    story.append(Paragraph("TECHNICAL ARCHITECTURE", style_badge))
    story.append(Paragraph("🏗️ System Architecture & Data Pipeline", style_title))
    story.append(Paragraph("High-throughput, asynchronous client-server architecture", style_subtitle))

    a1 = make_card("📱 Frontend & Client Layer", [
        "<b>Flutter Mobile Client</b>: Provider state management, Dio HTTP networking with dynamic IP interceptor, dark glassmorphic UI.",
        "<b>Android Native Bridge</b>: Kotlin <code>NotificationListenerService</code> and <code>SmsReceiver</code> coupled via <code>MethodChannel</code>.",
        "<b>React 19 Web Dashboard</b>: Vite 6, Tailwind CSS, drag-and-drop QR file upload dropzone."
    ], "highlight")

    a2 = make_card("⚙️ Backend AI Services (FastAPI)", [
        "<b>REST Gateway (:8000)</b>: Asynchronous endpoints for <code>/api/analyze/url</code>, <code>/api/analyze/text</code>, <code>/api/analyze/qr</code>, <code>/api/history</code>.",
        "<b>Analysis Pipeline</b>: Rule Engine + TF-IDF ML Model + Explainable AI module.",
        "<b>Database Layer</b>: SQLite with WAL mode for persistent scan telemetry and audit logging."
    ], "success")

    grid5 = Table([[a1, a2]], colWidths=[4.9 * inch, 4.9 * inch])
    grid5.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(grid5)
    story.append(Spacer(1, 30))
    story.append(make_speaker_note(
        "Here is our architecture. Our mobile app leverages native Android background services to capture notification streams. These are dispatched to our high-throughput FastAPI backend over asynchronous REST APIs, evaluated against our hybrid detection core, and returned within milliseconds."
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # SLIDE 6: AI Engine
    # -------------------------------------------------------------
    story.append(Paragraph("AI & HEURISTICS", style_badge))
    story.append(Paragraph("🧠 The Hybrid AI Detection Engine", style_title))
    story.append(Paragraph("Combining deterministic cybersecurity heuristics with NLP statistical models", style_subtitle))

    m1 = make_card("📐 Rule Engine (70% Deterministic Weight)", [
        "<b>Typosquatting</b>: Detects deceptive brand imitations across 20+ top services (Google, PayPal, SBI, Amazon).",
        "<b>DGA Detection</b>: Calculates vowel ratios and consonant clustering to flag randomly generated malware domains.",
        "<b>Urgency Heuristics</b>: Identifies coercive phrases ('Account suspended', 'Verify immediately').",
        "<b>Safe Context Engine</b>: Whitelists legitimate transactional OTP formats ('Your OTP is 482910') to avoid false alarms."
    ], "highlight")

    m2 = make_card("🤖 Machine Learning Classifier (30% Weight)", [
        "Trained on 800+ real-world phishing and legitimate communications.",
        "TF-IDF N-gram feature extraction capturing semantic phishing cues.",
        "<b>Balanced Verdict Logic</b>:<br/>• <b>Dangerous</b>: combined &ge; 48 or rule_score &ge; 50<br/>• <b>Suspicious</b>: rule_score &ge; 15 or combined &ge; 18<br/>• <b>Safe</b>: Clean input (0 rules) &rarr; <b>85-95% Safe</b>"
    ], "success")

    grid6 = Table([[m1, m2]], colWidths=[4.9 * inch, 4.9 * inch])
    grid6.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(grid6)
    story.append(Spacer(1, 20))
    story.append(make_speaker_note(
        "Pure machine learning models often hallucinate or produce false alarms, while pure rules miss novel phrasing. CyberShield combines the interpretability and precision of deterministic security rules with the flexibility of ML NLP, delivering dependable verdicts."
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # SLIDE 7: Android Integration
    # -------------------------------------------------------------
    story.append(Paragraph("MOBILE ENGINEERING", style_badge))
    story.append(Paragraph("📱 Deep Android OS Integration & Resilience", style_title))
    story.append(Paragraph("Native Kotlin services engineered for real-world background execution", style_subtitle))

    n1 = make_card("🔔 Dual-Channel Notification Architecture", [
        "🚨 <b>Threat Channel (High Importance)</b>: Fires with custom vibration patterns (500ms bursts) and red alert banners for Dangerous/Suspicious threats.",
        "🟢 <b>Safe Channel (Default Importance)</b>: Provides non-intrusive confirmation that incoming messages were scanned and verified safe."
    ])

    n2 = make_card("🔓 Zero-Masking Lockscreen Visibility", [
        "Explicitly configured with <code>Notification.VISIBILITY_PUBLIC</code>.",
        "Eliminates Android 12/13/14's default 'Content Hidden' lockscreen masking so threat details are immediately visible."
    ])

    n3 = make_card("⚙️ Dynamic Network IP Synchronization", [
        "Native services read backend server IP dynamically from <code>SharedPreferences</code> (<code>flutter.server_ip</code>).",
        "Allows the app to seamlessly adapt when testing across changing WiFi networks."
    ], "highlight")

    n4 = make_card("🔋 Battery & Memory Efficiency", [
        "Event-driven architecture: zero background CPU polling when idle.",
        "Executes analysis on dedicated background worker threads without blocking main UI rendering."
    ], "highlight")

    grid7 = Table([[n1, n2], [n3, n4]], colWidths=[4.9 * inch, 4.9 * inch])
    grid7.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    story.append(grid7)
    story.append(Spacer(1, 10))
    story.append(make_speaker_note(
        "Our Android implementation is built for real-world resilience. We solved platform-specific challenges like background process limits, notification permissions, and lockscreen privacy masking to ensure users get immediate, clear visibility of potential threats."
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # SLIDE 8: Web Dashboard
    # -------------------------------------------------------------
    story.append(Paragraph("WEB PLATFORM", style_badge))
    story.append(Paragraph("💻 React 19 Web Command Center", style_title))
    story.append(Paragraph("Modern desktop security suite for power users and administrators", style_subtitle))

    w1 = make_card("🖥️ Unified Multi-Vector Scanner", [
        "Dedicated interactive tabs for <b>URL Scans</b>, <b>Email / SMS Text Scans</b>, and <b>QR Code Files</b>.",
        "Instant visual validation preventing invalid inputs or empty queries."
    ])

    w2 = make_card("📂 Drag-and-Drop QR Dropzone", [
        "HTML5 drag-and-drop file upload with client-side image preview.",
        "Decodes QR images instantly via OpenCV / Pyzbar backend processing."
    ])

    w3 = make_card("🌐 Live DNS Verification", [
        "Performs active DNS lookups to catch unregistered domains, parked ad-farms, and sinkholed malicious links."
    ], "highlight")

    w4 = make_card("📊 Real-Time SQLite Audit Feed", [
        "Displays a chronological table of all past scans, confidence scores, and triggered rules.",
        "Built-in Incident Reporting feature allowing users to flag false positives for model retraining."
    ], "highlight")

    grid8 = Table([[w1, w2], [w3, w4]], colWidths=[4.9 * inch, 4.9 * inch])
    grid8.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    story.append(grid8)
    story.append(Spacer(1, 10))
    story.append(make_speaker_note(
        "For desktop users and enterprise administrators, our Web Dashboard provides a fast, modern command center. It shares the exact same backend engine as our mobile app, providing consistent threat intelligence across devices."
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # SLIDE 9: Explainable AI
    # -------------------------------------------------------------
    story.append(Paragraph("USER EXPERIENCE & XAI", style_badge))
    story.append(Paragraph("🔍 Explainable AI (XAI) & Education", style_title))
    story.append(Paragraph("Empowering users with transparent reasoning rather than black-box scores", style_subtitle))

    x1 = make_card("🏷️ Itemized Red Flag Breakdown", [
        "Itemizes exact security violations (e.g. <i>Typosquatting Detected</i>, <i>Missing HTTPS Protocol</i>, <i>Urgency Language</i>).",
        "Assigns severity tags (High, Medium, Low) for transparent risk evaluation."
    ], "danger")

    x2 = make_card("📈 Statistical Confidence Gauge", [
        "Displays quantified percentage agreement between ML classifier and deterministic rule sets."
    ], "highlight")

    x3 = make_card("💡 Actionable Safety Guidelines", [
        "Provides practical, step-by-step instructions (e.g. <i>'Do not share OTP'</i>, <i>'Navigate to the official portal manually'</i>).",
        "Transforms security alerts into proactive user education."
    ], "success")

    x4 = make_card("🎨 Slide-Up Result Bottom Sheet", [
        "Animated modal with bold color badges (🟢 Safe, 🟡 Suspicious, 🔴 Dangerous).",
        "One-tap dismiss with automatic camera resumption for subsequent scans."
    ])

    grid9 = Table([[x1, x2], [x3, x4]], colWidths=[4.9 * inch, 4.9 * inch])
    grid9.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    story.append(grid9)
    story.append(Spacer(1, 10))
    story.append(make_speaker_note(
        "Security tools shouldn't just block; they should educate. When CyberShield detects a threat, it doesn't just say 'Blocked'. It shows the exact red flags found and tells the user exactly what to do next. This builds long-term user awareness."
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # SLIDE 10: Metrics
    # -------------------------------------------------------------
    story.append(Paragraph("VALIDATION & BENCHMARKS", style_badge))
    story.append(Paragraph("📊 Testing, Verification & Performance Metrics", style_title))
    story.append(Paragraph("Rigorously tested across real-world phishing datasets and edge cases", style_subtitle))

    k1 = make_card("✅ 28 / 28 Automated Tests Passed", [
        "<b>100% test pass rate</b> across unit, integration, and API test suites.",
        "Full coverage for URL normalizer, rate limiter, QR decoder, and false-positive reduction."
    ], "success")

    k2 = make_card("⚡ Sub-10 Millisecond Latency", [
        "Average backend inference turnaround in <b>&lt;10ms</b>.",
        "Ensures zero lag on incoming mobile message notifications."
    ], "highlight")

    k3 = make_card("🎯 Zero False Positives on Clean Text", [
        "Casual text (<i>'Hi bro let us meet tomorrow'</i>) scores <b>88.5% Safe</b> with 0 flags.",
        "Legitimate bank transactional OTP messages correctly recognized as safe."
    ])

    k4 = make_card("🚨 96%+ Precision on Malicious URLs", [
        "Impersonated domains (<code>paypal-security-update.xyz</code>) reliably flagged with <b>96.0% Dangerous</b> confidence."
    ], "danger")

    grid10 = Table([[k1, k2], [k3, k4]], colWidths=[4.9 * inch, 4.9 * inch])
    grid10.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    story.append(grid10)
    story.append(Spacer(1, 10))
    story.append(make_speaker_note(
        "We benchmarked and verified our entire stack with 28 automated integration tests covering URL parsing, false-positive prevention, OTP safety, and QR decoders. Everything executes in sub-10 milliseconds with high accuracy."
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # SLIDE 11: Roadmap
    # -------------------------------------------------------------
    story.append(Paragraph("FUTURE VISION", style_badge))
    story.append(Paragraph("🚀 Scaling CyberShield: Future Roadmap", style_title))
    story.append(Paragraph("Expanding the ecosystem across platforms and emerging threat vectors", style_subtitle))

    r1 = make_card("🧩 Browser Extension Ecosystem", [
        "Chromium & Firefox extension providing live DOM phishing link scanning and visual threat badges."
    ])

    r2 = make_card("🗣️ Vernacular & Multilingual AI", [
        "Expanding NLP models to detect smishing in Indian regional languages (Telugu, Hindi, Tamil, Kannada).",
        "Catching phonetically spelled financial scam lures (Hinglish / Telugish)."
    ], "highlight")

    r3 = make_card("🔓 Dark Web & Identity Shield", [
        "Integration with breach databases to alert users if their emails or passwords appear in active leaks."
    ])

    r4 = make_card("🏢 Enterprise SIEM & SOC Connectors", [
        "Exporting mobile threat telemetry to corporate Splunk and Elastic clusters for enterprise fleet protection."
    ])

    grid11 = Table([[r1, r2], [r3, r4]], colWidths=[4.9 * inch, 4.9 * inch])
    grid11.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    story.append(grid11)
    story.append(Spacer(1, 10))
    story.append(make_speaker_note(
        "Looking ahead, our vision is to expand CyberShield into browser extensions, integrate vernacular language processing for regional scams, and add identity breach monitoring to create an all-in-one digital defense platform."
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # SLIDE 12: Conclusion
    # -------------------------------------------------------------
    conclusion_hero = [
        Spacer(1, 0.3 * inch),
        Paragraph("🛡️ CYBERSHIELD", ParagraphStyle('HeroTitle2', fontName='Helvetica-Bold', fontSize=32, leading=38, textColor=colors.HexColor("#0F172A"), alignment=1)),
        Spacer(1, 6),
        Paragraph("Protecting Every Click. Securing Every Message.", ParagraphStyle('HeroTag2', fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=colors.HexColor("#0284C7"), alignment=1)),
        Spacer(1, 0.3 * inch),
    ]

    t_summary = Table([
        [
            Paragraph("<b>⚡ Autonomous</b><br/><font size=8 color='#64748B'>Zero-friction WhatsApp & SMS monitoring</font>", style_bullet),
            Paragraph("<b>🧠 Explainable AI</b><br/><font size=8 color='#64748B'>Itemized Red Flags & clear safety tips</font>", style_bullet),
            Paragraph("<b>📊 Production-Ready</b><br/><font size=8 color='#64748B'>28/28 tests passed, sub-10ms response</font>", style_bullet)
        ]
    ], colWidths=[3.2 * inch, 3.2 * inch, 3.2 * inch])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    conclusion_hero.append(t_summary)
    conclusion_hero.append(Spacer(1, 0.3 * inch))
    conclusion_hero.append(Paragraph("<b>Thank You! We are open for Questions.</b>", ParagraphStyle('Thanks', fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=colors.HexColor("#0F172A"), alignment=1)))
    conclusion_hero.append(Spacer(1, 0.3 * inch))
    conclusion_hero.append(make_speaker_note(
        "To conclude, CyberShield bridges the critical gap between threat arrival and user action through intelligent, real-time background protection. Thank you judges. We are now open for questions!"
    ))
    story.extend(conclusion_hero)

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF at: {PDF_PATH}")

if __name__ == "__main__":
    build_presentation_pdf()
