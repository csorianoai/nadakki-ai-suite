# scripts/find_duplicate_content.py
import hashlib
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = ROOT / "agents"

def hash_file_content(file_path):
    """Generate hash of file content (ignoring whitespace)"""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        # Normalize: remove whitespace, lowercase
        normalized = ''.join(content.split()).lower()
        return hashlib.md5(normalized.encode()).hexdigest()
    except Exception:
        return None

def find_duplicates_by_content():
    """Find files with identical content"""
    hash_to_files = defaultdict(list)
    
    for py_file in AGENTS_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        file_hash = hash_file_content(py_file)
        if file_hash:
            hash_to_files[file_hash].append(py_file)
    
    # Filter only actual duplicates (more than 1 file)
    duplicates = {h: files for h, files in hash_to_files.items() if len(files) > 1}
    
    return duplicates

def find_duplicates_by_name():
    """Find files with similar names (snake_case vs camelCase)"""
    name_to_files = defaultdict(list)
    
    for py_file in AGENTS_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file) or py_file.name == "__init__.py":
            continue
        
        # Normalize name: remove underscores, lowercase
        normalized_name = py_file.stem.replace("_", "").lower()
        name_to_files[normalized_name].append(py_file)
    
    # Filter only actual duplicates
    duplicates = {n: files for n, files in name_to_files.items() if len(files) > 1}
    
    return duplicates

def main():
    print("🔍 Searching for duplicate files...")
    print("="*60)
    
    # By content
    content_dupes = find_duplicates_by_content()
    print(f"\n📄 DUPLICATES BY CONTENT: {len(content_dupes)} groups")
    for i, (hash_val, files) in enumerate(content_dupes.items(), 1):
        if i > 10:  # Show first 10
            print(f"... and {len(content_dupes) - 10} more groups")
            break
        print(f"\nGroup {i}: {len(files)} files with same content")
        for f in files:
            print(f"  - {f.relative_to(ROOT)}")
    
    # By name
    name_dupes = find_duplicates_by_name()
    print(f"\n📝 DUPLICATES BY NAME: {len(name_dupes)} groups")
    for i, (name, files) in enumerate(name_dupes.items(), 1):
        if i > 20:  # Show first 20
            print(f"... and {len(name_dupes) - 20} more groups")
            break
        print(f"\nGroup {i} - '{name}': {len(files)} files")
        for f in files:
            size_kb = f.stat().st_size / 1024
            print(f"  - {f.relative_to(ROOT)} ({size_kb:.1f} KB)")
    
    print("\n" + "="*60)
    print(f"📊 SUMMARY:")
    print(f"  Content duplicates: {sum(len(files)-1 for files in content_dupes.values())} files")
    print(f"  Name duplicates: {sum(len(files)-1 for files in name_dupes.values())} files")

if __name__ == "__main__":
    main()