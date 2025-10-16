# Automatic searching in Safari using AppleScript
import subprocess

class SafariSearcher:
    def __init__(self):
        pass

    def search_in_safari(self, query):
        """Open Safari and perform a search with the given query"""
        try:
            # Escape the query to prevent AppleScript injection
            safe_query = query.replace('"', '\\"')
            script = f'''
            tell application "Safari"
                activate
                if (count of windows) = 0 then
                    make new document
                end if
                tell front window
                    set current tab to (make new tab with properties {{URL:"https://www.google.com/search?q={safe_query}"}})
                end tell
            end tell
            '''
            subprocess.run(['osascript', '-e', script], check=True)
            print(f"🔍 Searched in Safari: {query}")
            return True
        except Exception as e:
            print(f"❌ Failed to search in Safari: {e}")
            return False