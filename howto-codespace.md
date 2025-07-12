# Howto GitHub Codespaces pour sites Docusaurus

### Commandes fréquentes
```bash
# Combo rapide
npm run start

# Sauvegarde rapide
git add .

# Deploy complet
npm run build 
&& GIT_USER=rollandauda npm run deploy

 && git commit -m "Update" && git push
```

## Configuration initiale

### Avantages avec GitHub Education
- **180 heures gratuites par mois** (au lieu de 60h)
- **20 GB de stockage gratuit**
- Accès aux instances plus puissantes

### Auto-configuration recommandée
Créer `.devcontainer/devcontainer.json` dans votre repo :

```json
{
  "name": "Docusaurus",
  "image": "mcr.microsoft.com/devcontainers/javascript-node:18",
  "postCreateCommand": "npm install",
  "forwardPorts": [3000],
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-vscode.vscode-typescript-next"
      ]
    }
  }
}
```

## Workflow complet dans Codespaces

### 1. Ouvrir le Codespace
```bash
# Depuis GitHub : Code > Codespaces > Create codespace
# Auto-installe avec postCreateCommand si configuré
# Sinon, faire manuellement :
npm install
```

### 2. Démarrer la prévisualisation
```bash
npm run start
# Port 3000 automatiquement exposé
# Popup pour ouvrir la prévisualisation
```

### 3. Modifier vos fichiers

### 4. Sauvegarder sur GitHub
```bash
# Voir les modifications
git status

# Ajouter tous les fichiers modifiés
git add .

# Commit avec message descriptif
git commit -m "Update"

# Pousser vers GitHub (authentification automatique)
git push
```

### 5. Déployer le site (optionnel)
```bash
# Vérification avant déploiement (recommandé)
npm run build

# Déploiement sur GitHub Pages
GIT_USER=rollandauda npm run deploy
```

## Workflows selon le type de modification

### Modifications importantes (nouveau contenu, restructuration)
```bash
# 1. Prévisualisation
npm run start

# 2. Modifications...

# 3. Vérification
npm run build

# 4. Sauvegarde
git add .
git commit -m "Ajout nouvelle leçon"
git push

# 5. Déploiement
GIT_USER=rollandauda npm run deploy
```

### Corrections rapides (typos, petites modifications)
```bash
# 1. Modifications directes

# 2. Sauvegarde
git add .
git commit -m "Correction typos"
git push

# 3. Déploiement direct
GIT_USER=rollandauda npm run deploy
```

### Workflow ultra-rapide
```bash
# Modifications + déploiement direct
git add .
git commit -m "Mise à jour"
git push
GIT_USER=rollandauda npm run deploy
```

## Commandes de mise à jour

### Mise à jour Docusaurus
```bash
npm install @docusaurus/core@latest @docusaurus/preset-classic@latest
```

### Installation complète des dépendances
```bash
npm install
```

## Conseils d'optimisation

### Économiser les heures Codespaces
- **Auto-stop** : 30 minutes d'inactivité
- **GitHub.dev** pour modifications ultra-rapides (gratuit illimité)
- **Codespaces** pour développement avec prévisualisation

### Gestion des erreurs courantes
```bash
# Liens brisés
npm run build  # Affiche les erreurs détaillées

# Problèmes de dépendances
npm install --force

# Reset complet
rm -rf node_modules package-lock.json
npm install
```

## Sites concernés
- **cav25** : Spécialité CAV
- **dgemc25** : DGEMC
- **phil25** : Philosophie  
- **hlp25** : HLP

## Estimation d'usage
- **2h/jour × 30 jours = 60h/mois**
- **Limite : 180h/mois avec GitHub Education**
- **Marge confortable : 3× l'usage estimé**

## Raccourcis utiles

### Accès rapide
- **GitHub.dev** : Appuyer sur `.` dans le repo
- **Codespace** : Code > Codespaces > Create

