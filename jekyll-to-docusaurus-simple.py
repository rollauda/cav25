#!/usr/bin/env python3
"""
Script de conversion Jekyll vers Docusaurus - Version Simple
Convertit un fichier Markdown Jekyll en format Docusaurus
"""

import os
import re
import yaml
from pathlib import Path
from datetime import datetime

class JekyllToDocusaurusConverter:
    def __init__(self):
        self.conversion_log = []
        
    def log(self, message):
        """Ajoute un message au log de conversion"""
        self.conversion_log.append(message)
        print(f"✓ {message}")
    
    def convert_front_matter(self, content):
        """Convertit le front matter Jekyll vers Docusaurus"""
        if not content.startswith('---'):
            return content
            
        try:
            # Extraire le front matter
            parts = content.split('---', 2)
            if len(parts) < 3:
                return content
                
            front_matter_str = parts[1]
            body = parts[2]
            
            # Parser le YAML
            jekyll_fm = yaml.safe_load(front_matter_str) or {}
            docusaurus_fm = {}
            
            # Conversions de champs
            field_mapping = {
                'title': 'title',
                'date': 'date',
                'author': 'authors',
                'tags': 'tags',
                'categories': 'tags',  # Categories -> tags
                'description': 'description',
                'permalink': 'slug',
                'excerpt': 'description'
            }
            
            for jekyll_field, docusaurus_field in field_mapping.items():
                if jekyll_field in jekyll_fm:
                    value = jekyll_fm[jekyll_field]
                    
                    # Traitement spécial pour certains champs
                    if jekyll_field == 'permalink':
                        # Nettoyer le permalink
                        value = value.strip('/')
                        if value.startswith('/'):
                            value = value[1:]
                    elif jekyll_field == 'categories' and 'tags' in docusaurus_fm:
                        # Fusionner categories avec tags existants
                        if isinstance(value, list):
                            docusaurus_fm['tags'].extend(value)
                        else:
                            docusaurus_fm['tags'].append(value)
                        continue
                    elif jekyll_field == 'date':
                        # Formater la date
                        if isinstance(value, str):
                            value = value.split('T')[0].split(' ')[0]
                    
                    docusaurus_fm[docusaurus_field] = value
            
            # Nettoyer les tags (dédoublonner)
            if 'tags' in docusaurus_fm and isinstance(docusaurus_fm['tags'], list):
                docusaurus_fm['tags'] = list(set(docusaurus_fm['tags']))
            
            # Reconstruire le contenu
            if docusaurus_fm:
                new_front_matter = yaml.dump(docusaurus_fm, default_flow_style=False, allow_unicode=True)
                new_content = f"---\n{new_front_matter}---{body}"
                self.log("Front matter converti")
            else:
                new_content = body.lstrip('\n')
                
            return new_content
            
        except Exception as e:
            print(f"⚠️ Erreur front matter: {e}")
            return content
    
    def convert_links(self, content):
        """Convertit les liens Jekyll vers Docusaurus"""
        
        # Supprimer {{ site.baseurl }} et variations
        if re.search(r'\{\{\s*site\.(baseurl|url)\s*\}\}', content):
            content = re.sub(r'\{\{\s*site\.baseurl\s*\}\}/?', '', content)
            content = re.sub(r'\{\{\s*site\.url\s*\}\}/?', '', content)
            self.log("Variables site.baseurl supprimées")
        
        # Convertir {% link %} tags
        def replace_link_tag(match):
            link_path = match.group(1).strip()
            # Convertir le chemin Jekyll vers un chemin relatif Docusaurus
            if link_path.startswith('_posts/'):
                # Articles de blog
                filename = link_path.split('/')[-1]
                clean_name = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', filename)
                clean_name = clean_name.replace('.md', '')
                return f'/blog/{clean_name}'
            elif link_path.startswith('_pages/'):
                # Pages
                clean_name = link_path.replace('_pages/', '').replace('.md', '')
                return f'/{clean_name}'
            else:
                # Autres fichiers
                return f'./{link_path.replace(".md", "")}'
        
        if re.search(r'\{\%\s*link\s+[^\}]+\s*\%\}', content):
            content = re.sub(r'\{\%\s*link\s+([^\}]+)\s*\%\}', replace_link_tag, content)
            self.log("Tags {% link %} convertis")
        
        # Supprimer les attributs Kramdown sur les liens
        if re.search(r'\]\([^)]+\)\{[^}]+\}', content):
            content = re.sub(r'\]\([^)]+\)\{[^}]+\}', lambda m: m.group(0).split('{')[0], content)
            self.log("Attributs Kramdown supprimés")
        
        return content
    
    def convert_images(self, content):
        """Convertit les références d'images Jekyll vers Docusaurus avec syntaxe centrée et cliquable"""
        
        # Supprimer {{ site.baseurl }} dans les images
        if re.search(r'!\[([^\]]*)\]\(\{\{\s*site\.baseurl\s*\}\}', content):
            content = re.sub(r'!\[([^\]]*)\]\(\{\{\s*site\.baseurl\s*\}\}/?([^)]+)\)', r'![\1](/\2)', content)
            self.log("Variables site.baseurl dans images supprimées")
        
        # Ajouter l'import useBaseUrl si nécessaire
        needs_usebaseurl = False
        if re.search(r'<img[^>]*src\s*=\s*["\'][^"\']*(?:/assets/|assets/|/img/)', content) or \
           re.search(r'!\[([^\]]*)\]\(([^)]*(?:/assets/|assets/|/img/)[^)]*)\)', content):
            needs_usebaseurl = True
        
        # Convertir les balises <img> vers syntaxe Docusaurus centrée et cliquable
        img_pattern = r'<img\s+([^>]*?)src\s*=\s*["\']([^"\']+)["\']([^>]*?)/?>'
        if re.search(img_pattern, content):
            def replace_img(match):
                before_src = match.group(1).strip()
                img_path = match.group(2)
                after_src = match.group(3).strip()
                
                # Adapter le chemin pour Docusaurus
                adapted_path = self.adapt_asset_path(img_path, 'img')
                
                # Extraire les attributs existants
                existing_attrs = before_src + ' ' + after_src
                
                # Extraire la largeur si spécifiée, sinon 65% par défaut
                width = "65%"
                width_match = re.search(r'width\s*=\s*["\']?([^"\';\s]+)', existing_attrs)
                if width_match:
                    specified_width = width_match.group(1)
                    if '%' in specified_width or 'px' in specified_width:
                        width = specified_width
                    else:
                        width = specified_width + 'px'
                
                # Extraire l'alt text
                alt_text = "Image"
                alt_match = re.search(r'alt\s*=\s*["\']([^"\']*)["\']', existing_attrs)
                if alt_match:
                    alt_text = alt_match.group(1)
                
                # Construire le template avec la bonne syntaxe JSX
                template = '''<div style={{textAlign: 'center'}}>
  <a href={useBaseUrl('PATH')} target="_blank" rel="noopener noreferrer">
    <img
      src={useBaseUrl('PATH')}
      alt="ALT_TEXT"
      style={{width: 'WIDTH'}}
    />
  </a>
</div>'''
                return template.replace('PATH', adapted_path).replace('ALT_TEXT', alt_text).replace('WIDTH', width)
            
            content = re.sub(img_pattern, replace_img, content)
            self.log("Images <img> converties vers syntaxe Docusaurus centrée et cliquable")
        
        # Convertir les images Markdown simples vers syntaxe Docusaurus centrée et cliquable
        markdown_img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        if re.search(markdown_img_pattern, content):
            def replace_markdown_img(match):
                alt_text = match.group(1) or "Image"
                img_path = match.group(2)
                
                # Adapter le chemin pour Docusaurus
                adapted_path = self.adapt_asset_path(img_path, 'img')
                
                # Construire le template avec la bonne syntaxe JSX
                template = '''<div style={{textAlign: 'center'}}>
  <a href={useBaseUrl('PATH')} target="_blank" rel="noopener noreferrer">
    <img
      src={useBaseUrl('PATH')}
      alt="ALT_TEXT"
      style={{width: '65%'}}
    />
  </a>
</div>'''
                return template.replace('PATH', adapted_path).replace('ALT_TEXT', alt_text)
            
            content = re.sub(markdown_img_pattern, replace_markdown_img, content)
            self.log("Images Markdown converties vers syntaxe Docusaurus centrée et cliquable (65%)")
        
        # Ajouter l'import useBaseUrl si nécessaire
        if needs_usebaseurl and 'import useBaseUrl' not in content:
            # Trouver la fin du front matter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    front_matter = f"---{parts[1]}---"
                    body = parts[2]
                    import_line = '\n\nimport useBaseUrl from \'@docusaurus/useBaseUrl\';\n'
                    content = front_matter + import_line + body
                    self.log("Import useBaseUrl ajouté")
        
        return content
    
    def convert_admonitions(self, content):
        """Convertit les admonitions Jekyll vers Docusaurus"""
        
        # Convertir les blockquotes avec classes Kramdown spécifiques
        patterns = [
            (r'>\s*\*\*Note:\*\*\s*([^\n]+)\n\{:\s*\.note\s*\}', r':::note\n\1\n:::'),
            (r'>\s*\*\*Info:\*\*\s*([^\n]+)\n\{:\s*\.info\s*\}', r':::info\n\1\n:::'),
            (r'>\s*\*\*Attention:\*\*\s*([^\n]+)\n\{:\s*\.warning\s*\}', r':::warning\n\1\n:::'),
            (r'>\s*\*\*Danger:\*\*\s*([^\n]+)\n\{:\s*\.danger\s*\}', r':::danger\n\1\n:::'),
            (r'>\s*\*\*Conseil:\*\*\s*([^\n]+)\n\{:\s*\.tip\s*\}', r':::tip\n\1\n:::'),
        ]
        
        converted = False
        for pattern, replacement in patterns:
            if re.search(pattern, content, flags=re.MULTILINE):
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                converted = True
        
        # Convertir seulement les classes admonition spécifiques Jekyll vers Docusaurus
        # Classes qui correspondent vraiment à des admonitions
        admonition_classes = [
            'highlight', 'highlight-title', 'important', 'important-title', 'warning', 'attention', 
            'attention-title', 'nouveau', 'nouveau-title', 'new', 'danger', 'error', 'info',
            'note-title'  # Ajout de la classe note-title
        ]
        
        # Pattern amélioré pour détecter les admonitions même en début de fichier
        # Gère les cas où la classe est suivie directement par un blockquote
        for class_name in admonition_classes:
            # Pattern principal : classe suivie d'un blockquote (avec ou sans ligne vide)
            pattern = rf'\{{\s*:\s*\.{class_name}(?:\s*\.[\w-]+)*\s*\}}\s*\n((?:>\s*[^\n]*(?:\n|$))+)'
            
            def convert_specific_admonition(match):
                blockquote_content = match.group(1)
                
                # Nettoyer TOUS les chevrons, y compris ceux imbriqués
                # Utiliser une approche plus robuste qui supprime tous les chevrons
                lines = blockquote_content.split('\n')
                clean_lines = []
                
                for line in lines:
                    # Supprimer tous les chevrons en début de ligne jusqu'à ce qu'il n'y en ait plus
                    while line.startswith('>'):
                        line = line[1:].lstrip()
                    clean_lines.append(line)
                
                clean_content = '\n'.join(clean_lines).strip()
                
                # Mapper vers les types d'admonitions Docusaurus
                if class_name in ['highlight', 'highlight-title']:
                    return f':::note\n{clean_content}\n:::'
                elif class_name in ['important', 'important-title']:
                    return f':::important\n{clean_content}\n:::'
                elif class_name in ['warning', 'attention', 'attention-title']:
                    return f':::warning\n{clean_content}\n:::'
                elif class_name in ['nouveau', 'nouveau-title', 'new']:
                    return f':::tip\n{clean_content}\n:::'
                elif class_name in ['danger', 'error']:
                    return f':::danger\n{clean_content}\n:::'
                elif class_name in ['info']:
                    return f':::info\n{clean_content}\n:::'
                elif class_name in ['note-title']:
                    return f':::note\n{clean_content}\n:::'
                else:
                    return f':::note\n{clean_content}\n:::'
            
            if re.search(pattern, content, flags=re.MULTILINE):
                content = re.sub(pattern, convert_specific_admonition, content, flags=re.MULTILINE)
                converted = True
        
        # Pattern spécial pour les admonitions en tout début de fichier
        # Gère le cas où le fichier commence directement par une classe suivie d'un blockquote
        start_pattern = rf'^(\{{\s*:\s*\.(?:' + '|'.join(admonition_classes) + r')(?:\s*\.[\w-]+)*\s*\}}\s*\n(?:>\s*[^\n]*(?:\n|$))+)'
        
        def convert_start_admonition(match):
            full_match = match.group(1)
            
            # Extraire la classe
            class_match = re.search(r'\{:\s*\.([^}\s]+)', full_match)
            if not class_match:
                return full_match
            
            class_name = class_match.group(1)
            
            # Extraire le contenu du blockquote
            blockquote_match = re.search(r'\}\s*\n((?:>\s*[^\n]*(?:\n|$))+)', full_match)
            if not blockquote_match:
                return full_match
            
            blockquote_content = blockquote_match.group(1)
            
            # Nettoyer TOUS les chevrons, y compris ceux imbriqués
            # Utiliser une approche plus robuste qui supprime tous les chevrons
            lines = blockquote_content.split('\n')
            clean_lines = []
            
            for line in lines:
                # Supprimer tous les chevrons en début de ligne jusqu'à ce qu'il n'y en ait plus
                while line.startswith('>'):
                    line = line[1:].lstrip()
                clean_lines.append(line)
            
            clean_content = '\n'.join(clean_lines).strip()
            
            # Mapper vers les types d'admonitions Docusaurus
            if class_name in ['highlight', 'highlight-title']:
                return f':::note\n{clean_content}\n:::'
            elif class_name in ['important', 'important-title']:
                return f':::important\n{clean_content}\n:::'
            elif class_name in ['warning', 'attention', 'attention-title']:
                return f':::warning\n{clean_content}\n:::'
            elif class_name in ['nouveau', 'nouveau-title', 'new']:
                return f':::tip\n{clean_content}\n:::'
            elif class_name in ['danger', 'error']:
                return f':::danger\n{clean_content}\n:::'
            elif class_name in ['info']:
                return f':::info\n{clean_content}\n:::'
            elif class_name in ['note-title']:
                return f':::note\n{clean_content}\n:::'
            else:
                return f':::note\n{clean_content}\n:::'
        
        if re.search(start_pattern, content, flags=re.MULTILINE):
            content = re.sub(start_pattern, convert_start_admonition, content, flags=re.MULTILINE)
            converted = True
        
        # Convertir les divs alert en admonitions
        alert_patterns = [
            (r'<div class="alert alert-info">\s*<strong>([^<]+):</strong>\s*([^<]+)</div>', r':::info \1\n\2\n:::'),
            (r'<div class="alert alert-warning">\s*<strong>([^<]+):</strong>\s*([^<]+)</div>', r':::warning \1\n\2\n:::'),
            (r'<div class="alert alert-danger">\s*<strong>([^<]+):</strong>\s*([^<]+)</div>', r':::danger \1\n\2\n:::'),
        ]
        
        for pattern, replacement in alert_patterns:
            if re.search(pattern, content, flags=re.MULTILINE | re.DOTALL):
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
                converted = True
        
        if converted:
            self.log("Admonitions converties")
        
        return content
    
    def convert_code_blocks(self, content):
        """Convertit les blocs de code Jekyll vers Docusaurus"""
        
        # Convertir {% highlight %} vers ```
        def replace_highlight(match):
            language = match.group(1).strip()
            options = match.group(2) if match.group(2) else ""
            code = match.group(3).strip()
            
            # Traiter les options
            show_line_numbers = ""
            if 'linenos' in options:
                show_line_numbers = " showLineNumbers"
            
            return f"```{language}{show_line_numbers}\n{code}\n```"
        
        if re.search(r'\{\%\s*highlight\s+', content):
            content = re.sub(
                r'\{\%\s*highlight\s+(\w+)([^%]*)\%\}(.*?)\{\%\s*endhighlight\s*\%\}',
                replace_highlight,
                content,
                flags=re.DOTALL
            )
            self.log("Blocs {% highlight %} convertis")
        
        return content
    
    def convert_pdf_embeds(self, content):
        """Convertit les embeds PDF Jekyll vers une syntaxe compatible Docusaurus avec ligne de téléchargement"""
        
        # Pattern pour détecter les embeds PDF Jekyll (avec guillemets)
        pdf_pattern = r'\{%\s*pdf\s+"([^"]+\.pdf)"\s*[^}]*\s*%\}'
        
        if re.search(pdf_pattern, content):
            # Ajouter l'import useBaseUrl si nécessaire
            if 'import useBaseUrl' not in content:
                # Trouver la fin du front matter
                front_matter_end = content.find('---', 3) + 3
                if front_matter_end > 2:
                    import_line = '\n\nimport useBaseUrl from \'@docusaurus/useBaseUrl\';\n'
                    content = content[:front_matter_end] + import_line + content[front_matter_end:]
            
            def replace_pdf(match):
                pdf_path = match.group(1).strip()
                
                # Adapter le chemin du PDF pour Docusaurus
                adapted_path = self.adapt_asset_path(pdf_path, 'pdf')
                
                # Générer la balise embed avec useBaseUrl et ligne de téléchargement
                template = '''<embed
  src={useBaseUrl('PATH')}
  type="application/pdf"
  width="100%"
  height="600px"
/>

<span style={{backgroundColor: '#f5f5f5', padding: '2px 4px', borderRadius: '3px', fontSize: '13px'}}>→ [Ouvrir ce PDF dans un nouvel onglet](PATH)</span>'''
                return template.replace('PATH', adapted_path)
            
            content = re.sub(pdf_pattern, replace_pdf, content)
            self.log("Embeds PDF Jekyll convertis avec ligne de téléchargement")
        
        return content
    
    def adapt_asset_path(self, jekyll_path, asset_type='img'):
        """Adapte les chemins d'assets Jekyll vers Docusaurus
        
        Convertit:
        - /assets/img/fichier.jpg → /img/dgemc/fichier.jpg  
        - /assets/pdf/fichier.pdf → /pdf/fichier.pdf
        - assets/img/fichier.jpg → /img/dgemc/fichier.jpg
        - assets/pdf/fichier.pdf → /pdf/fichier.pdf
        """
        
        # Nettoyer le chemin
        path = jekyll_path.strip()
        
        # Supprimer les variables Jekyll
        path = re.sub(r'\{\{\s*site\.baseurl\s*\}\}/?', '', path)
        path = re.sub(r'\{\{\s*site\.url\s*\}\}/?', '', path)
        
        # Déterminer le type d'asset et extraire le nom de fichier
        filename = path
        
        # Gérer les chemins /assets/pdf/ ou assets/pdf/
        if '/assets/pdf/' in path or path.startswith('assets/pdf/'):
            if '/assets/pdf/' in path:
                filename = path.split('/assets/pdf/')[-1]
            else:
                filename = path.split('assets/pdf/')[-1]
            return f'/pdf/{filename}'
        
        # Gérer les chemins /assets/img/ ou assets/img/
        elif '/assets/img/' in path or path.startswith('assets/img/'):
            if '/assets/img/' in path:
                filename = path.split('/assets/img/')[-1]
            else:
                filename = path.split('assets/img/')[-1]
            return f'/img/dgemc/{filename}'
        
        # Gérer les autres chemins /assets/ ou assets/
        elif '/assets/' in path or path.startswith('assets/'):
            if '/assets/' in path:
                filename = path.split('/assets/')[-1]
            else:
                filename = path.split('assets/')[-1]
            
            # Selon le type d'asset demandé ou l'extension
            if asset_type == 'pdf' or filename.endswith('.pdf'):
                return f'/pdf/{filename}'
            elif asset_type == 'img' or filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg')):
                return f'/img/dgemc/{filename}'
            else:
                return f'/files/{filename}'
        
        # Si le chemin ne contient pas assets/, déterminer selon le type
        else:
            # Supprimer les préfixes de chemin relatif
            path = re.sub(r'^\.\./', '', path)
            path = re.sub(r'^\./', '', path)
            
            if asset_type == 'pdf' or path.endswith('.pdf'):
                return f'/pdf/{path}'
            elif asset_type == 'img' or path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg')):
                return f'/img/dgemc/{path}'
            else:
                return f'/{path}'

    def convert_image_embeds(self, content):
        """Convertit les images avec chemins assets vers une syntaxe compatible Docusaurus avec style centré"""
        
        # Pattern pour les balises img avec src="/assets/img/" ou "assets/img/"
        img_pattern = r'<img\s+([^>]*?)src\s*=\s*["\']([^"\']*(?:/assets/img/|assets/img/)[^"\']*)["\']([^>]*?)/?>'
        
        if re.search(img_pattern, content):
            # Ajouter l'import useBaseUrl si nécessaire
            if 'import useBaseUrl' not in content:
                # Trouver la fin du front matter
                front_matter_end = content.find('---', 3) + 3
                if front_matter_end > 2:
                    import_line = '\n\nimport useBaseUrl from \'@docusaurus/useBaseUrl\';\n'
                    content = content[:front_matter_end] + import_line + content[front_matter_end:]
            
            def replace_image(match):
                before_src = match.group(1).strip()
                img_path = match.group(2).strip()
                after_src = match.group(3).strip()
                
                # Adapter le chemin de l'image pour Docusaurus
                adapted_path = self.adapt_asset_path(img_path, 'img')
                
                # Analyser les attributs existants pour préserver certains styles spécifiques
                existing_attrs = before_src + ' ' + after_src
                
                # Vérifier s'il y a déjà une largeur spécifiée
                width_match = re.search(r'width\s*[:=]\s*["\']?([^"\';\s]+)', existing_attrs)
                style_match = re.search(r'style\s*=\s*["\']([^"\']*)["\']', existing_attrs)
                
                # Déterminer la largeur et le style
                width = "65%"  # Largeur par défaut
                additional_styles = ""
                
                if width_match:
                    # Utiliser la largeur existante si spécifiée
                    specified_width = width_match.group(1)
                    if '%' in specified_width or 'px' in specified_width:
                        width = specified_width
                
                if style_match:
                    # Préserver les styles existants mais adapter si nécessaire
                    existing_style = style_match.group(1)
                    # Supprimer zoom car non standard en HTML/CSS
                    if 'zoom:' not in existing_style:
                        additional_styles = existing_style
                
                # Générer la nouvelle balise img centrée avec useBaseUrl
                style_content = f"width: '{width}', display: 'block', margin: '0 auto'"
                if additional_styles:
                    # Convertir le CSS en objet de style React
                    additional_styles = additional_styles.replace(';', ', ').strip(', ')
                    style_content += f", {additional_styles}"
                
                # Construire le template avec la bonne syntaxe JSX
                template = '''<div style={{textAlign: 'center'}}>
  <a href={useBaseUrl('PATH')} target="_blank" rel="noopener noreferrer">
    <img
      src={useBaseUrl('PATH')}
      alt="Image"
      style={{width: 'WIDTH'}}
    />
  </a>
</div>'''
                return template.replace('PATH', adapted_path).replace('WIDTH', width)
            
            content = re.sub(img_pattern, replace_image, content)
            self.log("Images converties avec style centré (largeur 65% par défaut)")
        
        return content
    
    def standardize_iframes(self, content):
        """Standardise toutes les iframes pour une largeur 100% en préservant les proportions d'origine"""
        
        # Pattern général pour toutes les iframes
        iframe_pattern = r'<iframe([^>]*?)></iframe>'
        
        def standardize_iframe(match):
            attrs = match.group(1)
            
            # Garder les attributs importants (src, allowfullscreen, etc.)
            src_match = re.search(r'src\s*=\s*["\']([^"\']+)["\']', attrs)
            allowfullscreen = 'allowfullscreen' in attrs.lower()
            allow_match = re.search(r'allow\s*=\s*["\']([^"\']*)["\']', attrs)
            frameborder = 'frameborder="0"'
            
            if not src_match:
                return match.group(0)  # Retourner tel quel si pas de src
            
            src = src_match.group(1)
            
            # Extraire les dimensions originales pour calculer le ratio
            width_match = re.search(r'width\s*=\s*["\']?(\d+)', attrs)
            height_match = re.search(r'height\s*=\s*["\']?(\d+)', attrs)
            
            # Construire la nouvelle iframe standardisée
            new_attrs = [
                f'src="{src}"',
                'width="100%"'
            ]
            
            # Calculer la hauteur proportionnelle si les dimensions originales sont disponibles
            if width_match and height_match:
                original_width = int(width_match.group(1))
                original_height = int(height_match.group(1))
                # Utiliser la syntaxe JSX pour le style avec aspect-ratio
                new_attrs.append(f'style={{{{aspectRatio: "{original_width}/{original_height}"}}}}')
            else:
                # Hauteur par défaut si on ne peut pas calculer le ratio
                if 'drive.google.com' in src:
                    new_attrs.append('height="600px"')  # Google Drive
                elif 'youtube.com' in src or 'youtu.be' in src:
                    new_attrs.append('height="450px"')  # YouTube
                else:
                    new_attrs.append('height="500px"')  # Autres
            
            new_attrs.append(frameborder)
            
            if allowfullscreen:
                new_attrs.append('allowfullscreen')
            
            # Préserver l'attribut allow s'il existe
            if allow_match:
                new_attrs.append(f'allow="{allow_match.group(1)}"')
            
            return f'<iframe {" ".join(new_attrs)}></iframe>'
        
        if re.search(iframe_pattern, content, flags=re.DOTALL):
            content = re.sub(iframe_pattern, standardize_iframe, content, flags=re.DOTALL)
            self.log("iframes standardisées (largeur 100%, proportions préservées)")
        
        return content

    def convert_tables(self, content):
        """Convertit les tableaux Jekyll/Markdown vers un format Markdown compatible Docusaurus
        
        Jekyll accepte les tableaux sans ligne de séparation ET sans en-tête, 
        mais Docusaurus exige les deux. Cette fonction détecte automatiquement 
        les tableaux Jekyll et ajoute les séparateurs et en-têtes manquants.
        Elle convertit aussi les images mal formatées vers la syntaxe Docusaurus.
        """
        
        # Vérifier si on a besoin d'ajouter l'import useBaseUrl
        needs_usebaseurl = False
        if re.search(r'<img[^>]*src\s*=\s*["\'][^"\']*(?:/assets/|assets/|/img/)', content):
            needs_usebaseurl = True
        
        lines = content.split('\n')
        result_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Détecter une ligne de tableau (commence et finit par |)
            # Pour les tableaux à une colonne, on accepte juste | contenu |
            # Mais on doit avoir au moins 2 caractères entre les pipes
            if line.startswith('|') and line.endswith('|') and len(line) > 4:
                # Vérifier que c'est vraiment un tableau en regardant le contenu
                # Un vrai tableau doit avoir au moins une cellule avec du contenu
                cells = line.split('|')[1:-1]  # Exclure les | du début et de la fin
                
                # Vérifier qu'il y a au moins une cellule non vide
                has_content = any(cell.strip() for cell in cells)
                
                # Vérifier que ce n'est pas juste du texte avec des <br> qui pourrait ressembler à un tableau
                # Si la ligne contient beaucoup de texte et des <br>, c'est probablement du texte normal
                line_without_pipes = line.replace('|', '').strip()
                if ('<br' in line_without_pipes and 
                    len(line_without_pipes) > 100 and 
                    len(cells) == 1 and 
                    not any(keyword in line_without_pipes.lower() for keyword in ['tableau', 'table', 'colonne', 'ligne'])):
                    # C'est probablement du texte normal avec des <br>, pas un tableau
                    result_lines.append(lines[i])
                    i += 1
                    continue
                
                if not has_content:
                    # Ligne vide de tableau ou malformée, traiter comme du texte normal
                    result_lines.append(lines[i])
                    i += 1
                    continue
                # C'est une ligne de tableau
                table_lines = [lines[i]]  # Commencer avec la ligne actuelle
                j = i + 1
                
                # Chercher les lignes suivantes qui font partie du tableau
                while j < len(lines):
                    next_line = lines[j].strip()
                    
                    # Si la ligne suivante est aussi une ligne de tableau
                    if next_line.startswith('|') and next_line.endswith('|') and len(next_line) > 2:
                        table_lines.append(lines[j])
                        j += 1
                    # Si c'est une ligne vide, on continue à chercher
                    elif not next_line:
                        j += 1
                        break
                    else:
                        # Fin du tableau
                        break
                
                # Traiter le tableau détecté
                if len(table_lines) >= 1:
                    # Convertir les images dans chaque ligne du tableau
                    converted_table_lines = []
                    for table_line in table_lines:
                        converted_line = self.convert_table_images(table_line)
                        converted_table_lines.append(converted_line)
                        if converted_line != table_line:
                            needs_usebaseurl = True
                    
                    table_lines = converted_table_lines
                    
                    # Analyser la première ligne pour déterminer le nombre de colonnes
                    first_line = table_lines[0]
                    cells = first_line.split('|')[1:-1]  # Exclure les | du début et de la fin
                    num_columns = len(cells)
                    
                    # Vérifier si la deuxième ligne est une ligne de séparation
                    has_separator = False
                    if len(table_lines) > 1:
                        second_line = table_lines[1].strip()
                        # Une ligne de séparation contient principalement des - et des |
                        if re.match(r'^\|[\s\-\|:]+\|$', second_line):
                            has_separator = True
                    
                    # Déterminer s'il faut ajouter un en-tête
                    needs_header = False
                    
                    if len(table_lines) == 1:
                        # Tableau à une seule ligne = pas d'en-tête
                        needs_header = True
                    elif not has_separator:
                        # Pas de ligne de séparation = probablement pas d'en-tête
                        needs_header = True
                    elif has_separator and len(table_lines) == 2:
                        # Seulement en-tête + séparateur = tableau vide, ajouter une ligne de données
                        needs_header = False
                    
                    if needs_header:
                        # Ajouter un en-tête générique pour tous les tableaux sans en-tête
                        header_parts = []
                        for col_idx in range(num_columns):
                            if num_columns == 1:
                                header_parts.append(" Contenu ")
                            else:
                                header_parts.append(f" Colonne {col_idx + 1} ")
                        
                        header = '|' + '|'.join(header_parts) + '|'
                        result_lines.append(header)
                        
                        # Ajouter la ligne de séparation
                        separator_parts = ['---' for _ in range(num_columns)]
                        separator = '|' + '|'.join(separator_parts) + '|'
                        result_lines.append(separator)
                        
                        # Ajouter toutes les lignes du tableau original
                        result_lines.extend(table_lines)
                        
                        self.log(f"Tableau Jekyll sans en-tête converti ({num_columns} colonnes)")
                        
                    elif not has_separator:
                        # Tableau avec en-tête mais sans séparateur
                        result_lines.append(table_lines[0])  # En-tête existant
                        
                        # Ajouter la ligne de séparation
                        separator_parts = ['---' for _ in range(num_columns)]
                        separator = '|' + '|'.join(separator_parts) + '|'
                        result_lines.append(separator)
                        
                        # Ajouter le reste des lignes
                        result_lines.extend(table_lines[1:])
                        
                        self.log("Tableau Jekyll converti (ligne de séparation ajoutée)")
                        
                    else:
                        # Tableau complet - l'ajouter tel quel
                        result_lines.extend(table_lines)
                    
                    # Continuer après le tableau
                    i = j
                else:
                    # Ligne normale
                    result_lines.append(lines[i])
                    i += 1
            else:
                # Ligne normale
                result_lines.append(lines[i])
                i += 1
        
        converted_content = '\n'.join(result_lines)
        
        # Ajouter l'import useBaseUrl si nécessaire et s'il n'existe pas déjà
        if needs_usebaseurl and 'import useBaseUrl' not in converted_content:
            # Trouver la fin du front matter
            if converted_content.startswith('---'):
                parts = converted_content.split('---', 2)
                if len(parts) >= 3:
                    front_matter = f"---{parts[1]}---"
                    body = parts[2]
                    import_line = '\n\nimport useBaseUrl from \'@docusaurus/useBaseUrl\';\n'
                    converted_content = front_matter + import_line + body
                    self.log("Import useBaseUrl ajouté pour les images de tableau")
        
        return converted_content

    def convert_table_images(self, table_line):
        """Convertit les images dans une ligne de tableau vers la syntaxe Docusaurus simple"""
        
        # Pattern pour détecter les images dans les cellules de tableau
        # Cherche les balises <img> avec src contenant des chemins d'assets
        img_pattern = r'<img\s+([^>]*?)src\s*=\s*["\']([^"\']*(?:/assets/|assets/)[^"\']*)["\']([^>]*?)/?>'
        
        def replace_table_image(match):
            before_src = match.group(1).strip()
            img_path = match.group(2).strip()
            after_src = match.group(3).strip()
            
            # Adapter le chemin de l'image pour Docusaurus
            adapted_path = self.adapt_asset_path(img_path, 'img')
            
            # Analyser les attributs existants pour préserver la largeur
            existing_attrs = before_src + ' ' + after_src
            
            # Extraire la largeur si spécifiée, sinon utiliser une largeur par défaut
            width = "350"  # Largeur par défaut en pixels
            width_match = re.search(r'width\s*[:=]\s*["\']?([^"\';\s]+)', existing_attrs)
            if width_match:
                specified_width = width_match.group(1)
                # Nettoyer la largeur (supprimer px, %, etc.)
                width = re.sub(r'[^\d]', '', specified_width)
                if not width:
                    width = "350"
            
            # Extraire l'alt text si présent
            alt_text = "Image"
            alt_match = re.search(r'alt\s*=\s*["\']([^"\']*)["\']', existing_attrs)
            if alt_match:
                alt_text = alt_match.group(1)
            
            # Générer la syntaxe JSX correcte pour tableau
            return f'<div style={{{{textAlign: "center"}}}}><img src={{useBaseUrl("{adapted_path}")}} width="{width}" alt="{alt_text}" /></div>'
        
        # Appliquer la conversion
        converted_line = re.sub(img_pattern, replace_table_image, table_line)
        
        # Gérer aussi les images Markdown simples dans les tableaux
        markdown_img_pattern = r'!\[([^\]]*)\]\(([^)]+(?:/assets/|assets/)[^)]*)\)'
        
        def replace_markdown_table_image(match):
            alt_text = match.group(1) or "Image"
            img_path = match.group(2).strip()
            
            # Adapter le chemin de l'image pour Docusaurus
            adapted_path = self.adapt_asset_path(img_path, 'img')
            
            # Générer la syntaxe JSX correcte pour tableau
            return f'<div style={{{{textAlign: "center"}}}}><img src={{useBaseUrl("{adapted_path}")}} width="350" alt="{alt_text}" /></div>'
        
        converted_line = re.sub(markdown_img_pattern, replace_markdown_table_image, converted_line)
        
        if converted_line != table_line:
            self.log("Images dans tableau converties vers syntaxe Docusaurus simple")
        
        return converted_line
    
    def convert_liquid_tags(self, content):
        """Supprime ou convertit les tags Liquid non supportés"""
        
        # Supprimer les tags Liquid courants
        liquid_patterns = [
            r'\{\%\s*assign\s+[^%]+\%\}',
            r'\{\%\s*capture\s+[^%]+\%\}.*?\{\%\s*endcapture\s*\%\}',
            r'\{\%\s*comment\s*\%\}.*?\{\%\s*endcomment\s*\%\}',
            r'\{\%\s*raw\s*\%\}.*?\{\%\s*endraw\s*\%\}',
            r'\{\%\s*include[^%]+\%\}',
            r'\{\%\s*include_relative[^%]+\%\}',
        ]
        
        liquid_found = False
        for pattern in liquid_patterns:
            if re.search(pattern, content, flags=re.DOTALL):
                content = re.sub(pattern, '', content, flags=re.DOTALL)
                liquid_found = True
        
        # Supprimer les variables Liquid simples, mais PAS les objets de style JSX ou les appels useBaseUrl
        # Pattern pour détecter les variables Liquid (pas les objets JSX ou useBaseUrl)
        liquid_var_pattern = r'\{\{\s*(?!(?:textAlign|width|height|margin|padding|fontSize|backgroundColor|borderRadius|aspectRatio)\s*:|useBaseUrl\s*\()[^}]+\s*\}\}'
        if re.search(liquid_var_pattern, content):
            content = re.sub(liquid_var_pattern, '', content)
            liquid_found = True
            print("🔧 Variables Liquid supprimées avec pattern amélioré (styles JSX et useBaseUrl préservés)")
        else:
            print("🔧 Aucune variable Liquid trouvée")
        
        # Supprimer les boucles Liquid
        if re.search(r'\{\%\s*for\s+', content):
            content = re.sub(
                r'\{\%\s*for\s+[^%]+\%\}.*?\{\%\s*endfor\s*\%\}',
                '<!-- Boucle Liquid supprimée - convertir en composant React -->',
                content,
                flags=re.DOTALL
            )
            liquid_found = True
        
        # Supprimer les conditions Liquid
        if re.search(r'\{\%\s*if\s+', content):
            content = re.sub(
                r'\{\%\s*if\s+[^%]+\%\}.*?\{\%\s*endif\s*\%\}',
                '<!-- Condition Liquid supprimée - convertir en composant React -->',
                content,
                flags=re.DOTALL
            )
            liquid_found = True
        
        if liquid_found:
            self.log("Tags Liquid supprimés")
        
        return content
    
    def convert_file(self, input_path, output_path):
        """Convertit un fichier Markdown Jekyll vers Docusaurus"""
        
        input_file = Path(input_path)
        output_file = Path(output_path)
        
        if not input_file.exists():
            print(f"❌ Erreur: Le fichier {input_file} n'existe pas")
            return False
        
        try:
            # Lire le fichier source
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            print(f"📖 Lecture de: {input_file}")
            
            # Appliquer toutes les conversions
            content = self.convert_front_matter(content)
            content = self.normalize_headings(content)  # Normaliser les titres APRÈS le front matter
            content = self.convert_links(content)
            content = self.convert_br_tags(content)  # Convertir les <br> AVANT les tableaux
            content = self.clean_table_line_breaks(content)  # Nettoyer les retours à la ligne dans les tableaux AVANT conversion
            content = self.convert_tables(content)  # AVANT conversion des images
            content = self.convert_images(content)
            content = self.convert_admonitions(content)
            content = self.convert_code_blocks(content)
            content = self.convert_liquid_tags(content)
            content = self.convert_pdf_embeds(content)
            content = self.convert_image_embeds(content)
            content = self.standardize_iframes(content)  # Standardiser les iframes
            content = self.convert_toc(content)
            content = self.clean_kramdown_attributes(content)
            content = self.normalize_headings(content)  # Normaliser les titres
            content = self.clean_table_leading_spaces(content)  # Nettoyer les espaces en début de ligne dans les tableaux EN DERNIER
            
            # Nettoyer les espaces multiples
            content = re.sub(r'\n{3,}', '\n\n', content)
            content = content.strip()
            
            # Créer le répertoire de sortie si nécessaire
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Écrire le fichier converti
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"💾 Fichier sauvegardé: {output_file}")
            
            # Afficher le résumé
            if content != original_content:
                print(f"✨ Conversion terminée avec {len(self.conversion_log)} modifications")
            else:
                print("ℹ️ Aucune modification nécessaire")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la conversion: {e}")
            return False

    def convert_br_tags(self, content):
        """Convertit les balises <br> en retours à la ligne Markdown ou <br/> dans les cellules de tableau"""
        
        if re.search(r'<br\s*/?>', content):
            # Traitement spécial pour les <br> dans les tableaux
            lines = content.split('\n')
            result_lines = []
            
            for line in lines:
                # Vérifier si c'est une ligne de tableau (doit avoir au moins 2 pipes et du contenu)
                stripped_line = line.strip()
                if (stripped_line.startswith('|') and stripped_line.endswith('|') and 
                    stripped_line.count('|') >= 2 and len(stripped_line) > 4):
                    
                    # Dans un tableau, convertir <br> en <br/> (JSX/HTML compatible)
                    if '<br' in line:
                        # Convertir toutes les variations de <br> en <br/>
                        line = re.sub(r'<br\s*/?>', '<br/>', line)
                        self.log("Balises <br> dans tableau converties en <br/>")
                    result_lines.append(line)
                else:
                    # En dehors des tableaux, conversion normale des <br>
                    if '<br' in line:
                        line = re.sub(r'<br\s*/?>', '  \n', line)
                    result_lines.append(line)
            
            content = '\n'.join(result_lines)
            self.log("Balises <br> converties")
        
        return content
    
    def convert_toc(self, content):
        """Gère les tables des matières Jekyll - les supprime complètement"""
        
        toc_found = False
        
        # Supprimer les blocs <details> complets avec TOC Jekyll
        details_toc_pattern = r'<details[^>]*>\s*<summary>\s*[^<]*</summary>\s*.*?- TOC.*?</details>'
        if re.search(details_toc_pattern, content, flags=re.DOTALL | re.IGNORECASE):
            content = re.sub(details_toc_pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
            toc_found = True
        
        # Supprimer les TOC Jekyll simples
        if re.search(r'\*\s*TOC\s*\n\{:toc\}', content):
            content = re.sub(r'\*\s*TOC\s*\n\{:toc\}', '', content)
            toc_found = True
        
        # Supprimer {:toc} isolé
        if re.search(r'\{:toc\}', content):
            content = re.sub(r'\{:toc\}', '', content)
            toc_found = True
        
        # Supprimer les lignes "- TOC" isolées
        if re.search(r'^- TOC\s*$', content, flags=re.MULTILINE):
            content = re.sub(r'^- TOC\s*$', '', content, flags=re.MULTILINE)
            toc_found = True
        
        # Ajouter automatiquement hide_table_of_contents dans le front matter si une TOC Jekyll était présente
        if toc_found:
            # Ajouter dans le front matter que la TOC doit être cachée
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    front_matter_str = parts[1]
                    body = parts[2]
                    
                    try:
                        front_matter = yaml.safe_load(front_matter_str) or {}
                        front_matter['hide_table_of_contents'] = True
                        
                        new_front_matter = yaml.dump(front_matter, default_flow_style=False, allow_unicode=True)
                        content = f"---\n{new_front_matter}---{body}"
                    except:
                        pass  # Si erreur YAML, on garde le contenu tel quel
            
            self.log("Table des matières Jekyll supprimée (TOC automatique désactivée)")
        
        return content
    
    def clean_kramdown_attributes(self, content):
        """Supprime les attributs Kramdown non supportés, sauf les cas spéciaux"""
        
        kramdown_found = False
        
        # Préserver {: .no_toc } pour les titres (utilisé par Docusaurus)
        # Supprimer les autres attributs de bloc {:class} sauf no_toc
        pattern = r'\{:\s*(?!\.no_toc)[^}]+\}'
        if re.search(pattern, content):
            content = re.sub(pattern, '', content)
            kramdown_found = True
        
        # Supprimer les attributs {:toc} mais garder {: .no_toc }
        if re.search(r'\{:toc\}', content):
            content = re.sub(r'\{:toc\}', '', content)
            kramdown_found = True
        
        # Supprimer les autres attributs text-delta, etc.
        pattern_text = r'\{:\s*\.text-[\w-]+\s*\}'
        if re.search(pattern_text, content):
            content = re.sub(pattern_text, '', content)
            kramdown_found = True
        
        if kramdown_found:
            self.log("Attributs Kramdown supprimés (sauf {: .no_toc })")
        
        return content
    
    def normalize_headings(self, content):
        """Normalise les titres pour commencer par un titre de niveau 1 (#)"""
        
        # Séparer le front matter du contenu
        front_matter = ""
        body = content
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                front_matter = f"---{parts[1]}---"
                body = parts[2]
        
        # Trouver le premier titre dans le body
        heading_match = re.search(r'^(#+)\s+(.+)$', body, flags=re.MULTILINE)
        
        if heading_match:
            first_level = len(heading_match.group(1))  # Nombre de #
            
            # Si le premier titre n'est pas de niveau 1, normaliser tous les titres
            if first_level > 1:
                # Calculer le décalage nécessaire
                offset = first_level - 1
                
                # Fonction pour ajuster chaque titre
                def adjust_heading(match):
                    current_level = len(match.group(1))
                    new_level = max(1, current_level - offset)  # Minimum niveau 1
                    return '#' * new_level + ' ' + match.group(2)
                
                # Appliquer l'ajustement à tous les titres
                body = re.sub(r'^(#+)\s+(.+)$', adjust_heading, body, flags=re.MULTILINE)
                
                self.log(f"Titres normalisés (premier titre de niveau {first_level} → niveau 1)")
        
        # Reconstituer le contenu complet
        return front_matter + body
    
    def clean_table_line_breaks(self, content):
        """Nettoie les tableaux en fusionnant les lignes de continuation avec espaces en début"""
        
        lines = content.split('\n')
        result_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            line_stripped = line.strip()
            
            # Détecter une ligne de tableau (commence et finit par |)
            if line_stripped.startswith('|') and line_stripped.endswith('|') and len(line_stripped) > 2:
                # C'est une ligne de tableau
                current_table_line = line_stripped
                j = i + 1
                
                # Chercher les lignes suivantes qui peuvent faire partie de cette ligne de tableau
                while j < len(lines):
                    next_line = lines[j] if j < len(lines) else ""
                    next_line_stripped = next_line.strip()
                    
                    # Si la ligne suivante est une nouvelle ligne de tableau, on s'arrête
                    if next_line_stripped.startswith('|') and next_line_stripped.endswith('|') and len(next_line_stripped) > 2:
                        break
                    # Si c'est une ligne vide, on passe
                    elif not next_line_stripped:
                        j += 1
                        continue
                    # Si la ligne commence par un espace et contient du texte (ligne de continuation)
                    elif next_line.startswith(' ') and next_line_stripped:
                        # Vérifier que ce n'est pas un élément markdown spécial
                        if not next_line_stripped.startswith((':::', '#', '<iframe', '![', '```', '-', '*', '>')):
                            # C'est une ligne de continuation, la fusionner
                            # Enlever le | final de la ligne courante, ajouter le texte, remettre le |
                            current_table_line = current_table_line.rstrip(' |').rstrip() + ' ' + next_line_stripped + ' |'
                            j += 1
                            self.log("Ligne avec espace en début fusionnée dans tableau")
                            continue
                    
                    # Sinon, c'est la fin du tableau
                    break
                
                # Nettoyer les espaces en début de ligne dans les cellules du tableau
                current_table_line = self.clean_table_cell_spaces(current_table_line)
                
                # Ajouter la ligne de tableau nettoyée
                result_lines.append(current_table_line)
                i = j
            else:
                # Ligne normale
                result_lines.append(lines[i])
                i += 1
        
        return '\n'.join(result_lines)
    
    def clean_table_cell_spaces(self, table_line):
        """Nettoie les espaces en début de ligne dans les cellules du tableau"""
        if not table_line.strip().startswith('|'):
            return table_line
        
        # Séparer les cellules
        cells = table_line.split('|')
        
        # Nettoyer chaque cellule
        cleaned_cells = []
        for cell in cells:
            # Enlever tous les espaces/tabs en début ET fin
            cleaned_cell = cell.strip()
            if cleaned_cell and not cleaned_cell.startswith('-'):  # Ne pas toucher aux séparateurs
                # Nettoyer les espaces multiples en début de texte dans la cellule
                cleaned_cell = re.sub(r'^\s+', '', cleaned_cell)
                cleaned_cell = re.sub(r'\s+$', '', cleaned_cell)
                
                # Remplacer les groupes de 4 espaces (marqueurs de <br>) par de vrais sauts de ligne
                cleaned_cell = re.sub(r'    ', '  \n', cleaned_cell)
                
                # Ajouter un espace de marge propre seulement si pas vide
                if cleaned_cell:
                    cleaned_cell = ' ' + cleaned_cell + ' '
                else:
                    cleaned_cell = '  '
            elif not cleaned_cell:
                cleaned_cell = '  '
            cleaned_cells.append(cleaned_cell)
        
        return '|'.join(cleaned_cells)

    def process_table_lines(self, table_lines):
        """Traite les lignes de tableau pour gérer les sauts de ligne et normaliser le contenu"""
        
        cleaned_table_lines = []
        
        for k, table_line in enumerate(table_lines):
            # Vérifier si c'est une ligne de séparation (ne pas toucher)
            if re.match(r'^\|[\s\-\|:]+\|$', table_line.strip()):
                cleaned_table_lines.append(table_line)
                continue
            
            # Traiter une ligne de données de tableau
            processed_line = self.process_table_data_line(table_line)
            
            # Vérifier si la ligne contient des sauts de ligne internes qui nécessitent une division
            if self.should_split_table_line(processed_line):
                # Diviser la ligne en plusieurs lignes de tableau
                split_lines = self.split_table_line_on_breaks(processed_line)
                cleaned_table_lines.extend(split_lines)
            else:
                # Simplement normaliser le contenu des cellules
                normalized_line = self.normalize_table_cell_content(processed_line)
                cleaned_table_lines.append(normalized_line)
        
        return cleaned_table_lines
    
    def process_table_data_line(self, table_line):
        """Traite une ligne de données de tableau"""
        
        # Supprimer les <br> et les convertir en marqueurs de saut de ligne
        line = re.sub(r'<br\s*/?>', ' [LINEBREAK] ', table_line)
        
        # Nettoyer les espaces multiples mais préserver les marqueurs
        line = re.sub(r'  +', ' ', line)
        
        return line.strip()
    
    def should_split_table_line(self, table_line):
        """Détermine si une ligne de tableau doit être divisée à cause de sauts de ligne internes"""
        
        # Vérifier la présence de marqueurs de saut de ligne
        if '[LINEBREAK]' in table_line:
            return True
        
        # Vérifier si le contenu des cellules est trop long (plus de 200 caractères par cellule)
        cells = table_line.split('|')[1:-1]  # Exclure les | du début et de la fin
        for cell in cells:
            if len(cell.strip()) > 200:
                return True
        
        return False
    
    def split_table_line_on_breaks(self, table_line):
        """Divise une ligne de tableau sur les sauts de ligne en créant plusieurs lignes de tableau"""
        
        cells = table_line.split('|')
        
        if len(cells) < 3:  # Pas assez de cellules
            return [self.normalize_table_cell_content(table_line)]
        
        # Traiter chaque cellule
        cell_lines = []
        max_lines = 1
        
        for i in range(1, len(cells) - 1):  # Ignorer la première et dernière cellule vides
            cell_content = cells[i].strip()
            
            # Diviser sur les marqueurs de saut de ligne
            if '[LINEBREAK]' in cell_content:
                lines = [line.strip() for line in cell_content.split('[LINEBREAK]') if line.strip()]
                cell_lines.append(lines)
                max_lines = max(max_lines, len(lines))
            else:
                cell_lines.append([cell_content])
        
        # Créer les lignes de tableau résultantes
        result_lines = []
        
        for line_idx in range(max_lines):
            line_cells = ['']  # Première cellule vide
            
            for cell_idx, cell_content_lines in enumerate(cell_lines):
                if line_idx < len(cell_content_lines):
                    # Utiliser le contenu de cette ligne
                    content = cell_content_lines[line_idx]
                else:
                    # Cellule vide pour cette ligne
                    content = ''
                
                line_cells.append(f' {content} ')
            
            line_cells.append('')  # Dernière cellule vide
            
            # Construire la ligne
            table_line_result = '|'.join(line_cells)
            result_lines.append(table_line_result)
        
        if len(result_lines) > 1:
            self.log(f"Ligne de tableau divisée en {len(result_lines)} lignes")
        
        return result_lines

    def normalize_table_cell_content(self, table_line):
        """Normalise le contenu des cellules de tableau en gérant les retours à la ligne"""
        
        # Séparer les cellules
        cells = table_line.split('|')
        
        # Garder les | du début et de la fin
        if len(cells) < 3:
            return table_line
        
        # Traiter chaque cellule (ignorer la première et la dernière qui sont vides)
        normalized_cells = [cells[0]]  # Premier | vide
        
        for i in range(1, len(cells) - 1):
            cell_content = cells[i].strip()
            
            # Supprimer les marqueurs de saut de ligne restants
            cell_content = cell_content.replace('[LINEBREAK]', ' ')
            
            # Remplacer les <br> par des espaces
            cell_content = re.sub(r'<br\s*/?>', ' ', cell_content)
            
            # Remplacer les retours à la ligne multiples par des espaces
            cell_content = re.sub(r'\s*\n\s*', ' ', cell_content)
            
            # Nettoyer les espaces multiples
            cell_content = re.sub(r'\s+', ' ', cell_content)
            
            # Supprimer les espaces en début et fin, puis ajouter un espace de padding
            cell_content = cell_content.strip()
            normalized_cells.append(f' {cell_content} ')
        
        return '|'.join(normalized_cells)
    
    def clean_table_leading_spaces(self, content):
        """Supprime les espaces en début de ligne dans les cellules de tableau et fusionne les lignes de continuation"""
        lines = content.split('\n')
        result_lines = []
        
        for i, line in enumerate(lines):
            # Si c'est une ligne qui commence par un espace et contient un |
            if line.startswith(' ') and '|' in line:
                # Chercher si la ligne précédente était une ligne de tableau
                if i > 0 and lines[i-1].strip().startswith('|') and lines[i-1].strip().endswith('|'):
                    # Fusionner avec la ligne précédente
                    cleaned_line = line.lstrip()
                    if result_lines:
                        # Enlever le | final de la ligne précédente et ajouter le contenu
                        prev_line = result_lines[-1]
                        if prev_line.endswith(' |'):
                            # Fusionner le contenu
                            merged_content = prev_line[:-2] + ' ' + cleaned_line
                            result_lines[-1] = merged_content
                        else:
                            result_lines.append(line)
                    else:
                        result_lines.append(line)
                else:
                    result_lines.append(line)
            else:
                result_lines.append(line)
        
        return '\n'.join(result_lines)

# Test de conversion
if __name__ == "__main__":
    import sys
    
    converter = JekyllToDocusaurusConverter()
    
    # Vérifier les arguments de ligne de commande
    if len(sys.argv) > 2:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        # Test avec les fichiers dans convert-md
        input_file = "convert-md/input.md"
        output_file = "convert-md/output.md"
    
    print("🚀 Conversion Jekyll vers Docusaurus")
    print(f"📖 Fichier d'entrée : {input_file}")
    print(f"📝 Fichier de sortie : {output_file}")
    
    success = converter.convert_file(input_file, output_file)
    
    if success:
        print("✅ Conversion réussie !")
    else:
        print("❌ Erreur lors de la conversion")
