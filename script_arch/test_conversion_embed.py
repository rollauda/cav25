#!/usr/bin/env python3

# Test rapide de la conversion PDF
import re

test_content = '''---
title: Vocabulaire
---
## Vocabulaire technique du cinéma et principaux métiers du cinéma

<br>

{% pdf "../../assets/pdf/ressources/vocabulaire-cinema.pdf" width=80% height=700px no_link %}
'''

def adapt_asset_path(jekyll_path, asset_type='img'):
    """Adapte un chemin d'asset Jekyll vers Docusaurus"""
    
    # Nettoyer le chemin
    path = jekyll_path.strip()
    
    # Supprimer les préfixes Jekyll
    path = re.sub(r'\{\{\s*site\.baseurl\s*\}\}/?', '', path)
    path = re.sub(r'^/assets/', '', path)
    path = re.sub(r'^\.\./\.\./assets/', '', path)
    path = re.sub(r'^assets/', '', path)
    
    # Déterminer le type d'asset et le dossier de destination
    if asset_type == 'pdf' or path.endswith('.pdf'):
        # PDF vers /pdf/
        path = re.sub(r'^pdf/', '', path)  # Enlever pdf/ du début si présent
        return f'/pdf/{path}'
    elif asset_type == 'img' or any(path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']):
        # Images vers /img/
        path = re.sub(r'^img/', '', path)  # Enlever img/ du début si présent
        return f'/img/{path}'
    else:
        # Autres assets vers /static/
        return f'/static/{path}'

# Test de conversion
pdf_pattern = r'\{%\s*pdf\s+"([^"]+\.pdf)"\s*[^}]*\s*%\}'

def replace_pdf(match):
    pdf_path = match.group(1).strip()
    
    # Adapter le chemin du PDF pour Docusaurus avec useBaseUrl
    adapted_path = adapt_asset_path(pdf_path, 'pdf')
    
    # Générer la balise embed avec useBaseUrl (syntaxe qui fonctionne)
    return f'''<embed
  src={{useBaseUrl('{adapted_path}')}}
  type="application/pdf"
  width="100%"
  height="600px"
/>'''

print("Contenu original:")
print(test_content)
print("\n" + "="*50)

result = re.sub(pdf_pattern, replace_pdf, test_content)

print("Contenu converti:")
print(result)
