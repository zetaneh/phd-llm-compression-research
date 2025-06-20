# Commandes Git Utiles

## Configuration initiale
```bash
git config --global user.name "Ayoub Abraich"
git config --global user.email "your-email@um6p.ma"
```

## Workflow quotidien
```bash
# Voir le statut
git status

# Ajouter les changements
git add .

# Commit avec message
git commit -m "Add notes on quantization paper X"

# Push vers GitHub
git push
```

## Créer des branches pour des expériences
```bash
# Créer une nouvelle branche
git checkout -b experiment/new-compression-method

# Revenir à la branche principale
git checkout main

# Merger une branche
git merge experiment/new-compression-method
```

## Sauvegarde
```bash
# Créer un backup tag
git tag -a backup-$(date +%Y%m%d) -m "Backup $(date)"
git push --tags
```
