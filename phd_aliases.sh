# Aliases pour le repository PhD - Ajoutez à votre ~/.bashrc

# Navigation rapide vers le repository
alias phd='cd "/home/ayoub/Bureau/um6p/github/PhD Research Compression of Large Language Models (LLMs)"'

# Mises à jour rapides
alias phd-update='cd "/home/ayoub/Bureau/um6p/github/PhD Research Compression of Large Language Models (LLMs)" && python3 auto_update.py'
alias phd-quick='cd "/home/ayoub/Bureau/um6p/github/PhD Research Compression of Large Language Models (LLMs)" && python3 quick_update.py'
alias phd-push='cd "/home/ayoub/Bureau/um6p/github/PhD Research Compression of Large Language Models (LLMs)" && git add . && git commit -m "Manual update - $(date +%Y-%m-%d)" && git push'

# Statut et navigation
alias phd-status='cd "/home/ayoub/Bureau/um6p/github/PhD Research Compression of Large Language Models (LLMs)" && git status'
alias phd-log='cd "/home/ayoub/Bureau/um6p/github/PhD Research Compression of Large Language Models (LLMs)" && git log --oneline -10'
alias phd-papers='cd "/home/ayoub/Bureau/um6p/github/PhD Research Compression of Large Language Models (LLMs)/papers"'
alias phd-research='cd "/home/ayoub/Bureau/um6p/github/PhD Research Compression of Large Language Models (LLMs)/research"'

# Ouvrir dans l'éditeur
alias phd-code='cd "/home/ayoub/Bureau/um6p/github/PhD Research Compression of Large Language Models (LLMs)" && code .'
alias phd-vim='cd "/home/ayoub/Bureau/um6p/github/PhD Research Compression of Large Language Models (LLMs)" && vim README.md'

# Pour charger ces aliases:
# echo "source /home/ayoub/Bureau/um6p/github/PhD Research Compression of Large Language Models (LLMs)/phd_aliases.sh" >> ~/.bashrc
# source ~/.bashrc
