from flask import Flask, render_template, request, jsonify, Response, url_for
import json
from datetime import datetime
import os

app = Flask(__name__)

# Store viewer analytics data
analytics_data = []

# Register blueprints here (to be added later)

@app.route('/')
def homepage():
    return render_template(
        'homepage.html',
        canonical_url=request.base_url,
        meta_description='ดูทีวีออนไลน์ สด ครบทุกช่อง ข่าว บันเทิง กีฬา เด็ก เพลง ไลฟ์สไตล์ รวมลิงก์จากช่องทางทางการ ดูสดได้ตลอด 24 ชั่วโมง',
    )


@app.route('/live/ch3')
def live_ch3():
    """Live Channel 3 HD"""
    # Channel data to pass to template
    channel_data = {
        'channel_id': 'ch3',
        'name': 'ช่อง 3 HD',
        'description': 'สถานีโทรทัศน์ไทยทีวีสีช่อง 3',
        'stream_link': 'https://lb1-live-mv.v2h-cdn.com/hls/ffae/3hd/3hd.m3u8',
        'logo': '/static/img/3hd.png',
        'isLive': True
    }
    
    return render_template('live.html', canonical_url=request.base_url, **channel_data)

@app.route('/live/ch5')
def live_ch5():
    """Live Channel 5 HD"""
    # Channel data to pass to template
    channel_data = {
        'channel_id': 'ch5',
        'name': 'ช่อง 5 HD',
        'description': 'สถานีโทรทัศน์ไทยทีวีสีช่อง 5',
        'stream_link': 'https://639bc5877c5fe.streamlock.net/tv5hdlive/tv5hdlive/playlist.m3u8',
        'logo': '/static/img/channel5.png',
        'isLive': True
    }
    
    return render_template('live.html', canonical_url=request.base_url, **channel_data)

@app.route('/live/ch7')
def live_ch7():
    """Live Channel 7 HD"""
    # Channel data to pass to template
    channel_data = {
        'channel_id': 'ch7',
        'name': 'ช่อง 7 HD',
        'description': 'สถานีโทรทัศน์ไทยทีวีสีช่อง 7',
        'stream_link': 'http://edge2a.v2h-cdn.com/hd_7/7hd.stream/playlist.m3u8',
        'logo': '/static/img/ch7-hd.png',
        'isLive': True
    }
    
    return render_template('live.html', canonical_url=request.base_url, **channel_data)

@app.route('/live/mcot')
def live_mcot():
    """Live Channel MCOT HD"""
    # Channel data to pass to template
    channel_data = {
        'channel_id': 'mcot',
        'name': 'MCOT HD',
        'description': 'สถานีโทรทัศน์ไทยทีวีสีช่อง MCOT',
        'stream_link': 'https://p1.cdn.vet/live/ch9/i/ch9i.m3u8?sid=b5yMzA2OTJkMDNjOTg0YmY2NmZhMwNzdlZGQ4NzAzOTg3ZGNh',
        'logo': '/static/img/mcot-hd.png',
        'isLive': True
    }
    
    return render_template('live.html', canonical_url=request.base_url, **channel_data)


@app.route('/live/thaipbs')
def live_thaipbs():
    """Live Channel Thai PBS HD"""
    # Channel data to pass to template
    channel_data = {
        'channel_id': 'thaipbs',
        'name': 'ไทยพีบีเอส HD',
        'description': 'สถานีโทรทัศน์ไทยพีบีเอส',
        'stream_link': 'https://edge2a.v2h-cdn.com/tpbs/tpbs.stream/playlist.m3u8',
        'logo': '/static/img/thaipbs.png',
        'isLive': True
    }
    
    return render_template('live.html', canonical_url=request.base_url, **channel_data)


@app.route('/live/MamaHD')
def live_MamaHD():
    """Live Channel Mama HD"""
    # Channel data to pass to template
    channel_data = {
        'channel_id': 'MamaHD',
        'name': 'Mama HD',
        'description': 'สถานีโทรทัศน์ Mama HD',
        'stream_link': 'http://stv.mediacdn.ru/live/cdn/mama/playlist.m3u8',
        'logo': '/static/img/cartoon.png',
        'isLive': True
    }
    
    return render_template('live.html', canonical_url=request.base_url, **channel_data)


@app.route('/live/FWTOON')
def live_FWTOON():
    """Live Channel FWTOON"""
    # Channel data to pass to template
    channel_data = {
        'channel_id': 'FWTOON',
        'name': 'FWTOON',
        'description': 'สถานีโทรทัศน์ FWTOON',
        'stream_link': 'https://freelive2.inwstream.com:1936/freelive-edge/fwtoon_fw-iptv.stream/chunks.m3u8?nimblesessionid=187607525&wmsAuthSign=c2VydmVyX3RpbWU9OS8yLzIwMjUgNzoxODo1OSBBTSZoYXNoX3ZhbHVlPTBHS25QK1RwVEMvZHpIN2U4YnJ0T2c9PSZ2YWxpZG1pbnV0ZXM9Mg==',
        'logo': '/static/img/cartoon.png',
        'isLive': True
    }
    
    return render_template('live.html', canonical_url=request.base_url, **channel_data)


@app.route('/live/4sport')
def live_4sport():
    """Live Channel 4 Sport"""
    # Channel data to pass to template
    channel_data = {
        'channel_id': '4sport',
        'name': '4 Sport',
        'description': 'สถานีโทรทัศน์ 4 Sport',
        'stream_link': 'https://pepsi.abntv.live/hls/4spstream.m3u8',
        'logo': '/static/img/cartoon.png',
        'isLive': True
    }
    
    return render_template('live.html', canonical_url=request.base_url, **channel_data)

# Global template context for SEO/site info
@app.context_processor
def inject_site_meta():
    base_url = request.url_root.rstrip('/') if request else ''
    return {
        'site_name': 'TVHUB.ONLINE',
        'base_url': base_url,
        'full_url': request.base_url if request else '',
    }


def _sitemap_urls():
    today = datetime.utcnow().date().isoformat()
    urls = [
        {'loc': url_for('homepage', _external=True), 'priority': '1.0', 'changefreq': 'daily', 'lastmod': today},
        {'loc': url_for('live_ch3', _external=True), 'priority': '0.8', 'changefreq': 'weekly', 'lastmod': today},
        {'loc': url_for('live_ch5', _external=True), 'priority': '0.8', 'changefreq': 'weekly', 'lastmod': today},
        {'loc': url_for('live_ch7', _external=True), 'priority': '0.8', 'changefreq': 'weekly', 'lastmod': today},
        {'loc': url_for('live_mcot', _external=True), 'priority': '0.7', 'changefreq': 'weekly', 'lastmod': today},
        {'loc': url_for('live_thaipbs', _external=True), 'priority': '0.8', 'changefreq': 'weekly', 'lastmod': today},
    ]
    return urls


@app.route('/sitemap.xml')
def sitemap():
    urls = _sitemap_urls()
    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    for u in urls:
        xml_parts.append('<url>')
        xml_parts.append(f'<loc>{u["loc"]}</loc>')
        xml_parts.append(f'<lastmod>{u["lastmod"]}</lastmod>')
        xml_parts.append(f'<changefreq>{u["changefreq"]}</changefreq>')
        xml_parts.append(f'<priority>{u["priority"]}</priority>')
        xml_parts.append('</url>')
    xml_parts.append('</urlset>')
    xml = '\n'.join(xml_parts)
    return Response(xml, mimetype='application/xml')


@app.route('/robots.txt')
def robots():
    sitemap_url = url_for('sitemap', _external=True)
    content = f"""User-agent: *
Allow: /
Sitemap: {sitemap_url}
"""
    return Response(content, mimetype='text/plain')


if __name__ == '__main__':
    app.run(debug=True)
