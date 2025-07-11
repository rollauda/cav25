#!/usr/bin/env python3

import re

def convert_pdf_embeds(content):
    """Convertit les embeds PDF Jekyll vers une syntaxe compatible Docusaurus"""
    
    # Pattern pour détecter les embeds PDF Jekyll - plus flexible
    pdf_pattern = r'\{\%\s*pdf\s+["\']([^"\']*)["\']([^%]*)\%\}'
    
    def replace_pdf(match):
        pdf_path = match.group(1)
        options = match.group(2).strip() if match.group(2) else ""
        
        print(f"DEBUG: pdf_path = {pdf_path}")
        print(f"DEBUG: options = {options}")
        
        # Adapter le chemin du PDF pour Docusaurus
        adapted_path = adapt_asset_path(pdf_path, 'pdf')
        
        # Parser les options (width, height, no_link, etc.)
        width = "100%"
        height = "600px"
        
        if "width=" in options:
            width_match = re.search(r'width=([^\s]+)', options)
            if width_match:
                width = width_match.group(1)
        
        if "height=" in options:
            height_match = re.search(r'height=([^\s]+)', options)
            if height_match:
                height = height_match.group(1)
        
        # Générer le code Docusaurus (iframe ou embed)
        return f'<iframe src="{adapted_path}" width="{width}" height="{height}" style={{{{border: "none"}}}}></iframe>'
    
    print(f"DEBUG: Chercher pattern dans: {content}")
    if re.search(pdf_pattern, content):
        print("DEBUG: Pattern trouvé!")
        content = re.sub(pdf_pattern, replace_pdf, content)
        print("Embeds PDF Jekyll convertis")
    else:
        print("DEBUG: Pattern NOT trouvé!")
        print(f"DEBUG: Pattern utilisé: {pdf_pattern}")
    
    return content

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

# Test
test_content = '''{% pdf "../../assets/pdf/ressources/vocabulaire-cinema.pdf" width=80% height=700px no_link %}'''

print("AVANT:")
print(test_content)
print("\nAPRES:")
result = convert_pdf_embeds(test_content)
print(result)
