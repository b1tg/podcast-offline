import xml.etree.ElementTree as ET
import requests
import sqlite3
import os, re, sys
from datetime import datetime
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Function to download file
def download_file(url, filename):
    if os.path.exists(filename):
        print(f"File already exists: {filename}")
        return
    print(f"Donwloading {url} to {filename}")
    response = requests.get(url, verify=False)
    with open(filename, 'wb') as file:
        file.write(response.content)
    print(f"Downloaded: {filename}")

# Download XML file
xml_url = "https://proxy.wavpub.com/caffebreve.xml"
# xml_filename = "podcast_feed.xml"
xml_filename = "caffebreve.xml"
if not os.path.exists(xml_filename):
    download_file(xml_url, xml_filename)

# Parse XML
tree = ET.parse(xml_filename)
root = tree.getroot()

# Connect to SQLite database
conn = sqlite3.connect('podcast.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS episodes (
    guid TEXT PRIMARY KEY,
    title TEXT,
    link TEXT,
    description TEXT,
    pub_date TEXT,
    audio_url TEXT,
    audio_length INTEGER,
    audio_type TEXT,
    author TEXT,
    image_url TEXT,
    duration TEXT,
    episode_type TEXT,
    episode_number INTEGER
)
''')
def sanitize_filename(filename):
    # Remove invalid characters and replace spaces with underscores
    return re.sub(r'[\\/*?:"<>|]', "", filename).replace(" ", "_")
# Create 'audio' directory if it doesn't exist
if not os.path.exists('audio'):
    os.makedirs('audio')

# Iterate through items and save to database
for item in root.findall('.//item'):
    guid = item.find('guid').text
    title = item.find('title').text
    link = item.find('link').text
    description = item.find('description').text
    pub_date = datetime.strptime(item.find('pubDate').text, '%a, %d %b %Y %H:%M:%S %z').isoformat()
    
    enclosure = item.find('enclosure')
    audio_url = enclosure.get('url')
    audio_length = enclosure.get('length')
    audio_type = enclosure.get('type')
    
    author = item.find('.//{http://www.itunes.com/dtds/podcast-1.0.dtd}author').text
    image_url = item.find('.//{http://www.itunes.com/dtds/podcast-1.0.dtd}image').get('href')
    duration = item.find('.//{http://www.itunes.com/dtds/podcast-1.0.dtd}duration').text
    episode_type = item.find('.//{http://www.itunes.com/dtds/podcast-1.0.dtd}episodeType').text
    episode_number = item.find('.//{http://www.itunes.com/dtds/podcast-1.0.dtd}episode').text

    # Insert data into database
    cursor.execute('''
    INSERT OR REPLACE INTO episodes 
    (guid, title, link, description, pub_date, audio_url, audio_length, audio_type, 
    author, image_url, duration, episode_type, episode_number)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (guid, title, link, description, pub_date, audio_url, audio_length, audio_type,
          author, image_url, duration, episode_type, episode_number))
    conn.commit()
    # Download audio file
    audio_filename = f"audio/{sanitize_filename(title)}-{guid}.{audio_url.split('.')[-1]}"
    download_file(audio_url, audio_filename)
    

# Commit changes and close connection

conn.close()

print("Podcast data saved to database and audio files downloaded.")
