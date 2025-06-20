# Makefile pour automatisation du repository PhD
# Usage: make update, make quick, make help

.PHONY: help update quick push clean status

help:
	@echo "📚 Commandes disponibles pour le repository PhD:"
	@echo "  make update     - Mise à jour complète avec dates"
	@echo "  make quick      - Mise à jour rapide quotidienne"  
	@echo "  make push [msg] - Push avec message personnalisé"
	@echo "  make status     - Afficher le statut Git"
	@echo "  make clean      - Nettoyer les fichiers temporaires"

update:
	@echo "🚀 Mise à jour complète..."
	python3 auto_update.py

quick:
	@echo "⚡ Mise à jour rapide..."
	python3 quick_update.py

push:
	@echo "📤 Push avec message personnalisé..."
	@read -p "Message de commit: " msg; \
	git add . && git commit -m "$$msg" && git push

status:
	@echo "📊 Statut du repository:"
	@git status --short
	@echo "📈 Derniers commits:"
	@git log --oneline -5

clean:
	@echo "🧹 Nettoyage..."
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -delete
	@find . -name "*.tmp" -delete
	@echo "✅ Nettoyage terminé"

# Raccourcis
u: update
q: quick
s: status
