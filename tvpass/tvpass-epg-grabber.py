import os
import gzip
import json
import xml.etree.ElementTree as ET
import requests

name = "tvpass"
save_as_gz = True  

output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "epgs")
os.makedirs(output_dir, exist_ok=True)  

output_file = os.path.join(output_dir, f"{name}-epg.xml")  
output_file_gz = output_file + ".gz"  
temp_gz_file = os.path.join(output_dir, f"{name}-temp.xml.gz")

tvg_json_url = "https://raw.githubusercontent.com/pigzillaaaaa/iptv-scraper/refs/heads/main/tvpass/tvpass-channels-data.json"

def fetch_tvg_ids_from_json(url):
    print(f"Fetching TVG IDs from {url}...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Extract tvg-ids from JSON
        tvg_ids = {channel["tvg-id"] for channel in data if "tvg-id" in channel}
        print(f"Loaded {len(tvg_ids)} TVG IDs.")
        return tvg_ids

    except requests.RequestException as e:
        print(f"Error fetching TVG IDs: {e}")
        return set()
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
        return set()

def download_file(url, destination, chunk_size=1024 * 1024):
    print(f"Downloading {url}...")
    
    try:
        with requests.get(url, stream=True, timeout=60) as response:
            if response.status_code != 200:
                print(f"Failed to fetch {url} - HTTP {response.status_code}")
                return False

            content_length = response.headers.get('Content-Length')
            if content_length:
                total_size = int(content_length)
                print(f"File size: {total_size / (1024 * 1024):.2f} MB")
            else:
                print("Warning: Content-Length is unknown.")

            with open(destination, 'wb') as file:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        print(f"\rDownloaded: {downloaded / (1024 * 1024):.2f} MB", end='', flush=True)
        
        print("\nDownload complete.")
        return True

    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return False

def extract_gz_to_xml(gz_file):
    """Extracts a .gz file and returns its XML root."""
    try:
        print("Decompressing .gz file...")
        with gzip.open(gz_file, 'rb') as f:
            decompressed_data = f.read()
        
        print(f"Decompression successful! Extracted {len(decompressed_data)} bytes.")
        return ET.fromstring(decompressed_data)

    except Exception as e:
        print(f"Failed to decompress or parse XML: {e}")
        return None

def filter_and_build_epg(urls):
    print("Fetching TVG IDs...")
    valid_tvg_ids = fetch_tvg_ids_from_json(tvg_json_url)
    if not valid_tvg_ids:
        print("No valid TVG IDs found. Exiting.")
        return

    root = ET.Element('tv')

    for url in urls:
        if not download_file(url, temp_gz_file):
            print(f"Skipping {url} due to download failure.")
            continue

        epg_data = extract_gz_to_xml(temp_gz_file)
        if epg_data is None:
            print(f"Skipping {url} due to decompression errors.")
            continue

        print(f"Processing XML from {url}...")

        # Process channels
        channel_count = 0
        for channel in epg_data.findall('channel'):
            tvg_id = channel.get('id')
            if tvg_id in valid_tvg_ids:
                root.append(channel)
                channel_count += 1
        print(f"Added {channel_count} channels.")

        # Process programs
        program_count = 0
        for programme in epg_data.findall('programme'):
            tvg_id = programme.get('channel')
            if tvg_id in valid_tvg_ids:
                title = programme.find('title')
                title_text = title.text if title is not None else 'No title'

                # Modify titles for specific sports
                if title_text in ['NHL Hockey', 'Live: NFL Football']:
                    subtitle = programme.find('sub-title')
                    subtitle_text = subtitle.text if subtitle is not None else 'No subtitle'
                    programme.find('title').text = f"{title_text} {subtitle_text}"

                root.append(programme)
                program_count += 1
        print(f"Added {program_count} programmes.")

    # Save XML file
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"New EPG saved to {output_file}")

    # Save compressed XML file
    if save_as_gz:
        with gzip.open(output_file_gz, 'wb') as f:
            tree.write(f, encoding='utf-8', xml_declaration=True)
        print(f"New EPG saved to {output_file_gz}")

    # Remove temporary file
    os.remove(temp_gz_file)

urls = [
    "https://epgshare01.online/epgshare01/epg_ripper_US1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_FANDUEL1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_US_LOCALS2.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_CA1.xml.gz",
    "http://m3u4u.com/epg/x79znkdzz3h49xrwygk2"
]

if __name__ == "__main__":
    filter_and_build_epg(urls)
