#!/usr/bin/env python3
"""
Script de mise à jour quotidienne rapide
Usage: python3 quick_update.py [message]
"""

import os
import sys
import subprocess
import re
from datetime import datetime
from pathlib import Path

def quick_update():
    """Mise à jour rapide avec date et push automatique"""
    
    repo_path = Path.cwd()
    today = datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.now().strftime("%H:%M")
    
    print(f"⚡ Mise à jour rapide - {today} {time_now}")
    
    # Mettre à jour le README avec la date d'aujourd'hui
    readme_path = repo_path / "README.md"
    if readme_path.exists():
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacer les dates
        patterns = [
            r'(\*Last updated:\s*)(\d{4}-\d{2}-\d{2})(\*)',
            r'(\*\*Last Updated:\*\*\s*)(\d{4}-\d{2}-\d{2})',
        ]
        
        for pattern in patterns:
            content = re.sub(pattern, fr'\g<1>{today}\g<3>', content)
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ README mis à jour")
    
    # Git add, commit, push
    try:
        if len(sys.argv) > 1:
            message = " ".join(sys.argv[1:])
        else:
            message = f"Daily update - {today}"
        
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', message], check=True)
        subprocess.run(['git', 'push'], check=True)
        
        print(f"✅ Push réussi: {message}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    quick_update()
