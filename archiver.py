import os
import re
import time
import json
import requests
import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

def load_config():
    """Loads configuration from config.json."""
    config_path = Path(__file__).parent / "config.json"
    if not config_path.exists():
        print("Error: config.json not found. Please copy config.json.example to config.json and edit it.")
        exit(1)
    with open(config_path, 'r') as f:
        return json.load(f)

def sanitize_filename(name):
    """Removes characters that are unsafe for filenames."""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def extract_source_url(file_path):
    """
    Parses the markdown file to find the URL in the Metadata section.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraction logic for Readwise Metadata
    metadata_match = re.search(r'## Metadata(.*?)(?:##|$)', content, re.DOTALL)
    if not metadata_match:
        return None
        
    metadata_text = metadata_match.group(1)
    url_match = re.search(r'^- URL:\s*(https?://[^\s]+)', metadata_text, re.MULTILINE | re.IGNORECASE)
    if url_match:
        return url_match.group(1)
    return None

def update_log(log_path, successes, warnings):
    """Updates the Markdown log file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if log_path.exists():
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    else:
        lines = ["# 📥 Archiver Log\n\n", "## ⚠️ Attention Required\n\n", "None currently.\n\n", "## ✅ Success Log\n\n", "| Date | Note | Status |\n", "| --- | --- | --- |\n"]

    try:
        header_idx = lines.index("## ⚠️ Attention Required\n")
        success_idx = lines.index("## ✅ Success Log\n")
    except ValueError:
        return # Skip logging if format is unrecognizable

    new_warnings = [f"- **{n}**: {m} ({timestamp})\n" for n, m in warnings]
    existing_warnings = [l for l in lines[header_idx+2:success_idx] if l.strip() and l.strip() != "None currently."]
    all_warnings = new_warnings + existing_warnings if (new_warnings + existing_warnings) else ["None currently.\n"]

    new_rows = [f"| {timestamp} | {n} | {m} |\n" for n, m in successes]
    
    final_content = lines[:header_idx+2] + all_warnings + ["\n"] + lines[success_idx:success_idx+3] + new_rows + lines[success_idx+3:]
    
    with open(log_path, 'w', encoding='utf-8') as f:
        f.writelines(final_content)

def archive_url(url, output_path):
    """Saves URL to PDF."""
    if url.lower().endswith(".pdf"):
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return True, "Direct PDF Download"
    else:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=60000)
            page.pdf(path=str(output_path), format="A4", print_background=True)
            browser.close()
        return True, "Webpage Rendered"

def main():
    config = load_config()
    vault_root = Path(config['vault_root'])
    source_dir = vault_root / config['source_rel_path']
    target_dir = vault_root / config['target_rel_path']
    log_path = target_dir / config['log_filename']
    
    target_dir.mkdir(parents=True, exist_ok=True)
    
    success_list = []
    warning_list = []
    
    for md_file in source_dir.glob("*.md"):
        # Process files from last 24 hours
        if time.time() - md_file.stat().st_mtime > 86400:
            continue
            
        pdf_path = target_dir / f"{sanitize_filename(md_file.stem)}.pdf"
        if pdf_path.exists():
            continue
            
        url = extract_source_url(md_file)
        if not url:
            continue
        
        if "readwise.io" in url.lower():
            warning_list.append((md_file.stem, "Readwise Reader link - requires manual archive."))
            continue
            
        try:
            _, method = archive_url(url, pdf_path)
            success_list.append((md_file.stem, method))
        except Exception as e:
            warning_list.append((md_file.stem, f"Error: {str(e)}"))

    if success_list or warning_list:
        update_log(log_path, success_list, warning_list)

if __name__ == "__main__":
    main()
