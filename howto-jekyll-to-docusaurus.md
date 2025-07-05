# Jekyll to Docusaurus
## 1. Front Matter (En-tête YAML)
### Jekyll

```yaml
---
layout: post
title: "Mon article"
date: 2025-01-01
categories: [blog, tech]
tags: [markdown, jekyll]
permalink: /mon-article/
author: "Rolland"
---
```

### Docusaurus

```yaml
---
title: Mon article
sidebar_position: 1
id: mon-article
slug: /mon-article
tags: [markdown, docusaurus]
authors: rolland
date: 2025-01-01
---
```

## 2. Liens et références
### Jekyll

```markdown
<!-- Liens internes avec site.baseurl -->
[Page]({{ site.baseurl }}/page)
[Article]({% link _posts/2025-01-01-article.md %})

<!-- Images -->
![Image]({{ site.baseurl }}/assets/img/photo.jpg)

<!-- Variables de site -->
{{ site.title }}
{{ site.description }}
```

### Docusaurus

```md
<!-- Liens internes relatifs -->
[Page](./page)
[Article](/blog/article)

<!-- Images -->
![Image](/img/photo.jpg)
import photo from '@site/static/img/photo.jpg';

<!-- Variables de config -->
Pas d'équivalent direct, utiliser des composants React
```

## 3. Attributs de liens et éléments
### Jekyll (Kramdown)

```md
[Lien externe](https://example.com){:target="_blank"}
[Lien avec classe](page.html){: .button .primary}
{: .highlight }
Texte mis en valeur

## Titre {#custom-id}
```

### Docusaurus

```md
<!-- markdown : enlever {:target="_blank"}, le lien sou'crira automatiquement dans u nouvel onglet -->
[Lien externe](https://example.com)

<!-- HTML standard -->
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Lien externe</a>

<!-- Classes CSS via HTML -->
<div className="highlight">Texte mis en valeur</div>

## Titre {#custom-id}  <!-- Fonctionne pareil -->
```

## 4. Admonitions/Alertes
### Jekyll

```md
> **Note:** Ceci est une note
{: .note}

> **Attention:** Ceci est un avertissement  
{: .warning}

<div class="alert alert-info">
  <strong>Info:</strong> Message d'information
</div>
```

### Docusaurus

```md
:::note
Ceci est une note
:::

:::warning
Ceci est un avertissement
:::

:::tip[Conseil personnalisé]
Message avec titre personnalisé
:::

:::danger
Message important
:::
```

## 5. Code et syntaxe highlighting
### Jekyll

```md
{% highlight python linenos %}
def hello():
    print("Hello World")
{% endhighlight %}

```python
# Code avec langue
print("Hello")
```

### Docusaurus

```md
````markdown
```python title="hello.py" showLineNumbers
def hello():
    print("Hello World")
```

```js
def hello():
    name = "World"
    print(f"Hello {name}")
```

## 6. Inclusion de fichiers

### Jekyll
```markdown
{% include file.html %}
{% include_relative ../snippets/code.md %}

<!-- Variables -->
{% assign variable = "valeur" %}
{{ variable }}
```

### Docusaurus
```markdown
<!-- Import de composants React -->
import MyComponent from '@site/src/components/MyComponent';
import CodeBlock from '@theme/CodeBlock';

<MyComponent />

<!-- Pas de variables Liquid, utiliser React/MDX -->
```

## 7. Boucles et logique

### Jekyll (Liquid)
```markdown
{% for post in site.posts %}
  - [{{ post.title }}]({{ post.url }})
{% endfor %}

{% if page.author %}
  Auteur: {{ page.author }}
{% endif %}

{% unless page.hidden %}
  Contenu visible
{% endunless %}
```

### Docusaurus
```jsx
<!-- Utiliser des composants React -->
import BlogPostsList from '@site/src/components/BlogPostsList';

<BlogPostsList />

<!-- Ou JavaScript dans MDX -->
export const posts = ['Post 1', 'Post 2'];

{posts.map(post => <li key={post}>{post}</li>)}
```

## 8. Collections et données

### Jekyll
```markdown
<!-- _data/navigation.yml -->
{% for item in site.data.navigation %}
  - [{{ item.title }}]({{ item.url }})
{% endfor %}

<!-- Posts -->
{% for post in site.posts limit:5 %}
  {{ post.title }}
{% endfor %}
```

### Docusaurus
```jsx
<!-- Utiliser des fichiers JSON + composants React -->
import navigation from '@site/data/navigation.json';

{navigation.map(item => (
  <a href={item.url}>{item.title}</a>
))}
```

## 9. Pagination

### Jekyll
```markdown
<!-- Pagination automatique -->
{{ paginator.previous_page_path }}
{{ paginator.next_page_path }}
{{ paginator.total_pages }}

{% for post in paginator.posts %}
  {{ post.title }}
{% endfor %}
```

### Docusaurus
```markdown
<!-- Pagination automatique dans les blogs -->
<!-- Navigation précédent/suivant automatique dans les docs -->
<!-- Pas de Liquid, mais composants React personnalisés si besoin -->
```

## 10. Filtres et fonctions

### Jekyll (Liquid)
```markdown
{{ "hello world" | capitalize }}
{{ site.time | date: "%Y-%m-%d" }}
{{ post.content | strip_html | truncatewords: 50 }}
{{ page.url | relative_url }}
{{ "/path" | absolute_url }}
```

### Docusaurus
```jsx
<!-- Utiliser JavaScript standard -->
{"hello world".charAt(0).toUpperCase() + "hello world".slice(1)}
{new Date().toISOString().split('T')[0]}

<!-- Ou créer des composants React pour les fonctions complexes -->
```

## 11. Métadonnées et SEO

### Jekyll
```yaml
---
title: "Mon article"
description: "Description de l'article"
image: /assets/img/featured.jpg
keywords: [mot1, mot2]
---
```

### Docusaurus
```yaml
---
title: Mon article
description: Description de l'article
image: /img/featured.jpg
keywords: [mot1, mot2]
---

<!-- Ou utiliser le composant Head -->
import Head from '@docusaurus/Head';

<Head>
  <meta property="og:title" content="Mon titre" />
  <meta property="og:description" content="Ma description" />
</Head>
```

## 12. Configuration des URLs

### Jekyll (_config.yml)
```yaml
permalink: /:categories/:year/:month/:day/:title:output_ext
baseurl: "/mon-site"
url: "https://exemple.com"
```

### Docusaurus (docusaurus.config.js)
```javascript
module.exports = {
  url: 'https://exemple.com',
  baseUrl: '/mon-site/',
  // Les permalinks sont définis dans le front matter ou automatiques
};
```

## 13. Tableaux de contenu

### Jekyll
```markdown
<!-- Plugin nécessaire ou manuel -->
* TOC
{:toc}
```

### Docusaurus
```yaml
---
hide_table_of_contents: false  # true pour cacher
toc_min_heading_level: 2
toc_max_heading_level: 4
---
<!-- TOC automatique dans la sidebar -->
```

## 14. Layouts et templates

### Jekyll
```yaml
---
layout: post
---
<!-- Le contenu utilise _layouts/post.html -->
```

### Docusaurus
```yaml
---
# Layouts automatiques selon le type (blog, docs, page)
# Personnalisation via swizzling des composants
---
```

## 15. Assets et ressources

### Jekyll
```markdown
<!-- CSS/JS dans _includes/head.html -->
<link rel="stylesheet" href="{{ '/assets/css/style.css' | relative_url }}">

<!-- Images -->
![Image]({{ site.baseurl }}/assets/images/photo.jpg)
```

### Docusaurus
```jsx
<!-- CSS dans src/css/custom.css ou composants -->
import './styles.module.css';

<!-- Images -->
![Image](/img/photo.jpg)
import useBaseUrl from '@docusaurus/useBaseUrl';
<img src={useBaseUrl('/img/photo.jpg')} />
```

## Migration : Checklist rapide

1. **Front matter** : Adapter les champs YAML
2. **Liens** : Supprimer `{{ site.baseurl }}` et `{% link %}`
3. **Attributs** : Remplacer `{:target="_blank"}` par HTML
4. **Admonitions** : Convertir vers la syntaxe `:::`
5. **Code** : Adapter les options de highlighting
6. **Liquid** : Remplacer par des composants React/MDX
7. **Variables** : Migrer vers des composants ou configuration
8. **Collections** : Utiliser la structure docs/blog de Docusaurus

Cette migration nécessitera une adaptation significative mais le résultat sera plus moderne et performant