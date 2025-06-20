#!/usr/bin/env python3
"""
ArXiv Paper Scraper pour recherche PhD sur la compression de LLM
Auteur: Ayoub Abraich
Usage: python3 arxiv_scraper.py [--category] [--max-results] [--days-back]
"""

import arxiv
import requests
import re
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import urlparse
from dataclasses import dataclass
from typing import List, Dict, Optional
import hashlib

@dataclass
class Paper:
    """Structure pour représenter un paper"""
    title: str
    authors: List[str]
    abstract: str
    arxiv_id: str
    pdf_url: str
    published: datetime
    categories: List[str]
    primary_category: str
    summary_url: str
    
class ArXivScraper:
    """Scraper principal pour arXiv"""
    
    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path)
        self.papers_dir = self.repo_path / "papers"
        self.scraped_papers_file = self.repo_path / "tools" / "scraped_papers.json"
        
        # Configuration des mots-clés par catégorie
        self.search_queries = {
            "quantization": [
                "quantization large language model",
                "quantized LLM",
                "neural network quantization transformer",
                "weight quantization",
                "activation quantization",
                "mixed precision",
                "int8 int4 quantization"
            ],
            "pruning": [
                "pruning large language model",
                "sparse neural network",
                "network pruning transformer",
                "structured pruning",
                "unstructured pruning",
                "magnitude pruning"
            ],
            "distillation": [
                "knowledge distillation large language model", 
                "model distillation transformer",
                "teacher student LLM",
                "distillation compression"
            ],
            "kv-cache": [
                "KV cache compression",
                "key value cache",
                "attention cache optimization",
                "memory efficient attention"
            ],
            "systems": [
                "LLM inference optimization",
                "large language model serving",
                "transformer inference acceleration",
                "GPU LLM optimization"
            ],
            "general": [
                "large language model compression",
                "LLM efficiency",
                "transformer compression",
                "neural compression"
            ]
        }
        
        # Mapping des catégories vers les dossiers
        self.category_mapping = {
            "quantization": "01-quantization",
            "pruning": "02-pruning-sparsity", 
            "distillation": "03-distillation",
            "kv-cache": "05-kv-cache-compression",
            "systems": "06-systems-serving",
            "general": "08-other-techniques"
        }
        
        # Charger les papers déjà scrapés
        self.scraped_papers = self.load_scraped_papers()
        
    def load_scraped_papers(self) -> set:
        """Charge la liste des papers déjà scrapés"""
        if self.scraped_papers_file.exists():
            try:
                with open(self.scraped_papers_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('arxiv_ids', []))
            except Exception as e:
                print(f"⚠️  Erreur lecture scraped_papers.json: {e}")
        return set()
    
    def save_scraped_papers(self):
        """Sauvegarde la liste des papers scrapés"""
        self.scraped_papers_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "last_update": datetime.now().isoformat(),
            "total_papers": len(self.scraped_papers),
            "arxiv_ids": list(self.scraped_papers)
        }
        
        with open(self.scraped_papers_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def search_papers(self, query: str, max_results: int = 50, days_back: int = 30) -> List[Paper]:
        """Recherche des papers sur arXiv"""
        
        print(f"🔍 Recherche: '{query}' (max {max_results} résultats, {days_back} derniers jours)")
        
        # Construire la requête avec contrainte de date
        since_date = datetime.now() - timedelta(days=days_back)
        
        try:
            # Configuration du client arXiv
            client = arxiv.Client(page_size=min(max_results, 100), delay_seconds=2.0, num_retries=3)
            
            # Recherche
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            papers = []
            for result in client.results(search):
                # Filtrer par date
                if result.published.replace(tzinfo=None) < since_date:
                    continue
                
                # Skip si déjà scrapé
                if result.get_short_id() in self.scraped_papers:
                    continue
                
                paper = Paper(
                    title=result.title.strip(),
                    authors=[author.name for author in result.authors],
                    abstract=result.summary.strip(),
                    arxiv_id=result.get_short_id(),
                    pdf_url=result.pdf_url,
                    published=result.published.replace(tzinfo=None),
                    categories=result.categories,
                    primary_category=result.primary_category,
                    summary_url=result.entry_id
                )
                
                papers.append(paper)
                self.scraped_papers.add(paper.arxiv_id)
                
                # Délai pour éviter de surcharger arXiv
                time.sleep(1)
            
            print(f"✅ Trouvé {len(papers)} nouveaux papers")
            return papers
            
        except Exception as e:
            print(f"❌ Erreur recherche arXiv: {e}")
            return []
    
    def categorize_paper(self, paper: Paper) -> str:
        """Détermine la catégorie d'un paper basée sur son contenu"""
        
        text = (paper.title + " " + paper.abstract).lower()
        
        # Mots-clés par catégorie avec poids
        category_keywords = {
            "quantization": {
                "quantization": 3, "quantized": 3, "quantize": 3,
                "int8": 2, "int4": 2, "bit": 2, "precision": 2,
                "weight": 1, "activation": 1
            },
            "pruning": {
                "pruning": 3, "prune": 3, "sparse": 3, "sparsity": 3,
                "magnitude": 2, "structured": 2, "unstructured": 2,
                "compression": 1
            },
            "distillation": {
                "distillation": 3, "distill": 3, "teacher": 2, "student": 2,
                "knowledge": 2, "compression": 1
            },
            "kv-cache": {
                "cache": 3, "kv": 3, "key-value": 3, "attention": 2,
                "memory": 2, "efficient": 1
            },
            "systems": {
                "serving": 3, "inference": 3, "deployment": 2, "optimization": 2,
                "gpu": 2, "cpu": 2, "hardware": 2, "system": 2,
                "throughput": 1, "latency": 1
            }
        }
        
        # Calculer les scores
        scores = {}
        for category, keywords in category_keywords.items():
            score = 0
            for keyword, weight in keywords.items():
                count = text.count(keyword)
                score += count * weight
            scores[category] = score
        
        # Retourner la catégorie avec le score le plus élevé
        if max(scores.values()) > 0:
            best_category = max(scores, key=scores.get)
            return self.category_mapping[best_category]
        
        # Par défaut
        return self.category_mapping["general"]
    
    def download_pdf(self, paper: Paper, category_dir: Path) -> Optional[Path]:
        """Télécharge le PDF d'un paper"""
        
        # Créer le dossier PDFs
        pdfs_dir = category_dir / "pdfs"
        pdfs_dir.mkdir(exist_ok=True)
        
        # Nom du fichier (nettoyé)
        safe_title = re.sub(r'[^\w\s-]', '', paper.title)[:80]
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        filename = f"{paper.arxiv_id}_{safe_title}.pdf"
        pdf_path = pdfs_dir / filename
        
        # Skip si déjà téléchargé
        if pdf_path.exists():
            return pdf_path
        
        try:
            print(f"📥 Téléchargement PDF: {paper.arxiv_id}")
            
            response = requests.get(paper.pdf_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(pdf_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ PDF téléchargé: {filename}")
            return pdf_path
            
        except Exception as e:
            print(f"❌ Erreur téléchargement PDF {paper.arxiv_id}: {e}")
            return None
    
    def create_paper_note(self, paper: Paper, category_dir: Path) -> Path:
        """Crée une note vide pour un paper"""
        
        notes_dir = category_dir / "notes"
        notes_dir.mkdir(exist_ok=True)
        
        # Nom du fichier note
        safe_title = re.sub(r'[^\w\s-]', '', paper.title)[:60]
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        note_filename = f"{paper.arxiv_id}_{safe_title}.md"
        note_path = notes_dir / note_filename
        
        # Skip si déjà créé
        if note_path.exists():
            return note_path
        
        # Créer le contenu de la note
        authors_str = ", ".join(paper.authors[:3])
        if len(paper.authors) > 3:
            authors_str += f" et {len(paper.authors) - 3} autres"
        
        note_content = f"""# {paper.title}

**Date Read:** {datetime.now().strftime("%Y-%m-%d")}  
**Status:** 🔴 Not Started  
**Priority:** ⭐ High / 🎯 Core Research / 📚 Background  

## 📄 Paper Information

**Authors:** {authors_str}  
**ArXiv ID:** {paper.arxiv_id}  
**Published:** {paper.published.strftime("%Y-%m-%d")}  
**Categories:** {', '.join(paper.categories)}  
**ArXiv Link:** {paper.summary_url}  
**PDF Link:** {paper.pdf_url}  

---

## 🎯 Research Context

**Problem Addressed:** [What specific problem does this paper solve?]

**Motivation:** [Why is this problem important?]

**Research Gap:** [What gap in existing work does this fill?]

---

## 🔑 Key Contributions

1. **[Main Contribution 1]**
   - [Detailed description]

2. **[Main Contribution 2]**
   - [Detailed description]

---

## 📋 Summary (3-5 sentences)

{paper.abstract[:500]}...

---

## 🛠️ Methodology

### Approach Overview
[High-level description of the method/approach]

### Key Innovations
- [Innovation 1]
- [Innovation 2]

---

## 📊 Results & Analysis

### Main Results
[Key experimental results and metrics]

### Performance Trade-offs
- **Accuracy vs. Compression:** [Analysis]
- **Speed vs. Memory:** [Analysis]

---

## 💡 Relevance to My Research

- [How this directly relates to your thesis objectives]
- [Specific techniques you could adapt/use]

---

## 🔍 Strengths & Weaknesses

### Strengths ✅
- [Strength 1]
- [Strength 2]

### Weaknesses ❌
- [Weakness 1]
- [Weakness 2]

---

## 🚀 Future Work & Ideas

### My Research Ideas Inspired by This Paper
- [Idea 1]: [Brief description]
- [Idea 2]: [Brief description]

---

## 🔗 Related Papers to Read Next

- [ ] [Related Paper 1]: [Why relevant]
- [ ] [Related Paper 2]: [Why relevant]

---

## 🏷️ Tags

`#arxiv` `#{paper.primary_category}` `#llm-compression` `#[add-specific-tags]`

---

**ArXiv ID:** {paper.arxiv_id}  
**Auto-generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
"""
        
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(note_content)
        
        print(f"📝 Note créée: {note_filename}")
        return note_path
    
    def update_reading_list(self, papers_by_category: Dict[str, List[Paper]]):
        """Met à jour les listes de lecture par catégorie"""
        
        for category, papers in papers_by_category.items():
            if not papers:
                continue
                
            category_dir = self.papers_dir / category
            reading_list_path = category_dir / "reading_list.md"
            
            # Lire le contenu existant ou créer nouveau
            if reading_list_path.exists():
                with open(reading_list_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = f"""# Reading List - {category.split('-')[1].title()}

## Status Legend
- 🔴 **Not Started** - Paper not yet read
- 🟡 **In Progress** - Currently reading/taking notes  
- 🟢 **Completed** - Read and summarized

---

## 📊 Progress Overview

**Last Updated:** {datetime.now().strftime("%Y-%m-%d")}

---

## 📚 Papers

"""
            
            # Ajouter les nouveaux papers
            new_entries = []
            for paper in papers:
                authors_short = paper.authors[0] if paper.authors else "Unknown"
                if len(paper.authors) > 1:
                    authors_short += " et al."
                
                entry = f"""| 🔴 | ⭐ | {paper.title} | ArXiv | {paper.published.year} | [{paper.arxiv_id}]({paper.summary_url}) |"""
                
                # Vérifier si déjà présent
                if paper.arxiv_id not in content:
                    new_entries.append(entry)
            
            if new_entries:
                # Ajouter les nouvelles entrées
                if "| Status | Priority | Paper | Venue | Year | Link |" not in content:
                    content += "\n| Status | Priority | Paper | Venue | Year | Link |\n"
                    content += "|--------|----------|-------|-------|------|------|\n"
                
                content += "\n".join(new_entries) + "\n"
                
                # Mettre à jour la date
                content = re.sub(r'(\*\*Last Updated:\*\*\s*)\d{4}-\d{2}-\d{2}', 
                               fr'\g<1>{datetime.now().strftime("%Y-%m-%d")}', content)
                
                # Sauvegarder
                with open(reading_list_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"📚 Reading list mise à jour: {category} ({len(new_entries)} nouveaux papers)")
    
    def update_master_reading_list(self, total_new_papers: int):
        """Met à jour la liste de lecture principale"""
        
        master_list_path = self.papers_dir / "reading_list.md"
        
        if not master_list_path.exists():
            return
        
        with open(master_list_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Mettre à jour les statistiques
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Compter les papers totaux
        total_papers = len(self.scraped_papers)
        
        patterns = [
            (r'(\*\*Total Papers:\*\*\s*)\d+', fr'\g<1>{total_papers}'),
            (r'(\*\*Last Updated:\*\*\s*)\d{4}-\d{2}-\d{2}', fr'\g<1>{today}'),
            (r'(- \*\*Papers in Queue:\*\*\s*)\d+', fr'\g<1>{total_papers}'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        # Ajouter section des nouveaux papers
        if total_new_papers > 0:
            new_section = f"""
## 🆕 Nouveaux Papers ({today})

**{total_new_papers} nouveaux papers ajoutés automatiquement depuis arXiv**

Voir les catégories spécifiques pour les détails.

---
"""
            # Insérer avant la fin
            content = content.rstrip() + new_section
        
        with open(master_list_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📋 Master reading list mise à jour (+{total_new_papers} papers)")
    
    def run_scraping(self, categories: List[str] = None, max_results: int = 20, days_back: int = 7, download_pdfs: bool = True):
        """Exécute le scraping complet"""
        
        print(f"🚀 Début du scraping arXiv - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 70)
        
        if not categories:
            categories = list(self.search_queries.keys())
        
        all_papers = []
        papers_by_category = {}
        
        # Scraper par catégorie
        for category in categories:
            print(f"\n📂 Catégorie: {category}")
            print("-" * 40)
            
            category_papers = []
            
            # Rechercher avec chaque requête de la catégorie
            for query in self.search_queries[category]:
                papers = self.search_papers(query, max_results//len(self.search_queries[category]), days_back)
                category_papers.extend(papers)
                time.sleep(2)  # Délai entre requêtes
            
            # Dédupliquer
            seen_ids = set()
            unique_papers = []
            for paper in category_papers:
                if paper.arxiv_id not in seen_ids:
                    unique_papers.append(paper)
                    seen_ids.add(paper.arxiv_id)
            
            print(f"📊 {len(unique_papers)} papers uniques trouvés pour {category}")
            
            papers_by_category[self.category_mapping[category]] = unique_papers
            all_papers.extend(unique_papers)
        
        print(f"\n📈 Total: {len(all_papers)} nouveaux papers trouvés")
        
        if not all_papers:
            print("ℹ️  Aucun nouveau paper à traiter")
            return
        
        # Organiser les papers
        print("\n🗂️  Organisation des papers...")
        organized_count = 0
        
        for category_folder, papers in papers_by_category.items():
            if not papers:
                continue
                
            category_dir = self.papers_dir / category_folder
            category_dir.mkdir(parents=True, exist_ok=True)
            
            for paper in papers:
                # Re-catégoriser avec analyse du contenu
                best_category = self.categorize_paper(paper)
                if best_category != category_folder:
                    # Déplacer vers la meilleure catégorie
                    if best_category not in papers_by_category:
                        papers_by_category[best_category] = []
                    papers_by_category[best_category].append(paper)
                    continue
                
                # Créer la note
                note_path = self.create_paper_note(paper, category_dir)
                
                # Télécharger PDF si demandé
                if download_pdfs:
                    pdf_path = self.download_pdf(paper, category_dir)
                
                organized_count += 1
        
        print(f"✅ {organized_count} papers organisés")
        
        # Mettre à jour les listes de lecture
        print("\n📚 Mise à jour des listes de lecture...")
        self.update_reading_list(papers_by_category)
        self.update_master_reading_list(len(all_papers))
        
        # Sauvegarder la liste des papers scrapés
        self.save_scraped_papers()
        
        print(f"\n🎉 Scraping terminé! {len(all_papers)} nouveaux papers ajoutés")
        
        return all_papers

def main():
    """Fonction principale avec gestion des arguments"""
    
    parser = argparse.ArgumentParser(description='Scraper arXiv pour recherche PhD LLM compression')
    parser.add_argument('--categories', '-c', nargs='+', 
                       choices=['quantization', 'pruning', 'distillation', 'kv-cache', 'systems', 'general'],
                       help='Catégories à scraper')
    parser.add_argument('--max-results', '-m', type=int, default=30,
                       help='Nombre maximum de résultats par requête (défaut: 30)')
    parser.add_argument('--days-back', '-d', type=int, default=7,
                       help='Nombre de jours en arrière pour la recherche (défaut: 7)')
    parser.add_argument('--no-pdfs', action='store_true',
                       help='Ne pas télécharger les PDFs')
    parser.add_argument('--repo-path', '-p', type=str,
                       help='Chemin vers le repository (défaut: dossier courant)')
    
    args = parser.parse_args()
    
    # Chemin du repository
    if args.repo_path:
        repo_path = Path(args.repo_path)
    else:
        repo_path = Path.cwd()
    
    # Vérifier que c'est un repository valid
    if not (repo_path / ".git").exists():
        print("❌ Pas de repository Git trouvé")
        print("💡 Assurez-vous d'être dans votre dossier de repository PhD")
        return
    
    try:
        # Installer arxiv si nécessaire
        try:
            import arxiv
        except ImportError:
            print("📦 Installation du package arxiv...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "arxiv"])
            import arxiv
        
        # Créer et exécuter le scraper
        scraper = ArXivScraper(repo_path)
        papers = scraper.run_scraping(
            categories=args.categories,
            max_results=args.max_results,
            days_back=args.days_back,
            download_pdfs=not args.no_pdfs
        )
        
        if papers:
            print(f"\n📋 Prochaines étapes recommandées:")
            print("1. Réviser les papers ajoutés dans chaque catégorie")
            print("2. Prioriser les papers les plus pertinents")
            print("3. Commencer par lire les papers dans 'papers/07-surveys-background/'")
            print("4. Mettre à jour votre repository:")
            print("   python3 auto_update.py 'Added papers from arXiv scraping'")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    main()