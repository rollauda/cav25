#!/usr/bin/env python3
"""
Script de conversion Jekyll vers Docusaurus - Version Test Robuste
"""

import re
import os

def convert_file(input_file, output_file):
    """Convertit un fichier Jekyll vers Docusaurus"""
    
    # Lire le fichier
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📖 Lecture de: {input_file}")
    original_content = content
    
    # 1. Convertir les images avec style AVANT les tableaux
    img_style_pattern = r'<img\s+src="([^"]+)"\s+style="[^"]*"\s*/>'
    
    if re.search(img_style_pattern, content):
        def replace_img_style(match):
            img_path = match.group(1)
            
            # Adapter le chemin pour Docusaurus
            if img_path.startswith('/assets/img/'):
                img_path = img_path.replace('/assets/img/', '/img/')
            elif img_path.startswith('assets/img/'):
                img_path = '/' + img_path.replace('assets/img/', 'img/')
            
            return f'''<div style={{{{textAlign: 'center'}}}}>
  <a href={{useBaseUrl('{img_path}')}} target="_blank" rel="noopener noreferrer">
    <img
      src={{useBaseUrl('{img_path}')}}
      alt="Image"
      style={{{{width: '65%'}}}}
    />
  </a>
</div>'''
        
        content = re.sub(img_style_pattern, replace_img_style, content)
        print("✓ Images <img> avec style converties vers syntaxe Docusaurus")
    
    # 2. Convertir le tableau Jekyll spécifique (une seule ligne avec beaucoup de texte)
    # Chercher uniquement le tableau dans le contenu de l'affaire
    long_table_pattern = r'^\|\s*L\'affaire Jacqueline Sauvage[^|]+\|\s*<div style[^|]+\|\s*$'
    
    if re.search(long_table_pattern, content, re.MULTILINE):
        def replace_long_table(match):
            # Extraire les deux parties du tableau
            table_content = match.group(0)
            
            # Diviser en deux cellules
            cells = table_content.split('|')
            if len(cells) >= 3:
                cell1 = cells[1].strip()
                cell2 = cells[2].strip()
                
                # Créer un tableau Markdown propre
                return f"| {cell1} | {cell2} |\n|----------|----------|"
            else:
                return table_content
        
        content = re.sub(long_table_pattern, replace_long_table, content, flags=re.MULTILINE)
        print("✓ Tableau long converti (sans en-tête)")
    
    # 3. Convertir les admonitions Jekyll
    kramdown_admonition_pattern = r'\{:\s*\.(\w+)-title\s*\}\n>\s*([^\n]+)\n>\s*\n>\s*([^\n]+)'
    
    if re.search(kramdown_admonition_pattern, content):
        def replace_admonition(match):
            admonition_type = match.group(1)
            title = match.group(2)
            content_text = match.group(3)
            
            # Mapper les types Jekyll vers Docusaurus
            type_mapping = {
                'nouveau': 'tip',
                'note': 'note',
                'warning': 'warning',
                'danger': 'danger'
            }
            
            docusaurus_type = type_mapping.get(admonition_type, 'info')
            
            return f':::{docusaurus_type}\n{title}\n{content_text}\n:::'
        
        content = re.sub(kramdown_admonition_pattern, replace_admonition, content)
        print("✓ Admonitions converties")
    
    # 4. Standardiser les iframes
    iframe_pattern = r'<iframe\s+width="560"\s+height="315"\s+src="([^"]+)"[^>]*></iframe>'
    
    if re.search(iframe_pattern, content):
        def replace_iframe(match):
            src = match.group(1)
            return f'<iframe src="{src}" width="100%" height="450px" frameborder="0" allowfullscreen></iframe>'
        
        content = re.sub(iframe_pattern, replace_iframe, content)
        print("✓ iframes standardisées (largeur 100%, hauteur adaptée)")
    
    # Écrire le fichier de sortie
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"💾 Fichier sauvegardé: {output_file}")
    print("✨ Conversion terminée")

if __name__ == "__main__":
    input_file = "convert-md/input.md"
    output_file = "convert-md/output.md"
    
    convert_file(input_file, output_file)
