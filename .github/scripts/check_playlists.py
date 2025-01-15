import re
import requests

def check_playlist(url):
    try:
        print(f"Checking URL: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            content = response.text.strip()
            print(f"Content length: {len(content)}")
            if content == "#EXTM3U" or not content:
                return "🔴"  # Empty playlist
            return "🟢"  # Working playlist
    except Exception as e:
        print(f"Error checking {url}: {str(e)}")
    return "🔴"  # Failed to fetch

def update_readme():
    try:
        with open('readme.md', 'r', encoding='utf-8') as file:  # Changed to lowercase
            content = file.read()
            print("Successfully read readme.md")
    except Exception as e:
        print(f"Error reading readme.md: {str(e)}")
        return

    # Pattern to match URLs in backticks
    pattern = r'`(https://[^`]+)`'
    
    urls = re.findall(pattern, content)
    print(f"Found {len(urls)} URLs: {urls}")  # Debug print
    
    updated_content = content
    for url in urls:
        status = check_playlist(url)
        
        # Find the whole line containing the URL
        line_pattern = f'([^\n]*`{re.escape(url)}`[^\n]*)'
        line_match = re.search(line_pattern, updated_content)
        
        if line_match:
            old_line = line_match.group(1)
            # Remove existing status if any
            cleaned_line = re.sub(r' [🔴🟢]', '', old_line)
            # Add new status
            new_line = f"{cleaned_line} {status}"
            updated_content = updated_content.replace(old_line, new_line)
            print(f"Updated line for {url} with status {status}")

    try:
        with open('readme.md', 'w', encoding='utf-8') as file:  # Changed to lowercase
            file.write(updated_content)
            print("Successfully wrote readme.md")
    except Exception as e:
        print(f"Error writing readme.md: {str(e)}")

if __name__ == "__main__":
    update_readme()
