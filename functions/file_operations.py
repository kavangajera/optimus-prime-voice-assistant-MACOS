"""
Streamlined file operations module for Optimus Prime Voice Assistant
Handles copy, move, delete, create folder, rename, and details operations
"""
import os
import shutil
import json
import re
from pathlib import Path

try:
    from langchain_ollama import OllamaLLM
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("Warning: LangChain not available")


def parse_file_operation_command(command):
    """Parse file operation command using LLM"""
    if not LANGCHAIN_AVAILABLE:
        raise ImportError("LangChain not available")
    
    llm = OllamaLLM(model="mistral:instruct")
    
    prompt = f"""You are a file operation parser for macOS. Base directory: /Users/kavan

Parse the user command and return ONLY valid JSON (wrapped in ```json ```).

RULES:
1. User MUST specify exact locations: "move file1 in Downloads to ai in Documents"
2. Always construct FULL absolute paths starting with /Users/kavan
3. Handle multiple files: "move file1, file2, file3 in Downloads to ai in Documents"
4. Common folders: Downloads, Documents, Desktop, Pictures, Music, Movies
5. For nested paths: "move file1 in Downloads/subfolder to Documents/ai"
6. For navigation: "Go to Documents" or "Open Downloads directory"

RESPONSE FORMATS:

Navigate/Go to directory:
```json
{{
  "action": "navigate",
  "path": "/Users/kavan/Documents"
}}
```

Copy files:
```json
{{
  "action": "copy",
  "files": ["/Users/kavan/file1.txt", "/Users/kavan/file2.png"],
  "destination": "/Users/kavan/ai"
}}
```

Move files:
```json
{{
  "action": "move",
  "files": ["/Users/kavan/file1.png"],
  "destination": "/Users/kavan/ai"
}}
```

Delete files:
```json
{{
  "action": "delete",
  "files": ["/Users/kavan/file1.txt", "/Users/kavan/Desktop/file2.txt"]
}}
```

Create folder:
```json
{{
  "action": "create_folder",
  "folder_name": "new_folder",
  "destination": "/Users/kavan"
}}
```

Rename file:
```json
{{
  "action": "rename",
  "old_path": "/Users/kavan/old_name.txt",
  "new_name": "new_name.txt"
}}
```

Get details:
```json
{{
  "action": "details",
  "file_path": "/Users/kavan/file1.txt"
}}
```

IMPORTANT: 
- Return ONLY the JSON wrapped in ```json ```
- NO explanations, NO extra text
- current directory is /Users/kavan
- ** current path: /Users/kavan **
- ** use file extensions in full paths (e.g., .png, .txt) **
- Like in files or output_path use file_name.txt or file_name.png , etc.
- Always use full absolute paths
- if for files 'dot' means '.', replace accordingly
- if prompt is like 'rename kg 1.png to kg', interpret it as renaming 'kg1.png' to 'kg.png' remove spaces and add extension accordingly.

User command: '{command}'
"""
    
    response_llm = llm.invoke(prompt)
    print(f"LLM Response: {response_llm}")
    return response_llm


def expand_path(path_str):
    """Expand path to absolute path"""
    return str(Path(path_str).expanduser().resolve())


def execute_copy(files, destination):
    """Copy files to destination"""
    dest_path = Path(expand_path(destination))
    
    if not dest_path.exists():
        dest_path.mkdir(parents=True, exist_ok=True)
    
    results = []
    for file_path in files:
        src = Path(expand_path(file_path))
        if not src.exists():
            results.append(f"❌ Not found: {src.name}")
            continue
        
        try:
            if src.is_file():
                shutil.copy2(src, dest_path)
                results.append(f"✓ Copied: {src.name}")
            elif src.is_dir():
                dest_dir = dest_path / src.name
                if dest_dir.exists():
                    shutil.rmtree(dest_dir)
                shutil.copytree(src, dest_dir)
                results.append(f"✓ Copied folder: {src.name}")
        except Exception as e:
            results.append(f"❌ Error copying {src.name}: {e}")
    
    # Refresh Finder
    os.system(f'osascript -e \'tell application "Finder" to update folder POSIX file "{dest_path}"\'')
    
    return "\n".join(results)


def execute_move(files, destination):
    """Move files to destination"""
    dest_path = Path(expand_path(destination))
    
    if not dest_path.exists():
        dest_path.mkdir(parents=True, exist_ok=True)
    
    results = []
    for file_path in files:
        src = Path(expand_path(file_path))
        if not src.exists():
            results.append(f"❌ Not found: {src.name}")
            continue
        
        try:
            dest_file = dest_path / src.name
            if dest_file.exists():
                results.append(f"⚠️ Already exists: {src.name}")
                continue
            
            shutil.move(str(src), str(dest_file))
            results.append(f"✓ Moved: {src.name}")
        except Exception as e:
            results.append(f"❌ Error moving {src.name}: {e}")
    
    # Refresh Finder
    os.system(f'osascript -e \'tell application "Finder" to update folder POSIX file "{dest_path}"\'')
    
    return "\n".join(results)


def execute_delete(files):
    """Delete files"""
    results = []
    for file_path in files:
        path = Path(expand_path(file_path))
        if not path.exists():
            results.append(f"❌ Not found: {path.name}")
            continue
        
        try:
            if path.is_file():
                path.unlink()
                results.append(f"✓ Deleted: {path.name}")
            elif path.is_dir():
                shutil.rmtree(path)
                results.append(f"✓ Deleted folder: {path.name}")
        except Exception as e:
            results.append(f"❌ Error deleting {path.name}: {e}")
    
    return "\n".join(results)


def execute_create_folder(folder_name, destination):
    """Create folder in destination"""
    dest_path = Path(expand_path(destination))
    new_folder = dest_path / folder_name
    
    try:
        new_folder.mkdir(parents=True, exist_ok=True)
        # Refresh Finder
        os.system(f'osascript -e \'tell application "Finder" to update folder POSIX file "{dest_path}"\'')
        return f"✓ Created folder: {new_folder}"
    except Exception as e:
        return f"❌ Error creating folder: {e}"


def execute_rename(old_path, new_name):
    """Rename file"""
    old_file = Path(expand_path(old_path))
    
    if not old_file.exists():
        return f"❌ Not found: {old_file.name}"
    
    new_file = old_file.parent / new_name
    
    if new_file.exists():
        return f"❌ Already exists: {new_name}"
    
    try:
        old_file.rename(new_file)
        # Refresh Finder
        os.system(f'osascript -e \'tell application "Finder" to update folder POSIX file "{old_file.parent}"\'')
        return f"✓ Renamed: {old_file.name} → {new_name}"
    except Exception as e:
        return f"❌ Error renaming: {e}"


def execute_details(file_path):
    """Get file details"""
    path = Path(expand_path(file_path))
    
    if not path.exists():
        return f"❌ Not found: {path.name}"
    
    try:
        stat = path.stat()
        size_mb = stat.st_size / (1024 * 1024)
        
        details = f"""
📄 {path.name}
📁 Location: {path.parent}
📦 Size: {size_mb:.2f} MB
📂 Type: {'Folder' if path.is_dir() else 'File'}
🔒 Permissions: {oct(stat.st_mode)[-3:]}
"""
        return details.strip()
    except Exception as e:
        return f"❌ Error getting details: {e}"


def execute_navigate(path):
    """Navigate to directory and open in Finder"""
    dir_path = Path(expand_path(path))
    
    if not dir_path.exists():
        return f"❌ Directory not found: {dir_path}"
    
    if not dir_path.is_dir():
        return f"❌ Not a directory: {dir_path}"
    
    try:
        # Open directory in Finder
        os.system(f'open "{dir_path}"')
        return f"📂 Opened: {dir_path}"
    except Exception as e:
        return f"❌ Error opening directory: {e}"


def perform_file_operation(command):
    """Main function to perform file operations"""
    try:
        # Parse command
        response = parse_file_operation_command(command)
        
        # Extract JSON
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if not json_match:
            json_match = re.search(r'\{.*?\}', response, re.DOTALL)
        
        if not json_match:
            return "❌ Could not parse command. Please specify exact file locations."
        
        data = json.loads(json_match.group(1) if json_match.lastindex else json_match.group(0))
        action = data.get('action')
        
        # Execute action
        if action == "copy":
            return execute_copy(data['files'], data['destination'])
        
        elif action == "move":
            return execute_move(data['files'], data['destination'])
        
        elif action == "delete":
            return execute_delete(data['files'])
        
        elif action == "create_folder":
            return execute_create_folder(data['folder_name'], data['destination'])
        
        elif action == "rename":
            return execute_rename(data['old_path'], data['new_name'])
        
        elif action == "details":
            return execute_details(data['file_path'])
        
        elif action == "navigate":
            return execute_navigate(data['path'])
        
        else:
            return f"❌ Unknown action: {action}"
    
    except json.JSONDecodeError as e:
        return f"❌ Invalid JSON response: {e}"
    except KeyError as e:
        return f"❌ Missing required field: {e}"
    except Exception as e:
        return f"❌ Error: {e}"


# Test function
if __name__ == "__main__":
    test_commands = [
        "move kg.png to ai which in downloads folder",
    ]
    
    for cmd in test_commands:
        print(f"\n{'='*60}")
        print(f"Command: {cmd}")
        print(f"{'='*60}")
        result = perform_file_operation(cmd)
        print(result)