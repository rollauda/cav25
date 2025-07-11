# Guide d'utilisation du script Jekyll vers Docusaurus

Ce guide explique comment utiliser le script `jekyll-to-docusaurus-simple.py` pour convertir un fichier Markdown Jekyll au format Docusaurus.

## Vue d'ensemble

Le script `jekyll-to-docusaurus-simple.py` convertit un fichier Markdown Jekyll vers le format Docusaurus avec une interface interactive simple. Il gère :

- **Front matter** : Conversion des métadonnées Jekyll vers Docusaurus
- **Liens internes** : Adaptation des liens `{% link %}` et chemins relatifs
- **Images et assets** : Nettoyage des références vers `/static/`
- **Admonitions** : Conversion des alertes Jekyll vers les admonitions Docusaurus
- **Code blocks** : Transformation des `{% highlight %}` vers la syntaxe Markdown
- **Tags Liquid** : Suppression/conversion des tags non compatibles
- **Nettoyage** : Suppression des attributs Kramdown et balises spécifiques Jekyll

## Installation et prérequis

### Dépendances Python

```bash
pip install pyyaml
```

### Fichiers nécessaires

```
votre-dossier/
├── fichier-jekyll.md              # Votre fichier Jekyll source
├── jekyll-to-docusaurus-simple.py # Le script de conversion
└── fichier-docusaurus.md          # Fichier converti (sera créé)
```

## Utilisation

### Interface interactive (recommandée)

Lancez simplement le script :

```bash
python jekyll-to-docusaurus-simple.py
```

Le script vous demandera :

1. **Fichier d'entrée** : Le chemin vers votre fichier Jekyll (.md)
2. **Fichier de sortie** : Le chemin de destination (optionnel, un nom par défaut sera proposé)

**Exemple d'utilisation :**
```
🔄 Convertisseur Jekyll vers Docusaurus
========================================
📁 Chemin du fichier Jekyll (.md) : ./mon-article-jekyll.md
💡 Fichier de sortie suggéré: ./mon-article-jekyll-docusaurus.md
📝 Chemin du fichier de sortie (Entrée pour défaut) : ./mon-article-docusaurus.md
```

### Résultat de la conversion

Le script affiche en temps réel les modifications appliquées :

```
🚀 Début de la conversion...
----------------------------------------
📖 Lecture de: ./mon-article-jekyll.md
✓ Front matter converti
✓ Variables site.baseurl supprimées
✓ Admonitions converties
✓ Tags Liquid supprimés
💾 Fichier sauvegardé: ./mon-article-docusaurus.md
----------------------------------------
✅ Conversion réussie!

📋 Modifications appliquées:
   • Front matter converti
   • Variables site.baseurl supprimées
   • Admonitions converties
   • Tags Liquid supprimés
```

## Exemples de conversion

### Fichier Jekyll d'entrée

```markdown
---
layout: post
title: "Mon Guide Jekyll"
date: 2023-01-01
categories: [tutoriel, web]
tags: [jekyll, markdown]
author: John Doe
permalink: /guides/mon-guide/
---

# {{ page.title }}

Voici mon guide pour Jekyll !

> **Note:** Ceci est important
{: .note}

[Voir autre article]({% link _posts/2023-01-02-autre.md %})

![Image]({{ site.baseurl }}/assets/images/demo.jpg)

{% highlight python linenos %}
def hello():
    print("Hello Jekyll")
{% endhighlight %}

{% for post in site.posts limit:3 %}
  - {{ post.title }}
{% endfor %}
```

### Fichier Docusaurus de sortie

```markdown
---
title: Mon Guide Jekyll
date: 2023-01-01
authors: John Doe
tags: [tutoriel, web, jekyll, markdown]
slug: guides/mon-guide
---

# Mon Guide Jekyll

Voici mon guide pour Jekyll !

:::note
Ceci est important
:::

[Voir autre article](/blog/autre)

![Image](/images/demo.jpg)

```python showLineNumbers
def hello():
    print("Hello Jekyll")
```

<!-- Boucle Liquid supprimée - convertir en composant React -->
```

## Conversions détaillées

### 1. Front Matter

**Jekyll :**
```yaml
---
layout: post
title: "Mon Article"
date: 2023-01-01
categories: [blog, tech]
tags: [javascript, react]
author: John Doe
permalink: /articles/mon-article/
---
```

**Docusaurus :**
```yaml
---
title: Mon Article
date: 2023-01-01
authors: John Doe
tags: [blog, tech, javascript, react]
slug: articles/mon-article
---
```

### 2. Liens internes

**Jekyll :**
```markdown
[Voir l'article]({% link _posts/2023-01-01-guide.md %})
[Page de contact]({{ site.baseurl }}/contact/)
```

**Docusaurus :**
```markdown
[Voir l'article](/blog/guide)
[Page de contact](/contact/)
```

### 3. Images et assets

**Jekyll :**
```markdown
![Image]({{ site.baseurl }}/assets/images/photo.jpg)
![Logo](/assets/logo.png)
```

**Docusaurus :**
```markdown
![Image](/images/photo.jpg)
![Logo](/logo.png)
```

### 4. Admonitions

**Jekyll :**
```markdown
> **Note:** Ceci est important
{: .note}

<div class="alert alert-warning">
  <strong>Attention:</strong> Soyez prudent
</div>
```

**Docusaurus :**
```markdown
:::note
Ceci est important
:::

:::warning Attention
Soyez prudent
:::
```

### 5. Blocs de code

**Jekyll :**
```liquid
{% highlight python linenos %}
def hello():
    print("Hello World")
{% endhighlight %}
```

**Docusaurus :**
````markdown
```python showLineNumbers
def hello():
    print("Hello World")
```
````

### 6. Tags Liquid supprimés

**Éléments automatiquement supprimés :**
- `{% assign variable = value %}`
- `{% include fichier.html %}`
- `{{ site.variable }}`
- Boucles `{% for %}`
- Conditions `{% if %}`

**Remplacés par des commentaires :**
```markdown
<!-- Boucle Liquid supprimée - convertir en composant React -->
<!-- Condition Liquid supprimée - convertir en composant React -->
```

## Actions post-conversion

### 1. Vérification du fichier

Après conversion, vérifiez le fichier généré :

- [ ] **Front matter** : Métadonnées correctes
- [ ] **Liens** : Chemins relatifs valides  
- [ ] **Images** : Références vers `/static/`
- [ ] **Admonitions** : Format `:::type` correct
- [ ] **Code** : Coloration syntaxique préservée

### 2. Intégration dans Docusaurus

1. **Copiez le fichier** dans votre projet Docusaurus :
   - Articles de blog → `blog/`
   - Documentation → `docs/`
   - Pages → `src/pages/`

2. **Testez le rendu** :
```bash
cd votre-projet-docusaurus
npm start
```

3. **Ajustez si nécessaire** :
   - Vérifiez les liens internes
   - Adaptez les chemins d'images
   - Testez les admonitions

### 3. Remplacement des composants Liquid

Les éléments suivants nécessitent une conversion manuelle :

**Boucles et logique Liquid :**

```markdown
<!-- Remplacer ce commentaire par un composant React -->
<!-- Boucle Liquid supprimée - convertir en composant React -->
```

**Exemple de composant React :**
```jsx
// src/components/RecentPosts.js
import React from 'react';

export default function RecentPosts({limit = 5}) {
  // Logique pour récupérer les articles récents
  return (
    <div>
      {/* Affichage des articles */}
    </div>
  );
}
```

**Puis dans votre fichier Markdown :**
```markdown
import RecentPosts from '@site/src/components/RecentPosts';

<RecentPosts limit={3} />
```

## Configuration pour projets multiples

Si vous convertissez plusieurs fichiers pour différents sites Docusaurus :

### Batch de conversion

Créez un script pour convertir plusieurs fichiers :

```bash
#!/bin/bash
# convert-multiple.sh

FILES=(
    "article1.md"
    "article2.md" 
    "guide.md"
)

for file in "${FILES[@]}"; do
    echo "Conversion de $file..."
    python jekyll-to-docusaurus-simple.py "$file" "docusaurus-$file"
done
```

### Recommandations par type de site

**Pour phil25, dgemc25, hlp25, cav25 :**

- **Articles de blog** → Répertoire `blog/`
- **Documentation** → Répertoire `docs/`
- **Pages d'accueil** → Répertoire `src/pages/`

## Limitations et cas particuliers

### Éléments nécessitant une attention manuelle

1. **Composants complexes Jekyll** : Plugins spécifiques, shortcodes personnalisés
2. **Variables de site dynamiques** : `{{ site.data }}`, configurations complexes
3. **Layouts personnalisés** : Adaptation vers les layouts Docusaurus
4. **Includes avec logique** : Conversion en composants React
5. **Collections Jekyll** : Restructuration selon Docusaurus

### Limitations du script

- **Liquid complexe** : Seuls les patterns courants sont gérés
- **CSS/JS embedé** : Les styles inline ne sont pas convertis
- **Plugins Jekyll** : Fonctionnalités spécifiques non portées
- **Data files** : Les fichiers `_data/` doivent être convertis manuellement

## Optimisations et personnalisations

### Adaptation du script

Vous pouvez modifier le script pour vos besoins spécifiques :

```python
# Ajouter une conversion personnalisée
def convert_custom_syntax(self, content):
    """Convertit votre syntaxe personnalisée"""
    # Exemple : convertir un shortcode spécifique
    content = re.sub(r'\[mon_shortcode\]', ':::tip\nContenu spécial\n:::', content)
    return content

# L'ajouter dans convert_file()
content = self.convert_custom_syntax(content)
```

### Performance et sécurité

- **Sauvegarde** : Toujours garder une copie du fichier original
- **Test** : Vérifier le rendu avant de remplacer les fichiers source
- **Validation** : Contrôler la syntaxe Markdown/YAML après conversion

## Dépannage

### Erreurs courantes

**1. Erreur YAML dans le front matter**
```
❌ Erreur front matter: scanner.ScannerError
```
*Solution :* Vérifier la syntaxe YAML, échapper les caractères spéciaux (`:`, `"`, etc.)

**2. Fichier non trouvé**
```
❌ Erreur: Le fichier ./mon-fichier.md n'existe pas
```
*Solution :* Vérifier le chemin, utiliser un chemin absolu si nécessaire

**3. Encodage de caractères**
```
UnicodeDecodeError
```
*Solution :* Vérifier l'encodage du fichier source (doit être UTF-8)

### Questions fréquentes

**Q: Le script peut-il traiter des fichiers avec du HTML complexe ?**
R: Partiellement. Les balises HTML simples sont préservées, mais les structures complexes peuvent nécessiter un ajustement manuel.

**Q: Comment gérer les images avec des chemins absolus ?**
R: Le script convertit automatiquement les références `assets/` vers `/`. Pour des chemins spécifiques, adaptez la fonction `convert_images()`.

**Q: Peut-on convertir des fichiers autres que .md ?**
R: Non, le script est conçu pour les fichiers Markdown (.md) uniquement.

## Workflow recommandé

### Pour un fichier unique

1. **Test** : Convertir d'abord une copie de test
2. **Vérification** : Contrôler le résultat manuellement
3. **Integration** : Copier dans le projet Docusaurus
4. **Validation** : Tester le rendu avec `npm start`

### Pour plusieurs fichiers

1. **Batch** : Utiliser un script de traitement par lot
2. **Comparaison** : Vérifier les différences avec `diff`
3. **Validation** : Tester l'ensemble du site
4. **Déploiement** : Publier après validation complète

---

**Ce guide couvre l'utilisation complète du script simplifié jekyll-to-docusaurus-simple.py. Pour des besoins spécifiques, le script peut être adapté selon vos requirements.**
