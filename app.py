import os
import logging
import json
import re
from datetime import datetime
from dotenv import load_dotenv
from flask import (Flask, Response, abort, jsonify, render_template, request,
                   send_from_directory, url_for)
import google.generativeai as genai

from blueprints.admin import bp as admin_bp
from blueprints.reviews import bp as reviews_bp
from connect_db import db as dbutil

# --- Gemini API Configuration ---
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        logging.info("Gemini API configured successfully.")
    except Exception as e:
        logging.error("Failed to configure Gemini API: %s", e)
else:
    logging.warning("GEMINI_API_KEY not found in environment variables. Horoscope feature will not work.")

# --- App Setup ---
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
logging.basicConfig(level=logging.INFO)

SITE_NAME = os.getenv('SITE_NAME', 'TVHUB.ONLINE')
BASE_URL = os.getenv('BASE_URL', 'https://tvhub.online').rstrip('/')
CHANNELS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'channels.json')

# --- Caching ---
_api_cache = {}


def load_channels():
    """Load TV channel metadata from the shared JSON data file."""
    try:
        with open(CHANNELS_FILE, 'r', encoding='utf-8') as f:
            channels = json.load(f)
    except Exception as e:
        logging.error("Could not load channels data: %s", e)
        return {}
    return {item['channel_id'].lower(): item for item in channels if item.get('channel_id')}


def get_channel(channel_id):
    return load_channels().get((channel_id or '').lower())


def get_embed_sources(channel_data):
    return [
        source for source in channel_data.get('sources', [])
        if source.get('type') == 'embed' and source.get('url') and source.get('status') != 'inactive'
    ]


def select_embed_source(channel_data, source_id=None):
    embed_sources = get_embed_sources(channel_data)
    if source_id:
        for source in embed_sources:
            if source.get('id') == source_id:
                return source
    for source in embed_sources:
        if source.get('is_primary'):
            return source
    return embed_sources[0] if embed_sources else None


def build_home_source_links():
    source_links = {}
    for channel in load_channels().values():
        channel_id = channel.get('channel_id')
        links = []
        for source in channel.get('sources', []):
            if source.get('status') == 'inactive' or not source.get('url'):
                continue
            source_type = source.get('type')
            if source_type == 'embed':
                href = url_for('live', channel=channel_id, source=source.get('id'))
                label = 'ดูในเว็บ'
                external = False
            elif source_type in ('official', 'external'):
                href = source.get('url')
                label = source.get('label') or ('Official' if source_type == 'official' else 'External')
                external = True
            else:
                continue
            links.append({
                'id': source.get('id'),
                'label': label,
                'type': source_type,
                'href': href,
                'external': external,
            })
        source_links[channel_id] = links
    return source_links


@app.context_processor
def inject_site_context():
    return {
        'site_name': SITE_NAME,
        'base_url': BASE_URL,
        'now': datetime.now,
        'home_channel_sources': build_home_source_links,
        'channel_list': lambda: list(load_channels().values()),
    }

# --- Blueprints & DB Setup ---
def ensure_tables_and_register_blueprints():
    """Ensure necessary tables exist and register Flask blueprints."""
    try:
        create_sql = """
            CREATE TABLE IF NOT EXISTS movie_reviews (
                id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                title VARCHAR(255) NOT NULL,
                slug VARCHAR(255) NOT NULL UNIQUE,
                excerpt TEXT,
                cover_image TEXT,
                rating DECIMAL(3,1) DEFAULT 0.0,
                tags TEXT,
                body LONGTEXT,
                published_at DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        dbutil.sql_run_commit(create_sql)
        logging.info("`movie_reviews` table checked/created successfully.")
    except Exception as e:
        logging.error(f"Could not ensure `movie_reviews` table exists: {e}")

    # reviews blueprint expects '/reviews' prefix; admin blueprint already has '/admin' inside
    app.register_blueprint(reviews_bp, url_prefix='/reviews')
    app.register_blueprint(admin_bp)
    logging.info("Blueprints registered.")

ensure_tables_and_register_blueprints()


# --- Base Routes ---
@app.route('/')
def homepage():
    """Renders the main homepage."""
    return render_template('homepage_new.html')

@app.route('/live/<channel>')
def live(channel):
    """Renders the live stream page for a configured channel."""
    channel_data = get_channel(channel)
    if not channel_data:
        abort(404)

    sources = channel_data.get('sources', [])
    selected_source = select_embed_source(channel_data, request.args.get('source'))
    embed_sources = get_embed_sources(channel_data)
    external_sources = [
        source for source in sources
        if source.get('type') in ('official', 'external') and source.get('url') and source.get('status') != 'inactive'
    ]
    template_data = dict(channel_data)
    template_data.update({
        'stream_link': selected_source['url'] if selected_source else None,
        'current_source': selected_source,
        'embed_sources': embed_sources,
        'external_sources': external_sources,
    })
    return render_template('live.html', canonical_url=request.base_url, **template_data)

# --- Legal/Info Pages ---
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# --- SEO & Static Files ---
@app.route('/sitemap.xml')
def sitemap():
    """Generates a sitemap.xml for SEO."""
    try:
        static_urls = [
            url_for('homepage', _external=True),
            url_for('privacy', _external=True),
            url_for('terms', _external=True),
            url_for('contact', _external=True),
            url_for('horoscope_list', _external=True),
            url_for('horoscope_daily_page', _external=True),
            url_for('horoscope_birth_page', _external=True),
        ]

        rows = dbutil.sql_fetchall("SELECT slug FROM movie_reviews ORDER BY id DESC") or []
        movie_urls = [url_for('reviews.detail_movie', slug=row['slug'], _external=True) for row in rows]

        zodiacs = list(ZODIAC_SIGNS.keys())
        horoscope_urls = [url_for('horoscope_detail', sign=z, _external=True) for z in zodiacs]

        all_urls = set(static_urls + movie_urls + horoscope_urls)

        sitemap_xml = render_template('sitemap.xml', urls=all_urls)
        return Response(sitemap_xml, mimetype='application/xml')
    except Exception as e:
        logging.error(f"Error generating sitemap: {e}")
        return "Error generating sitemap.", 500

@app.route('/ads.txt')
def ads_txt():
    """Serves the ads.txt file."""
    return send_from_directory(app.static_folder, 'ads.txt')

# --- Horoscope Feature (Gemini Powered) ---
ZODIAC_SIGNS = {
    'aries': 'ราศีเมษ', 'taurus': 'ราศีพฤษภ', 'gemini': 'ราศีเมถุน',
    'cancer': 'ราศีกรกฎ', 'leo': 'ราศีสิงห์', 'virgo': 'ราศีกันย์',
    'libra': 'ราศีตุลย์', 'scorpio': 'ราศีพิจิก', 'sagittarius': 'ราศีธนู',
    'capricorn': 'ราศีมังกร', 'aquarius': 'ราศีกุมภ์', 'pisces': 'ราศีมีน'
}
DAYS_OF_WEEK = {
    "monday": "วันจันทร์", "tuesday": "วันอังคาร", "wednesday": "วันพุธ",
    "thursday": "วันพฤหัสบดี", "friday": "วันศุกร์", "saturday": "วันเสาร์", "sunday": "วันอาทิตย์"
}

# --- Birthdate Helpers ---
THAI_WEEKDAYS_FULL = ["วันอาทิตย์","วันจันทร์","วันอังคาร","วันพุธ","วันพฤหัสบดี","วันศุกร์","วันเสาร์"]

CHINESE_ZODIAC_TH = ['ชวด (หนู)','ฉลู (วัว)','ขาล (เสือ)','เถาะ (กระต่าย)','มะโรง (มังกร)','มะเส็ง (งู)','มะเมีย (ม้า)','มะแม (แพะ)','วอก (ลิง)','ระกา (ไก่)','จอ (สุนัข)','กุน (หมู)']

def detect_western_zodiac(month: int, day: int) -> str:
    """Return western zodiac sign based on month/day."""
    # Thresholds: (month, day, sign) means from this date inclusive
    thresholds = [
        (1, 20, 'aquarius'),
        (2, 19, 'pisces'),
        (3, 21, 'aries'),
        (4, 20, 'taurus'),
        (5, 21, 'gemini'),
        (6, 21, 'cancer'),
        (7, 23, 'leo'),
        (8, 23, 'virgo'),
        (9, 23, 'libra'),
        (10, 23, 'scorpio'),
        (11, 22, 'sagittarius'),
        (12, 22, 'capricorn')
    ]
    # Default before Jan 20 is Capricorn
    sign = 'capricorn'
    for m, d, s in thresholds:
        if (month, day) >= (m, d):
            sign = s
    return sign

def detect_chinese_zodiac_th(year: int) -> str:
    # Reference cycle with 1900 as Rat (ชวด)
    idx = (year - 1900) % 12
    return CHINESE_ZODIAC_TH[idx]

def calc_age(birthdate: datetime) -> int:
    today = datetime.today().date()
    years = today.year - birthdate.year
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        years -= 1
    return years

def get_gemini_horoscope(sign: str) -> dict:
    """
    Generates a 7-day horoscope forecast using the Gemini API and caches it daily.
    """
    today_str = datetime.now().strftime('%Y-%m-%d')
    cache_key = f"horoscope_{sign}_{today_str}"

    if cache_key in _api_cache:
        logging.info(f"CACHE HIT for {cache_key}")
        return _api_cache[cache_key]

    logging.info(f"CACHE MISS for {cache_key}. Calling Gemini API.")

    if not GEMINI_API_KEY:
        msg = "Gemini API is not configured. Set GEMINI_API_KEY."
        logging.error(msg)
        return {"error": msg}

    try:
        thai_sign = ZODIAC_SIGNS.get(sign, sign)

        prompt = (
            "จงทำนายดวงชะตา 7 วัน (จันทร์-อาทิตย์) สำหรับราศี '"
            + str(thai_sign)
            + "' โดยตอบเป็น JSON object เท่านั้น ตามโครงสร้างที่กำหนด และห้ามใส่คำอธิบายอื่นๆ นอก JSON:\n"
            + "{\n"
            + "  \"monday\": {\"work\": \"...\", \"finance\": \"...\", \"love\": \"...\"},\n"
            + "  \"tuesday\": {\"work\": \"...\", \"finance\": \"...\", \"love\": \"...\"},\n"
            + "  \"wednesday\": {\"work\": \"...\", \"finance\": \"...\", \"love\": \"...\"},\n"
            + "  \"thursday\": {\"work\": \"...\", \"finance\": \"...\", \"love\": \"...\"},\n"
            + "  \"friday\": {\"work\": \"...\", \"finance\": \"...\", \"love\": \"...\"},\n"
            + "  \"saturday\": {\"work\": \"...\", \"finance\": \"...\", \"love\": \"...\"},\n"
            + "  \"sunday\": {\"work\": \"...\", \"finance\": \"...\", \"love\": \"...\"}\n"
            + "}"
        )

        # Prefer a current model and ask for JSON; fall back if unsupported
        model = None
        try:
            model = genai.GenerativeModel(model_name='gemini-2.5-flash', generation_config={
                'response_mime_type': 'application/json'
            })
        except Exception:
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
            except Exception:
                model = genai.GenerativeModel('gemini-2.5-flash')

        response = model.generate_content(prompt)

        # Safely extract text content
        resp_text = None
        try:
            resp_text = response.text if hasattr(response, 'text') else None
        except Exception:
            resp_text = None

        if not resp_text:
            # Try assembling from candidates/parts
            try:
                parts = []
                for c in getattr(response, 'candidates', []) or []:
                    for p in getattr(c, 'content', {}).parts or []:
                        if hasattr(p, 'text') and p.text:
                            parts.append(p.text)
                resp_text = "\n".join(parts) if parts else None
            except Exception:
                resp_text = None

        if not resp_text:
            logging.error(f"Empty response from Gemini for sign '{sign}'. Raw: {response}")
            return {"error": "AI returned empty response."}

        cleaned_text = re.sub(r'^```json\s*|```\s*$', '', resp_text.strip(), flags=re.IGNORECASE|re.MULTILINE)
        # As a fallback, try to extract the first JSON object in the text
        try:
            data = json.loads(cleaned_text)
        except json.JSONDecodeError:
            match = re.search(r'\{[\s\S]*\}', cleaned_text)
            if match:
                data = json.loads(match.group(0))
            else:
                logging.error(f"Gemini response not valid JSON for '{sign}'. Text: {cleaned_text[:500]}")
                return {"error": "Invalid response format from AI."}

        _api_cache[cache_key] = data
        return data

    except Exception as e:
        logging.error(f"Error calling Gemini API for sign '{sign}': {e}")
        return {"error": "Could not retrieve horoscope data."}


def get_gemini_daily() -> dict:
    """Generates today's general daily horoscope (no zodiac) and caches by date."""
    today_str = datetime.now().strftime('%Y-%m-%d')
    cache_key = f"horoscope_daily_{today_str}"
    if cache_key in _api_cache:
        return _api_cache[cache_key]

    if not GEMINI_API_KEY:
        return {"error": "Gemini API is not configured. Set GEMINI_API_KEY."}

    try:
        prompt = (
            "จงทำนายดวงชะตาประจำวันนี้ (ไม่ระบุราศี) เป็นภาษาไทย โดยตอบเป็น JSON เท่านั้นและห้ามมีข้อความอื่นนอก JSON:\n"
            + "{\n"
            + "  \"work\": \"...\",\n"
            + "  \"finance\": \"...\",\n"
            + "  \"love\": \"...\"\n"
            + "}"
        )

        # Prefer 1.5 with JSON; fallback as needed
        try:
            model = genai.GenerativeModel(model_name='gemini-2.5-flash', generation_config={'response_mime_type': 'application/json'})
        except Exception:
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
            except Exception:
                model = genai.GenerativeModel('gemini-2.5-flash')

        response = model.generate_content(prompt)

        text = None
        try:
            text = response.text if hasattr(response, 'text') else None
        except Exception:
            text = None
        if not text:
            # fallback assemble
            try:
                parts = []
                for c in getattr(response, 'candidates', []) or []:
                    for p in getattr(c, 'content', {}).parts or []:
                        if hasattr(p, 'text') and p.text:
                            parts.append(p.text)
                text = "\n".join(parts) if parts else None
            except Exception:
                text = None
        if not text:
            return {"error": "AI returned empty response."}

        cleaned = re.sub(r'^```json\s*|```\s*$', '', text.strip(), flags=re.IGNORECASE|re.MULTILINE)
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            m = re.search(r'\{[\s\S]*\}', cleaned)
            if not m:
                return {"error": "Invalid response format from AI."}
            data = json.loads(m.group(0))

        _api_cache[cache_key] = data
        return data
    except Exception as e:
        logging.error(f"Error calling Gemini API for daily horoscope: {e}")
        return {"error": "Could not retrieve daily horoscope."}


def get_gemini_weekly_general() -> dict:
    """Generates a general weekly (Mon-Sun) horoscope without zodiac and caches by date."""
    today_str = datetime.now().strftime('%Y-%m-%d')
    cache_key = f"horoscope_weekly_general_{today_str}"
    if cache_key in _api_cache:
        return _api_cache[cache_key]

    if not GEMINI_API_KEY:
        return {"error": "Gemini API is not configured. Set GEMINI_API_KEY."}

    try:
        prompt = (
            "จงทำนายดวงชะตารายสัปดาห์ 7 วัน (จันทร์-อาทิตย์) แบบทั่วไป (ไม่ระบุราศี) เป็นภาษาไทย "
            "ให้เนื้อหาในแต่ละหัวข้อ 'การงาน', 'การเงิน', 'ความรัก' มีความละเอียดและน่าเชื่อถือ (อย่างน้อย 2-3 ประโยคต่อหัวข้อ) "
            "ใช้ภาษาธรรมชาติ ระบุบริบท สถานการณ์ หรือคำแนะนำที่ปฏิบัติได้จริง และหลีกเลี่ยงความกำกวมเกินจำเป็น "
            "ตอบเป็น JSON เท่านั้นและห้ามมีข้อความอื่นนอก JSON ตามโครงสร้างนี้:\n"
            + "{\n"
            + "  \"monday\": {\"work\": \"...\", \"finance\": \"...\", \"love\": \"...\"},\n"
            + "  \"tuesday\": {\"work\": \"...\", \"finance\": \"...\", \"love\": \"...\"},\n"
            + "  \"wednesday\": {\"work\": \"...\", \"finance\": \"...\", \"love\": \"...\"},\n"
            + "  \"thursday\": {\"work\": \"...\", \"finance\": \"...\", \"love\": \"...\"},\n"
            + "  \"friday\": {\"work\": \"...\", \"finance\": \"...\", \"love\": \"...\"},\n"
            + "  \"saturday\": {\"work\": \"...\", \"finance\": \"...\", \"love\": \"...\"},\n"
            + "  \"sunday\": {\"work\": \"...\", \"finance\": \"...\", \"love\": \"...\"}\n"
            + "}"
        )

        try:
            model = genai.GenerativeModel(model_name='gemini-2.5-flash', generation_config={'response_mime_type': 'application/json'})
        except Exception:
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
            except Exception:
                model = genai.GenerativeModel('gemini-2.5-flash')

        response = model.generate_content(prompt)

        text = None
        try:
            text = response.text if hasattr(response, 'text') else None
        except Exception:
            text = None
        if not text:
            try:
                parts = []
                for c in getattr(response, 'candidates', []) or []:
                    for p in getattr(c, 'content', {}).parts or []:
                        if hasattr(p, 'text') and p.text:
                            parts.append(p.text)
                text = "\n".join(parts) if parts else None
            except Exception:
                text = None
        if not text:
            return {"error": "AI returned empty response."}

        cleaned = re.sub(r'^```json\s*|```\s*$', '', text.strip(), flags=re.IGNORECASE|re.MULTILINE)
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            m = re.search(r'\{[\s\S]*\}', cleaned)
            if not m:
                return {"error": "Invalid response format from AI."}
            data = json.loads(m.group(0))

        _api_cache[cache_key] = data
        return data
    except Exception as e:
        logging.error(f"Error calling Gemini API for weekly general horoscope: {e}")
        return {"error": "Could not retrieve weekly horoscope."}

def get_gemini_birthdate(birthdate_str: str) -> dict:
    """Generates a personalized horoscope based on birth date (YYYY-MM-DD). Cached per birthdate per day."""
    today_str = datetime.now().strftime('%Y-%m-%d')
    cache_key = f"horoscope_birth_{birthdate_str}_{today_str}"
    if cache_key in _api_cache:
        return _api_cache[cache_key]

    if not GEMINI_API_KEY:
        return {"error": "Gemini API is not configured. Set GEMINI_API_KEY."}

    # Parse and compute metadata
    try:
        bd = datetime.strptime(birthdate_str, '%Y-%m-%d')
    except Exception:
        return {"error": "รูปแบบวันที่ไม่ถูกต้อง ใช้รูปแบบ YYYY-MM-DD"}

    if bd.date() > datetime.today().date():
        return {"error": "วันเกิดอยู่ในอนาคต กรุณาตรวจสอบอีกครั้ง"}

    weekday_th = THAI_WEEKDAYS_FULL[bd.weekday() if hasattr(bd, 'weekday') else 0]
    # Python weekday(): Monday=0 ... Sunday=6; THAI_WEEKDAYS_FULL starts Sunday=0, so adjust
    # Correct adjustment:
    wk = (bd.weekday() + 1) % 7  # convert Mon=0..Sun=6 -> Sun=0..Sat=6
    weekday_th = THAI_WEEKDAYS_FULL[wk]

    western_sign = detect_western_zodiac(bd.month, bd.day)
    western_sign_th = ZODIAC_SIGNS.get(western_sign, western_sign)
    chinese_th = detect_chinese_zodiac_th(bd.year)
    age_years = calc_age(bd)

    try:
        prompt = (
            "จงทำนายดวงเฉพาะบุคคลจากวันเดือนปีเกิด โดยใช้ข้อมูลต่อไปนี้เป็นบริบทและจงตอบเป็น JSON เท่านั้น (ห้ามมีข้อความนอก JSON):\n"
            f"วันเกิด: {bd.strftime('%Y-%m-%d')} ({weekday_th})\\n"
            f"ราศีตะวันตก: {ZODIAC_SIGNS.get(western_sign, western_sign)}\\n"
            f"นักษัตรจีน: {chinese_th}\\n"
            f"อายุโดยประมาณ: {age_years} ปี\\n\n"
            "ให้วิเคราะห์อย่างกระชับแต่มีสาระ น่าเชื่อถือ และมีคำแนะนำที่ปฏิบัติได้จริง โดยมีโครงสร้าง JSON ดังนี้:\n"
            "{\n"
            "  \"meta\": {\n"
            "    \"birthdate\": \"YYYY-MM-DD\", \"weekday_th\": \"...\", \"western_zodiac\": \"...\", \"thai_zodiac\": \"...\", \"age\": 0\n"
            "  },\n"
            "  \"overview\": \"...\",\n"
            "  \"personality\": \"...\",\n"
            "  \"work\": \"...\",\n"
            "  \"finance\": \"...\",\n"
            "  \"love\": \"...\",\n"
            "  \"health\": \"...\",\n"
            "  \"lucky\": { \"color\": \"...\", \"numbers\": [\"...\"], \"days\": [\"...\"] },\n"
            "  \"advice\": \"...\"\n"
            "}"
        )

        try:
            model = genai.GenerativeModel(model_name='gemini-1.5-pro', generation_config={'response_mime_type': 'application/json'})
        except Exception:
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
            except Exception:
                model = genai.GenerativeModel('gemini-2.5-flash')

        response = model.generate_content(prompt)

        text = None
        try:
            text = response.text if hasattr(response, 'text') else None
        except Exception:
            text = None
        if not text:
            try:
                parts = []
                for c in getattr(response, 'candidates', []) or []:
                    for p in getattr(c, 'content', {}).parts or []:
                        if hasattr(p, 'text') and p.text:
                            parts.append(p.text)
                text = "\n".join(parts) if parts else None
            except Exception:
                text = None
        if not text:
            return {"error": "AI returned empty response."}

        cleaned = re.sub(r'^```json\s*|```\s*$', '', text.strip(), flags=re.IGNORECASE|re.MULTILINE)
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            m = re.search(r'\{[\s\S]*\}', cleaned)
            if not m:
                return {"error": "Invalid response format from AI."}
            data = json.loads(m.group(0))

        # Enrich/ensure meta fields
        meta = data.get('meta', {}) if isinstance(data, dict) else {}
        meta.setdefault('birthdate', birthdate_str)
        meta.setdefault('weekday_th', weekday_th)
        meta.setdefault('western_zodiac', western_sign_th)
        meta.setdefault('thai_zodiac', chinese_th)
        meta.setdefault('age', age_years)
        if isinstance(data, dict):
            data['meta'] = meta

        _api_cache[cache_key] = data
        return data
    except Exception as e:
        logging.error(f"Error calling Gemini API for birth horoscope: {e}")
        return {"error": "Could not retrieve birthdate horoscope."}


def _normalize_birthdate_input(birthdate: str) -> str:
    """Accepts either ISO 'YYYY-MM-DD' (ค.ศ.) or 'dd/mm/yyyy' (พ.ศ./ค.ศ.) and returns ISO 'YYYY-MM-DD' (ค.ศ.).
    Raises ValueError if invalid.
    """
    if not birthdate or not isinstance(birthdate, str):
        raise ValueError("รูปแบบวันเกิดไม่ถูกต้อง")
    s = birthdate.strip()
    # ISO 8601
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", s)
    if m:
        # Validate by parsing
        dt = datetime.strptime(s, '%Y-%m-%d')
        return dt.strftime('%Y-%m-%d')
    # dd/mm/yyyy
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s)
    if m:
        d = int(m.group(1)); mth = int(m.group(2)); y = int(m.group(3))
        # If Thai Buddhist Era, convert to CE
        if y >= 2400:
            y -= 543
        dt = datetime(year=y, month=mth, day=d)
        return dt.strftime('%Y-%m-%d')
    raise ValueError("รูปแบบวันที่ไม่ถูกต้อง รองรับ YYYY-MM-DD หรือ dd/mm/yyyy (พ.ศ.)")

@app.route('/horoscope/')
def horoscope_list():
    """Displays the list of zodiac signs."""
    return render_template('horoscope/list.html', signs=ZODIAC_SIGNS)

@app.route('/horoscope/<sign>')
def horoscope_detail(sign: str):
    """Displays the 7-day horoscope for a given zodiac sign."""
    if sign not in ZODIAC_SIGNS:
        abort(404)
    # Render quickly; client will fetch data via API and show loading state meanwhile
    return render_template(
        'horoscope/detail.html',
        sign=sign,
        thai_sign=ZODIAC_SIGNS[sign],
        horoscope_data=None,
        days_of_week=DAYS_OF_WEEK,
        error=None
    )


@app.get('/api/horoscope/daily')
def api_horoscope_daily():
    data = get_gemini_daily()
    status = 200 if 'error' not in data else 500
    return data, status


@app.get('/api/horoscope/weekly')
def api_horoscope_weekly():
    data = get_gemini_weekly_general()
    status = 200 if 'error' not in data else 500
    return data, status


@app.route('/horoscope/daily')
def horoscope_daily_page():
    return render_template('horoscope/daily.html')


@app.get('/api/horoscope/<sign>')
def api_horoscope(sign: str):
    """Returns horoscope JSON for a given sign."""
    if sign not in ZODIAC_SIGNS:
        return {"error": "invalid sign"}, 404
    data = get_gemini_horoscope(sign)
    status = 200 if 'error' not in data else 500
    return data, status


# --- Birthdate Horoscope Routes ---
@app.route('/horoscope/birth')
def horoscope_birth_page():
    return render_template('horoscope/birth.html')


@app.post('/api/horoscope/birth')
def api_horoscope_birth():
    try:
        payload = request.get_json(silent=True) or {}
        birthdate_raw = payload.get('birthdate')
        if not birthdate_raw:
            return {"error": "กรุณาระบุวันเกิด (เช่น 24/08/2535 หรือ 1992-08-24) ในฟิลด์ birthdate"}, 400
        # Normalize dd/mm/yyyy (พ.ศ.) -> YYYY-MM-DD (ค.ศ.)
        try:
            birthdate_iso = _normalize_birthdate_input(birthdate_raw)
        except Exception as e:
            return {"error": str(e) or "รูปแบบวันเกิดไม่ถูกต้อง"}, 400
        data = get_gemini_birthdate(birthdate_iso)
        status = 200 if 'error' not in data else 400
        return data, status
    except Exception as e:
        logging.error(f"/api/horoscope/birth error: {e}")
        return {"error": "เกิดข้อผิดพลาดที่เซิร์ฟเวอร์"}, 500

# --- Channel Click Tracking ---
_CLICKS_FILE = os.path.join(os.path.dirname(__file__), 'channel_clicks.json')

def _load_clicks():
    try:
        with open(_CLICKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def _save_clicks(data):
    try:
        with open(_CLICKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Could not save clicks: {e}")

@app.post('/api/channel-click')
def api_channel_click():
    """Track a channel view click."""
    try:
        payload = request.get_json(silent=True) or {}
        name = (payload.get('name') or '').strip()
        if not name:
            return {"error": "missing name"}, 400
        logo = payload.get('logo', '')
        link = payload.get('link', '')

        clicks = _load_clicks()
        key = name
        if key in clicks:
            clicks[key]['clicks'] = clicks[key].get('clicks', 0) + 1
        else:
            clicks[key] = {'name': name, 'logo': logo, 'link': link, 'clicks': 1}
        _save_clicks(clicks)
        return {"ok": True}, 200
    except Exception as e:
        logging.error(f"/api/channel-click error: {e}")
        return {"error": str(e)}, 500

@app.get('/api/popular')
def api_popular():
    """Return top 10 popular channels."""
    clicks = _load_clicks()
    sorted_channels = sorted(clicks.values(), key=lambda x: x.get('clicks', 0), reverse=True)[:10]
    return {"channels": sorted_channels}, 200

@app.get('/api/channels/<channel>')
def api_channel(channel):
    channel_data = get_channel(channel)
    if not channel_data:
        return {"error": "channel not found"}, 404
    public_data = {
        k: v for k, v in channel_data.items()
        if k not in ('stream_link',)
    }
    public_data['sources'] = [
        {k: v for k, v in source.items() if not (source.get('type') == 'embed' and k == 'url')}
        for source in channel_data.get('sources', [])
    ]
    return jsonify(public_data)


# --- Main Execution ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
