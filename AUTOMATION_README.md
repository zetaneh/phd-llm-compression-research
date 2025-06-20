# 🤖 Outils d'Automatisation PhD

Outils pour automatiser la gestion de votre repository de recherche PhD.

## 📁 Scripts Disponibles

### 1. `auto_update.py` - Mise à jour complète
```bash
# Mise à jour complète avec dates
python3 auto_update.py

# Avec message personnalisé
python3 auto_update.py "Ajout des notes sur quantization papers"

# Forcer même sans changements
python3 auto_update.py --force
```

### 2. `quick_update.py` - Mise à jour rapide
```bash
# Mise à jour quotidienne rapide
python3 quick_update.py

# Avec message
python3 quick_update.py "Lecture avancée sur pruning"
```

### 3. `Makefile` - Commandes simplifiées
```bash
# Mise à jour complète
make update

# Mise à jour rapide
make quick

# Statut du repository
make status

# Aide
make help
```

## ⚡ Workflow Quotidien Recommandé

### Chaque matin:
```bash
cd "/home/ayoub/Bureau/um6p/github/PhD Research Compression of Large Language Models (LLMs)"
make quick
```

### Après avoir travaillé:
```bash
make update
# ou
python3 auto_update.py "Description de votre travail"
```

### Chaque vendredi:
```bash
make status  # Vérifier ce qui a été fait
make update  # Mise à jour complète
```

## 🔧 Installation des Aliases

Pour faciliter l'utilisation, ajoutez les aliases à votre shell:

```bash
# Ajouter les aliases
echo "source /home/ayoub/Bureau/um6p/github/PhD Research Compression of Large Language Models (LLMs)/phd_aliases.sh" >> ~/.bashrc
source ~/.bashrc

# Utilisation des aliases
phd-quick       # Mise à jour rapide
phd-update      # Mise à jour complète  
phd-status      # Statut Git
phd             # Aller au repository
phd-code        # Ouvrir dans VS Code
```

## 📅 Automatisation avec Cron (Optionnel)

Pour automatiser complètement, vous pouvez configurer cron:

```bash
# Éditer crontab
crontab -e

# Ajouter une ligne pour mise à jour quotidienne à 18h
0 18 * * * cd /home/ayoub/Bureau/um6p/github/PhD Research Compression of Large Language Models (LLMs) && python3 quick_update.py "Auto-update $(date)"

# Ou mise à jour hebdomadaire le vendredi à 17h
0 17 * * 5 cd /home/ayoub/Bureau/um6p/github/PhD Research Compression of Large Language Models (LLMs) && python3 auto_update.py "Weekly auto-update"
```

## 🎯 Fonctionnalités

### Ce que les scripts font automatiquement:
- ✅ Mettent à jour toutes les dates dans les fichiers
- ✅ Créent des commits avec messages appropriés
- ✅ Push automatique vers GitHub
- ✅ Gèrent les erreurs Git
- ✅ Affichent des messages informatifs

### Ce que vous devez faire manuellement:
- 📝 Ajouter vos notes de lecture
- 🔬 Documenter vos expériences
- 📊 Mettre à jour vos statistiques de progrès
- 🎯 Réviser vos objectifs de recherche

## 🚨 Dépannage

### Erreur "Repository not found"
```bash
git remote -v  # Vérifier les remotes
git remote set-url origin https://github.com/votre-username/repo-name.git
```

### Erreur de permissions
```bash
chmod +x *.py  # Rendre les scripts exécutables
```

### Conflits Git
```bash
git status     # Voir les conflits
git pull       # Récupérer les changements distants
# Résoudre manuellement puis:
git add .
git commit -m "Résolution conflits"
git push
```

---

*Outils créés le 2025-06-20 pour optimiser votre workflow de recherche PhD*
