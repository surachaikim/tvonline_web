
import requests
import xml.etree.ElementTree as ET
import sys

# Force encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://akkradet.github.io/IPTV-THAI/guide.xml'
print(f"Fetching {url}...")
try:
    r = requests.get(url, timeout=10)
    r.encoding = 'utf-8' # Ensure utf-8
    print(f"Status: {r.status_code}")
    
    root = ET.fromstring(r.text)
    
    print("\nAvailable Channels:")
    print("-" * 30)
    for channel in root.findall('channel'):
        cid = channel.get('id')
        name = channel.find('display-name').text
        print(f"{cid} : {name}")
    print("-" * 30)
    
except Exception as e:
    print(f"Error: {e}")
