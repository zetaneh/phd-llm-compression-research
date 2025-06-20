#!/usr/bin/env python3
"""
Script de mise à jour automatique du repository PhD
Auteur: Ayoub Abraich
Usage: python3 auto_update.py [message] [--force]
"""

import os
import sys
import subprocess
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path

class PhDRepoUpdater:
    def __init__(self, repo_path=None):
        """Initialise l'updater avec le chemin du repository"""
        if repo_path:
            self.repo_path = Path(repo_path)
        else:
            # Détecte automatiquement le chemin du repository
            self.repo_path = Path.cwd()
        
        # Vérifier qu'on est dans un repository Git
        if not (self.repo_path / ".git").exists():
            raise Exception(f"❌ Pas de repository Git trouvé dans {self.repo_path}")
        
        self.today = datetime.now()
        self.date_str = self.today.strftime("%Y-%m-%d")
        self.datetime_str = self.today.strftime("%Y-%m-%d %H:%M")
        
    def update_readme_dates(self):
        """Met à jour toutes les dates dans le README principal"""
        readme_path = self.repo_path / "README.md"
        
        if not readme_path.exists():
            print("⚠️  README.md non trouvé")
            return False
        
        # Lire le contenu actuel
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns de remplacement pour différents formats de date
        patterns = [
            # Format: **Last Updated:** YYYY-MM-DD
            (r'(\*\*Last Updated:\*\*\s*)(\d{4}-\d{2}-\d{2})', fr'\g<1>{self.date_str}'),
            # Format: *Last updated: YYYY-MM-DD*
            (r'(\*Last updated:\s*)(\d{4}-\d{2}-\d{2})(\*)', fr'\g<1>{self.date_str}\g<3>'),
            # Format: Last Updated: [Date]
            (r'(\*\*Last Updated:\*\*\s*)\[.*?\]', fr'\g<1>[{self.date_str}]'),
            # Format générique avec [Date]
            (r'\[Date\]', self.date_str),
            # Format: - **Last Updated:** quelque chose
            (r'(- \*\*Last Updated:\*\*\s*).*', fr'\g<1>{self.date_str}'),
        ]
        
        # Appliquer les remplacements
        updated = False
        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                updated = True
        
        # Mise à jour spécifique pour les statistiques de lecture
        reading_stats_pattern = r'(- \*\*Papers Read:\*\*\s*)(\d+|0)'
        if re.search(reading_stats_pattern, content):
            # Pour l'instant, garde le nombre existant, mais tu peux le modifier manuellement
            pass
        
        # Ajouter une section de dernière activité si elle n'existe pas
        if "## 📝 Recent Updates" not in content:
            recent_updates_section = f"""

## 📝 Recent Updates

### {self.date_str} - Repository Auto-Update
- Repository structure maintained and dates updated
- Continued research progress tracking

---
"""
            # Insérer avant la fin du fichier
            content = content.rstrip() + recent_updates_section
            updated = True
        else:
            # Mettre à jour la section des updates récents
            recent_pattern = r'(### )(\d{4}-\d{2}-\d{2})( - Recent Activities)'
            content = re.sub(recent_pattern, fr'\g<1>{self.date_str}\g<3>', content)
            updated = True
        
        if updated:
            # Sauvegarder le fichier mis à jour
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ README.md mis à jour avec la date {self.date_str}")
            return True
        else:
            print("ℹ️  README.md déjà à jour")
            return False

    def update_reading_list_dates(self):
        """Met à jour les dates dans la liste de lecture"""
        reading_list_path = self.repo_path / "papers" / "reading_list.md"
        
        if not reading_list_path.exists():
            print("⚠️  reading_list.md non trouvé")
            return False
        
        with open(reading_list_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Mettre à jour la date de dernière mise à jour
        pattern = r'(\*\*Last Updated:\*\*\s*)(\d{4}-\d{2}-\d{2})'
        new_content = re.sub(pattern, fr'\g<1>{self.date_str}', content)
        
        if new_content != content:
            with open(reading_list_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ reading_list.md mis à jour avec la date {self.date_str}")
            return True
        
        return False

    def update_research_files_dates(self):
        """Met à jour les dates dans les fichiers de recherche"""
        files_to_update = [
            "research/thesis-outline.md",
            "research/research-questions.md", 
            "conferences-deadlines/2025-deadlines.md"
        ]
        
        updated_files = []
        
        for file_path in files_to_update:
            full_path = self.repo_path / file_path
            if not full_path.exists():
                continue
                
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Patterns de mise à jour
            patterns = [
                (r'(\*\*Last Updated:\*\*\s*)(\d{4}-\d{2}-\d{2})', fr'\g<1>{self.date_str}'),
                (r'(\*Last Updated:\s*)(\d{4}-\d{2}-\d{2})', fr'\g<1>{self.date_str}'),
                (r'(\*Last updated:\s*)(\d{4}-\d{2}-\d{2})(\*)', fr'\g<1>{self.date_str}\g<3>'),
            ]
            
            updated = False
            for pattern, replacement in patterns:
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    content = new_content
                    updated = True
            
            if updated:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                updated_files.append(file_path)
        
        if updated_files:
            print(f"✅ Fichiers mis à jour: {', '.join(updated_files)}")
            return True
        
        return False

    def create_weekly_report(self):
        """Crée un nouveau rapport hebdomadaire si c'est lundi"""
        if self.today.weekday() == 0:  # Lundi
            # Calculer le numéro de semaine
            week_number = self.today.isocalendar()[1]
            
            reports_dir = self.repo_path / "research" / "progress" / "weekly-reports"
            report_name = f"week-{week_number:02d}-{self.today.year}.md"
            report_path = reports_dir / report_name
            
            if not report_path.exists():
                # Lire le template
                template_path = self.repo_path / "tools" / "templates" / "weekly-report-template.md"
                if template_path.exists():
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template = f.read()
                    
                    # Remplacer les placeholders
                    start_date = (self.today - timedelta(days=7)).strftime("%Y-%m-%d")
                    end_date = self.today.strftime("%Y-%m-%d")
                    
                    report_content = template.replace("[Number]", str(week_number))
                    report_content = report_content.replace("[Start Date]", start_date)
                    report_content = report_content.replace("[End Date]", end_date)
                    
                    # Sauvegarder le nouveau rapport
                    with open(report_path, 'w', encoding='utf-8') as f:
                        f.write(report_content)
                    
                    print(f"📊 Nouveau rapport hebdomadaire créé: {report_name}")
                    return True
        
        return False

    def get_git_status(self):
        """Obtient le statut Git du repository"""
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd=self.repo_path)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""

    def git_add_commit_push(self, commit_message=None, force=False):
        """Ajoute, commit et push les changements"""
        
        # Vérifier s'il y a des changements
        status = self.get_git_status()
        if not status and not force:
            print("ℹ️  Aucun changement à commiter")
            return True
        
        try:
            # Git add
            subprocess.run(['git', 'add', '.'], cwd=self.repo_path, check=True)
            print("✅ Fichiers ajoutés (git add)")
            
            # Créer le message de commit
            if not commit_message:
                # Compter les fichiers modifiés
                modified_files = len([line for line in status.split('\n') if line.strip()])
                commit_message = f"Auto-update repository - {self.datetime_str} ({modified_files} files updated)"
            
            # Git commit
            subprocess.run(['git', 'commit', '-m', commit_message], 
                         cwd=self.repo_path, check=True)
            print(f"✅ Commit créé: {commit_message}")
            
            # Git push
            subprocess.run(['git', 'push'], cwd=self.repo_path, check=True)
            print("✅ Changements push vers GitHub")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur Git: {e}")
            return False

    def generate_progress_summary(self):
        """Génère un résumé du progrès basé sur les fichiers"""
        summary = {
            'papers_read': 0,
            'notes_created': 0,
            'experiments': 0,
            'last_update': self.date_str
        }
        
        # Compter les notes de papers
        papers_dir = self.repo_path / "papers"
        if papers_dir.exists():
            for category_dir in papers_dir.iterdir():
                if category_dir.is_dir() and "notes" in [d.name for d in category_dir.iterdir()]:
                    notes_dir = category_dir / "notes"
                    if notes_dir.exists():
                        summary['notes_created'] += len([f for f in notes_dir.iterdir() if f.suffix == '.md'])
        
        # Compter les expériences
        experiments_dir = self.repo_path / "research" / "experiments"
        if experiments_dir.exists():
            summary['experiments'] = len([d for d in experiments_dir.iterdir() if d.is_dir() and d.name != "experiment-templates"])
        
        return summary

    def update_progress_in_readme(self, summary):
        """Met à jour les statistiques de progrès dans le README"""
        readme_path = self.repo_path / "README.md"
        
        if not readme_path.exists():
            return False
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns pour mettre à jour les statistiques
        patterns = [
            (r'(- \*\*Papers Read:\*\*\s*)(\d+)', fr'\g<1>{summary["notes_created"]}'),
            (r'(- \*\*Summary Notes:\*\*\s*)(\d+)', fr'\g<1>{summary["notes_created"]}'),
            (r'(\*\*Papers Read & Summarized:\*\*\s*)(\d+)', fr'\g<1>{summary["notes_created"]}'),
        ]
        
        updated = False
        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                updated = True
        
        if updated:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False

    def run_full_update(self, commit_message=None, force=False):
        """Exécute une mise à jour complète du repository"""
        print(f"🚀 Début de la mise à jour automatique - {self.datetime_str}")
        print("=" * 60)
        
        updates_made = []
        
        # 1. Mettre à jour les dates dans les fichiers
        if self.update_readme_dates():
            updates_made.append("README dates")
        
        if self.update_reading_list_dates():
            updates_made.append("Reading list dates")
        
        if self.update_research_files_dates():
            updates_made.append("Research files dates")
        
        # 2. Créer un rapport hebdomadaire si nécessaire
        if self.create_weekly_report():
            updates_made.append("Weekly report created")
        
        # 3. Mettre à jour les statistiques de progrès
        summary = self.generate_progress_summary()
        if self.update_progress_in_readme(summary):
            updates_made.append("Progress statistics")
        
        # 4. Afficher le résumé
        print("\n📊 Résumé du progrès:")
        print(f"   - Notes créées: {summary['notes_created']}")
        print(f"   - Expériences: {summary['experiments']}")
        print(f"   - Dernière mise à jour: {summary['last_update']}")
        
        # 5. Commit et push
        if updates_made or force:
            print(f"\n🔄 Mises à jour effectuées: {', '.join(updates_made)}")
            success = self.git_add_commit_push(commit_message, force)
            if success:
                print("\n✅ Mise à jour automatique terminée avec succès!")
            else:
                print("\n❌ Erreur lors de la mise à jour Git")
                return False
        else:
            print("\nℹ️  Aucune mise à jour nécessaire")
        
        return True

def main():
    """Fonction principale avec gestion des arguments"""
    parser = argparse.ArgumentParser(description='Mise à jour automatique du repository PhD')
    parser.add_argument('message', nargs='?', help='Message de commit personnalisé')
    parser.add_argument('--force', '-f', action='store_true', help='Forcer le commit même sans changements')
    parser.add_argument('--path', '-p', help='Chemin vers le repository')
    parser.add_argument('--quick', '-q', action='store_true', help='Mise à jour rapide (dates seulement)')
    
    args = parser.parse_args()
    
    try:
        # Initialiser l'updater
        updater = PhDRepoUpdater(args.path)
        
        if args.quick:
            # Mise à jour rapide - juste les dates
            print("⚡ Mise à jour rapide...")
            updater.update_readme_dates()
            updater.update_reading_list_dates()
            updater.git_add_commit_push("Quick update - dates refreshed", args.force)
        else:
            # Mise à jour complète
            updater.run_full_update(args.message, args.force)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()