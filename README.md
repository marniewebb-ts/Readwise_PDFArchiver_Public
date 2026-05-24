# 📚 Readwise to PDF Archiver
*This project was entirely **vibe coded**—conceptualized and built through a conversation with Gemini CLI.*

Automatically archive the full text of your Readwise-synced articles as permanent, immutable PDFs within your Obsidian vault (or any local directory). Perfect for long-term knowledge management and bridging the gap to apps like DEVONthink.

## ✨ Features
*   **Link Rot Protection:** Converts web-based highlights into permanent PDF source files.
*   **Headless Rendering:** Uses Playwright (Chromium) to ensure PDFs look exactly like the original webpage.
*   **Smart Scanning:** Automatically detects the source URL from Readwise markdown metadata.
*   **Markdown Logging:** Keeps a running log of successful archives and manual requirements directly in your vault.

## 🛠️ Setup

### 1. Prerequisites
*   Python 3.8+
*   macOS (for the included `launchd` automation)

### 2. Installation
1.  Clone this repository.
2.  Install dependencies:
    ```bash
    pip install requests playwright
    playwright install chromium
    ```

### 3. Configuration
1.  Copy `config.json.example` to `config.json`.
2.  Edit `config.json` with your specific paths:
    ```json
    {
        "vault_root": "/Users/YOUR_USER/Documents/ObsidianVault",
        "source_rel_path": "Readwise/Articles",
        "target_rel_path": "Attachments/Source_PDFs",
        "log_filename": "!_Archiver_Log.md"
    }
    ```

## 🚀 Usage

### Manual Run
```bash
python archiver.py
```

### Automation (macOS)
The repository includes a sample `.plist` file for `launchd` to run this script every morning at 8:00 AM. 
1.  Edit the paths in the `.plist` to point to your Python executable and script.
2.  Move it to `~/Library/LaunchAgents/`.
3.  Load it: `launchctl load ~/Library/LaunchAgents/your.plist.name`

## ⚖️ Limitations
*   **Paywalls:** This script does not handle logins. Articles behind hard paywalls may only render the login screen.
*   **Readwise Reader:** Links pointing directly to the Readwise Reader (private uploads) are flagged for manual archiving to prevent authentication failures.

---
*Shared in case this is helpful to anyone else.*
