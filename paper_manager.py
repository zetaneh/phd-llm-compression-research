#!/usr/bin/env python3
"""
Gestionnaire de papers pour repository PhD
Usage: python3 paper_manager.py [command] [options]
"""

import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import subprocess

class PaperManager:
    """Gestionnaire pour organiser et suivre les papers"""
    
    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path)
        self.papers_dir = self.repo_path / "papers"
        self.tracking_file = self.repo_path / "tools" / "paper_tracking.json"
        
        # Charger le suivi existant
        self.tracking_data = self.load_tracking_data()
    
    def load_tracking_data(self) -> Dict:
        """Charge les données de suivi des papers"""
        if self.tracking_file.exists():
            try:
                with open(self.tracking_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Erreur lecture tracking: {e}")
        
        return {
            "papers": {},
            "statistics": {
                "total_papers": 0,
                "read_papers": 0,
                "in_progress": 0,
                "high_priority": 0
            },
            "last_update": datetime.now().isoformat()
        }
    
    def save_tracking_data(self):
        """Sauvegarde les données de suivi"""
        self.tracking_file.parent.mkdir(parents=True, exist_ok=True)
        self.tracking_data["last_update"] = datetime.now().isoformat()
        
        with open(self.tracking_file, 'w', encoding='utf-8') as f:
            json.dump(self.tracking_data, f, indent=2, ensure_ascii=False)
    
    def scan_papers(self):
        """Scanne tous les papers dans le repository"""
        print("🔍 Scan des papers dans le repository...")
        
        papers_found = 0
        
        for category_dir in self.papers_dir.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith('.'):
                continue
            
            notes_dir = category_dir / "notes"
            if not notes_dir.exists():
                continue
            
            for note_file in notes_dir.glob("*.md"):
                paper_id = note_file.stem
                
                # Extraire les métadonnées du fichier
                metadata = self.extract_paper_metadata(note_file)
                
                if paper_id not in self.tracking_data["papers"]:
                    self.tracking_data["papers"][paper_id] = {
                        "title": metadata.get("title", "Unknown"),
                        "category": category_dir.name,
                        "file_path": str(note_file.relative_to(self.repo_path)),
                        "status": metadata.get("status", "🔴 Not Started"),
                        "priority": metadata.get("priority", "📚 Background"),
                        "date_added": metadata.get("date_read", datetime.now().isoformat()[:10]),
                        "arxiv_id": metadata.get("arxiv_id", ""),
                        "authors": metadata.get("authors", ""),
                        "tags": metadata.get("tags", [])
                    }
                    papers_found += 1
                else:
                    # Mettre à jour les métadonnées existantes
                    self.tracking_data["papers"][paper_id].update({
                        "status": metadata.get("status", self.tracking_data["papers"][paper_id]["status"]),
                        "priority": metadata.get("priority", self.tracking_data["papers"][paper_id]["priority"])
                    })
        
        # Mettre à jour les statistiques
        self.update_statistics()
        self.save_tracking_data()
        
        print(f"✅ Scan terminé: {papers_found} nouveaux papers trouvés")
        print(f"📊 Total papers: {self.tracking_data['statistics']['total_papers']}")
    
    def extract_paper_metadata(self, note_file: Path) -> Dict:
        """Extrait les métadonnées d'un fichier de note"""
        try:
            with open(note_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = {}
            
            # Extraire le titre (première ligne # )
            title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            if title_match:
                metadata["title"] = title_match.group(1).strip()
            
            # Extraire le statut
            status_match = re.search(r'\*\*Status:\*\*\s*([^*\n]+)', content)
            if status_match:
                metadata["status"] = status_match.group(1).strip()
            
            # Extraire la priorité
            priority_match = re.search(r'\*\*Priority:\*\*\s*([^*\n]+)', content)
            if priority_match:
                metadata["priority"] = priority_match.group(1).strip()
            
            # Extraire ArXiv ID
            arxiv_match = re.search(r'\*\*ArXiv ID:\*\*\s*([^\s\n]+)', content)
            if arxiv_match:
                metadata["arxiv_id"] = arxiv_match.group(1).strip()
            
            # Extraire les auteurs
            authors_match = re.search(r'\*\*Authors:\*\*\s*([^\n]+)', content)
            if authors_match:
                metadata["authors"] = authors_match.group(1).strip()
            
            # Extraire la date
            date_match = re.search(r'\*\*Date Read:\*\*\s*(\d{4}-\d{2}-\d{2})', content)
            if date_match:
                metadata["date_read"] = date_match.group(1)
            
            # Extraire les tags
            tags_match = re.search(r'`#([^`]+)`', content)
            if tags_match:
                tags_str = tags_match.group(1)
                metadata["tags"] = [tag.strip() for tag in tags_str.split('#') if tag.strip()]
            
            return metadata
            
        except Exception as e:
            print(f"⚠️  Erreur lecture {note_file}: {e}")
            return {}
    
    def update_statistics(self):
        """Met à jour les statistiques"""
        stats = {
            "total_papers": len(self.tracking_data["papers"]),
            "read_papers": 0,
            "in_progress": 0,
            "high_priority": 0,
            "by_category": {},
            "by_status": {"🔴 Not Started": 0, "🟡 In Progress": 0, "🟢 Completed": 0},
            "by_priority": {"⭐ High": 0, "🎯 Core Research": 0, "📚 Background": 0}
        }
        
        for paper_id, paper in self.tracking_data["papers"].items():
            # Compter par statut
            status = paper.get("status", "🔴 Not Started")
            if "🟢" in status or "Completed" in status:
                stats["read_papers"] += 1
            elif "🟡" in status or "Progress" in status:
                stats["in_progress"] += 1
            
            # Compter par priorité
            priority = paper.get("priority", "📚 Background")
            if "⭐" in priority or "High" in priority:
                stats["high_priority"] += 1
            
            # Compter par catégorie
            category = paper.get("category", "unknown")
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            
            # Compter statuts détaillés
            for status_key in stats["by_status"]:
                if status_key.split()[1] in status or status_key in status:
                    stats["by_status"][status_key] += 1
                    break
            
            # Compter priorités détaillées
            for priority_key in stats["by_priority"]:
                if priority_key.split()[1] in priority or priority_key in priority:
                    stats["by_priority"][priority_key] += 1
                    break
        
        self.tracking_data["statistics"] = stats
    
    def mark_paper_status(self, paper_pattern: str, new_status: str):
        """Marque le statut d'un paper"""
        
        # Trouver le paper correspondant
        matching_papers = []
        for paper_id, paper in self.tracking_data["papers"].items():
            if (paper_pattern.lower() in paper_id.lower() or 
                paper_pattern.lower() in paper.get("title", "").lower() or
                paper_pattern in paper.get("arxiv_id", "")):
                matching_papers.append((paper_id, paper))
        
        if not matching_papers:
            print(f"❌ Aucun paper trouvé pour: {paper_pattern}")
            return
        
        if len(matching_papers) > 1:
            print(f"🔍 Plusieurs papers trouvés pour '{paper_pattern}':")
            for i, (paper_id, paper) in enumerate(matching_papers):
                print(f"  {i+1}. {paper.get('title', paper_id)}")
            
            try:
                choice = int(input("Choisir un numéro: ")) - 1
                if 0 <= choice < len(matching_papers):
                    paper_id, paper = matching_papers[choice]
                else:
                    print("❌ Choix invalide")
                    return
            except ValueError:
                print("❌ Choix invalide")
                return
        else:
            paper_id, paper = matching_papers[0]
        
        # Mettre à jour le statut
        old_status = paper.get("status", "🔴 Not Started")
        paper["status"] = new_status
        
        # Mettre à jour le fichier de note
        file_path = self.repo_path / paper["file_path"]
        if file_path.exists():
            self.update_note_status(file_path, new_status)
        
        self.update_statistics()
        self.save_tracking_data()
        
        print(f"✅ Paper '{paper.get('title', paper_id)}' marqué: {old_status} → {new_status}")
    
    def update_note_status(self, note_file: Path, new_status: str):
        """Met à jour le statut dans le fichier de note"""
        try:
            with open(note_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remplacer le statut
            content = re.sub(r'(\*\*Status:\*\*\s*)[^\n]+', 
                           fr'\g<1>{new_status}', content)
            
            # Mettre à jour la date si changement vers "en cours" ou "complété"
            if "🟡" in new_status or "🟢" in new_status:
                today = datetime.now().strftime("%Y-%m-%d")
                content = re.sub(r'(\*\*Date Read:\*\*\s*)\d{4}-\d{2}-\d{2}', 
                               fr'\g<1>{today}', content)
            
            with open(note_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
        except Exception as e:
            print(f"⚠️  Erreur mise à jour note {note_file}: {e}")
    
    def list_papers(self, category: str = None, status: str = None, priority: str = None, limit: int = None):
        """Liste les papers avec filtres"""
        
        papers = list(self.tracking_data["papers"].items())
        
        # Appliquer les filtres
        if category:
            papers = [(pid, p) for pid, p in papers if category.lower() in p.get("category", "").lower()]
        
        if status:
            papers = [(pid, p) for pid, p in papers if status.lower() in p.get("status", "").lower()]
        
        if priority:
            papers = [(pid, p) for pid, p in papers if priority.lower() in p.get("priority", "").lower()]
        
        # Trier par date d'ajout (plus récent en premier)
        papers.sort(key=lambda x: x[1].get("date_added", ""), reverse=True)
        
        # Limiter si demandé
        if limit:
            papers = papers[:limit]
        
        # Afficher
        if not papers:
            print("📭 Aucun paper trouvé avec ces critères")
            return
        
        print(f"📚 {len(papers)} paper(s) trouvé(s):")
        print("-" * 80)
        
        for paper_id, paper in papers:
            title = paper.get("title", paper_id)[:60]
            status = paper.get("status", "Unknown")[:20]
            priority = paper.get("priority", "Unknown")[:15]
            category = paper.get("category", "Unknown")
            
            print(f"{status} | {priority} | {category} | {title}")
        
        print("-" * 80)
    
    def get_recommendations(self):
        """Recommande les prochains papers à lire"""
        
        print("💡 Recommandations de lecture:")
        print("=" * 50)
        
        # 1. Papers haute priorité non lus
        high_priority_unread = [
            (pid, p) for pid, p in self.tracking_data["papers"].items()
            if ("⭐" in p.get("priority", "") or "High" in p.get("priority", "")) and
               "🔴" in p.get("status", "")
        ]
        
        if high_priority_unread:
            print("🎯 Papers haute priorité à lire:")
            for paper_id, paper in high_priority_unread[:5]:
                print(f"   • {paper.get('title', paper_id)}")
        
        # 2. Papers de survey non lus
        survey_papers = [
            (pid, p) for pid, p in self.tracking_data["papers"].items()
            if "survey" in p.get("category", "").lower() and "🔴" in p.get("status", "")
        ]
        
        if survey_papers:
            print("\n📊 Papers de survey recommandés:")
            for paper_id, paper in survey_papers[:3]:
                print(f"   • {paper.get('title', paper_id)}")
        
        # 3. Papers récents non lus
        recent_papers = [
            (pid, p) for pid, p in self.tracking_data["papers"].items()
            if "🔴" in p.get("status", "")
        ]
        recent_papers.sort(key=lambda x: x[1].get("date_added", ""), reverse=True)
        
        if recent_papers:
            print("\n🆕 Papers récents à considérer:")
            for paper_id, paper in recent_papers[:3]:
                print(f"   • {paper.get('title', paper_id)} ({paper.get('date_added', 'Unknown')})")
    
    def generate_report(self):
        """Génère un rapport de progrès"""
        
        self.update_statistics()
        stats = self.tracking_data["statistics"]
        
        print("📊 Rapport de Progrès de Lecture")
        print("=" * 50)
        print(f"📅 Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print()
        
        # Statistiques générales
        print("📈 Vue d'ensemble:")
        print(f"   • Total papers: {stats['total_papers']}")
        print(f"   • Papers lus: {stats['read_papers']} ({stats['read_papers']/max(stats['total_papers'],1)*100:.1f}%)")
        print(f"   • En cours: {stats['in_progress']}")
        print(f"   • Haute priorité: {stats['high_priority']}")
        print()
        
        # Par catégorie
        print("📂 Par catégorie:")
        for category, count in sorted(stats.get("by_category", {}).items()):
            category_name = category.replace("-", " ").title()
            print(f"   • {category_name}: {count}")
        print()
        
        # Par statut
        print("📋 Par statut:")
        for status, count in stats.get("by_status", {}).items():
            print(f"   • {status}: {count}")
        print()
        
        # Objectifs
        total = stats['total_papers']
        if total > 0:
            read_percentage = stats['read_papers'] / total * 100
            
            print("🎯 Progression vers objectifs:")
            if read_percentage < 20:
                print("   📚 Phase d'apprentissage - Concentrez-vous sur les surveys")
            elif read_percentage < 50:
                print("   🔍 Phase d'exploration - Diversifiez vos lectures")
            elif read_percentage < 80:
                print("   🎯 Phase de spécialisation - Focalisez sur votre domaine")
            else:
                print("   🏆 Expertise avancée - Maintenez votre veille")
        
        print()
        
        # Sauvegarder le rapport
        report_path = self.repo_path / "research" / "progress" / f"reading_report_{datetime.now().strftime('%Y-%m-%d')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Rapport de Lecture - {datetime.now().strftime('%Y-%m-%d')}\n\n")
            f.write(f"## Statistiques Générales\n\n")
            f.write(f"- **Total papers:** {stats['total_papers']}\n")
            f.write(f"- **Papers lus:** {stats['read_papers']}\n")
            f.write(f"- **En cours:** {stats['in_progress']}\n")
            f.write(f"- **Haute priorité:** {stats['high_priority']}\n\n")
            
            f.write("## Détail par Catégorie\n\n")
            for category, count in sorted(stats.get("by_category", {}).items()):
                f.write(f"- **{category}:** {count}\n")
        
        print(f"💾 Rapport sauvegardé: {report_path}")

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Gestionnaire de papers PhD')
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Scan
    scan_parser = subparsers.add_parser('scan', help='Scanner tous les papers du repository')
    
    # List
    list_parser = subparsers.add_parser('list', help='Lister les papers')
    list_parser.add_argument('--category', '-c', help='Filtrer par catégorie')
    list_parser.add_argument('--status', '-s', help='Filtrer par statut')
    list_parser.add_argument('--priority', '-p', help='Filtrer par priorité')
    list_parser.add_argument('--limit', '-l', type=int, help='Limiter le nombre de résultats')
    
    # Mark
    mark_parser = subparsers.add_parser('mark', help='Marquer le statut d\'un paper')
    mark_parser.add_argument('paper', help='ID ou titre du paper')
    mark_parser.add_argument('status', choices=['started', 'progress', 'completed'], 
                           help='Nouveau statut')
    
    # Recommendations
    subparsers.add_parser('recommend', help='Obtenir des recommandations de lecture')
    
    # Report
    subparsers.add_parser('report', help='Générer un rapport de progrès')
    
    # Stats
    subparsers.add_parser('stats', help='Afficher les statistiques')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Détecter le repository
    repo_path = Path.cwd()
    if not (repo_path / ".git").exists():
        print("❌ Pas de repository Git trouvé")
        return
    
    manager = PaperManager(repo_path)
    
    # Exécuter la commande
    if args.command == 'scan':
        manager.scan_papers()
    
    elif args.command == 'list':
        manager.list_papers(
            category=args.category,
            status=args.status, 
            priority=args.priority,
            limit=args.limit
        )
    
    elif args.command == 'mark':
        status_map = {
            'started': '🟡 In Progress',
            'progress': '🟡 In Progress', 
            'completed': '🟢 Completed'
        }
        manager.mark_paper_status(args.paper, status_map[args.status])
    
    elif args.command == 'recommend':
        manager.get_recommendations()
    
    elif args.command == 'report':
        manager.generate_report()
    
    elif args.command == 'stats':
        manager.update_statistics()
        stats = manager.tracking_data["statistics"]
        print("📊 Statistiques rapides:")
        print(f"   Papers totaux: {stats['total_papers']}")
        print(f"   Papers lus: {stats['read_papers']}")
        print(f"   En cours: {stats['in_progress']}")

if __name__ == "__main__":
    main()