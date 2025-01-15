import re
import requests

def check_playlist(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            content = response.text.strip()
            if content == "#EXTM3U" or not content:
                return "🔴" # Empty playlist
            return "🟢" # Working playlist
    except:
        pass
    return "🔴" # Failed to fetch

def update_readme():
    with open('README.md', 'r', encoding='utf-8') as file:
        content = file.read()

    # Regular expression to find playlist URLs
    url_pattern = r'(https?://[^\s<>"]+?\.m3u[^\s<>"]*)'
    
    # Find all playlist URLs
    urls = re.findall(url_pattern, content)
    
    # Check each URL and update status
    for url in urls:
        status = check_playlist(url)
        
        # Create the status badge
        status_badge = f" {status}"
        
        # Find the line containing the URL
        line_pattern = f'(.*{re.escape(url)}.*)'
        line_match = re.search(line_pattern, content)
        
        if line_match:
            old_line = line_match.group(1)
            # Remove existing status if any
            cleaned_line = re.sub(r' [🔴🟢]', '', old_line)
            # Add new status
            new_line = f"{cleaned_line}{status_badge}"
            content = content.replace(old_line, new_line)
    
    # Write updated content back to README
    with open('readme.md', 'w', encoding='utf-8') as file:
        file.write(content)

if __name__ == "__main__":
    update_readme()
