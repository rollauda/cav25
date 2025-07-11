---
sidebar_position: 20
---
## Admonitions
En plus de la syntaxe Markdown de base, nous avons une syntaxe spéciale d’admonestations en enveloppant le texte avec un ensemble de 3 deux-points, suivi d’une étiquette indiquant son type.


:::note 
= gris
:::

:::tip 
= vert
:::

:::info 
= bleu
:::

:::warning 
= jaune
:::

:::danger 
= rose
:::

## images

### Intégration

![Texte alternatif](/img/philo/arrival.png)


### Limiter la taille

<img
  src={require('/img/philo/bladerunner.png').default}
  alt="Example banner"
  width="50%"
/>

### Intégration avec clic ouverture autre onglet

<a href="/phil25/img/philo/arrival.png" target="_blank" rel="noopener noreferrer">
  <img src={require('/img/philo/arrival.png').default} alt="Description" />
</a>

### avec clic et limiter la taille

<a href="/phil25/img/philo/bladerunner.png" target="_blank" rel="noopener noreferrer">
  <img src={require('/img/philo/bladerunner.png').default} alt="Description" width="50%" />
</a>

## embed pdf 

Mettre au début du fichier :

```
import useBaseUrl from '@docusaurus/useBaseUrl';
````

Puis dans le fichier :

```
<embed
  src={useBaseUrl('/pdf/L0/presentation-philo.pdf')}
  type="application/pdf"
  width="100%"
  height="600px"
/>
```

### Videos

#### youtube

<iframe width="800" height="450" src="https://www.youtube.com/embed/pw0zH_JdHRY?si=_I_P_z2GWPr3GEQk" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

#### google

<iframe src="https://drive.google.com/file/d/1W8CUzhPTo4OaazhEb9amSgqAaT-pOQnA/preview" width="800" height="450" allow="autoplay"></iframe>

#### locale

import useBaseUrl from '@docusaurus/useBaseUrl';

<video
  controls
  width={800}
  height={450}
  style={{ objectFit: 'cover' }}
  src={useBaseUrl('/videos/jour-fin.mp4')}
>
  Votre navigateur ne supporte pas la balise <code>video</code>.
</video>

### Onglets

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
  <TabItem value="apple" label="Apple" default>
    This is an apple 🍎
  </TabItem>
  <TabItem value="orange" label="Orange">
    This is an orange 🍊
  </TabItem>
  <TabItem value="banana" label="Banana">
    This is a banana 🍌
  </TabItem>
</Tabs>

#### Exercice

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

:::tip[EXERCICE]

<Tabs>
  <TabItem value="question" label="Question ❓" default>
    1. Il faut
    2. Et il faut
  </TabItem>
  <TabItem value="solution" label="Réponse ✅">
    1. Il fallait
    2. Et il fallait
  </TabItem>
</Tabs>

:::

## Différences jekyll / docusaurus

### enlever les {:target="_blank" }
Par défaut, Docusaurus ouvre automatiquement les liens externes dans un nouvel onglet, donc tu n'as pas besoin de spécifier target="_blank".

### Images dans tableau

``md
<div style={{textAlign: 'center', minWidth: '250px'}}><a href={useBaseUrl('/img/dgemc/antigone.png')} target="_blank" rel="noopener noreferrer"><img src={useBaseUrl('/img/dgemc/antigone.png')} alt="Image"/></a></div>
```

