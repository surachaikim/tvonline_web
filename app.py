from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)

# Store viewer analytics data
analytics_data = []

# Register blueprints here (to be added later)

@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/live/ch3')
def live_ch3():
    """Live Channel 3 HD"""
    # Channel data to pass to template
    channel_data = {
        'channel_id': 'ch3',
        'name': 'ช่อง 3 HD',
        'description': 'สถานีโทรทัศน์ไทยทีวีสีช่อง 3',
        'stream_link': 'https://p1.cdn.vet/live/ch3/i/ch3i.m3u8?sid=b5yMjYzMjE5YjI4YmVkNWZhYzE5ZQNGVkZWI2NzE0YzEwZDdm',
        'logo': '/static/img/3hd.png',
        'isLive': True
    }
    
    return render_template('live.html', **channel_data)

@app.route('/live/ch5')
def live_ch5():
    """Live Channel 5 HD"""
    # Channel data to pass to template
    channel_data = {
        'channel_id': 'ch5',
        'name': 'ช่อง 5 HD',
        'description': 'สถานีโทรทัศน์ไทยทีวีสีช่อง 5',
        'stream_link': 'https://p1.cdn.vet/live/ch5/i/ch5i.m3u8?sid=b5yMjYzMjE5YjI4YmVkNWZhYzE5ZQNGVkZWI2NzE0YzEwZDdm',
        'logo': '/static/img/channel5.png',
        'isLive': True
    }
    
    return render_template('live.html', **channel_data)

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
    
    return render_template('live.html', **channel_data)

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
    
    return render_template('live.html', **channel_data)


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
    
    return render_template('live.html', **channel_data)


if __name__ == '__main__':
    app.run(debug=True)
