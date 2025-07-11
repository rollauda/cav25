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
        """Convertit les références d'images Jekyll vers Docusaurus avec syntaxe require()"""
        
        # Supprimer {{ site.baseurl }} dans les images
        if re.search(r'!\[([^\]]*)\]\(\{\{\s*site\.baseurl\s*\}\}', content):
            content = re.sub(r'!\[([^\]]*)\]\(\{\{\s*site\.baseurl\s*\}\}/?([^)]+)\)', r'![\1](/\2)', content)
            self.log("Variables site.baseurl dans images supprimées")
        
        # Convertir les balises <img> avec style vers syntaxe Docusaurus
        img_style_pattern = r'<img\s+src="([^"]+)"\s+style="[^"]*"\s*/>'
        if re.search(img_style_pattern, content):
            def replace_img_style(match):
                img_path = match.group(1)
                # Adapter le chemin pour Docusaurus
                adapted_path = self.adapt_asset_path(img_path, 'img')
                
                return f'''<div style={{{{textAlign: 'center'}}}}>
  <a href={{useBaseUrl('{adapted_path}')}} target="_blank" rel="noopener noreferrer">
    <img
      src={{useBaseUrl('{adapted_path}')}}
      alt="Image"
      style={{{{width: '65%'}}}}
    />
  </a>
</div>'''
            
            content = re.sub(img_style_pattern, replace_img_style, content)
            self.log("Images <img> avec style converties vers syntaxe Docusaurus")
        
        # Convertir les images Markdown simples vers syntaxe Docusaurus centrée
        markdown_img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        if re.search(markdown_img_pattern, content):
            def replace_markdown_img(match):
                alt_text = match.group(1) or "Image"
                img_path = match.group(2)
                
                # Adapter le chemin pour Docusaurus
                adapted_path = self.adapt_asset_path(img_path, 'img')
                
                return f'''<div style={{{{textAlign: 'center'}}}}>
  <a href={{useBaseUrl('{adapted_path}')}} target="_blank" rel="noopener noreferrer">
    <img
      src={{useBaseUrl('{adapted_path}')}}
      alt="{alt_text}"
      style={{{{width: '65%'}}}}
    />
  </a>
</div>'''
            
            content = re.sub(markdown_img_pattern, replace_markdown_img, content)
            self.log("Images Markdown converties vers syntaxe Docusaurus centrée (65%)")
        
        # Convertir les chemins assets vers img dans les balises existantes
        if re.search(r'/assets/img/', content):
            content = re.sub(r'/assets/img/', '/img/', content)
            content = re.sub(r'assets/img/', '/img/', content)
            self.log("Chemins assets/img/ convertis vers /img/")
        
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
            'highlight', 'important', 'important-title', 'warning', 'attention', 
            'attention-title', 'nouveau', 'nouveau-title', 'new', 'danger', 'error', 'info'
        ]
        
        # Pattern pour détecter SEULEMENT les vraies admonitions
        for class_name in admonition_classes:
            pattern = rf'\{{\s*:\s*\.{class_name}(?:\s*\.[\w-]+)*\s*\}}\s*\n((?:>\s*[^\n]*(?:\n|$))+)'
            
            def convert_specific_admonition(match):
                blockquote_content = match.group(1)
                
                # Nettoyer le contenu du blockquote
                clean_content = re.sub(r'^>\s*', '', blockquote_content, flags=re.MULTILINE)
                clean_content = clean_content.strip()
                
                # Mapper vers les types d'admonitions Docusaurus
                if class_name in ['highlight']:
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
                else:
                    return f':::note\n{clean_content}\n:::'
            
            if re.search(pattern, content, flags=re.MULTILINE):
                content = re.sub(pattern, convert_specific_admonition, content, flags=re.MULTILINE)
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
                return f'''<embed
  src={{useBaseUrl('{adapted_path}')}}
  type="application/pdf"
  width="100%"
  height="600px"
/>

<span style={{{{backgroundColor: '#f5f5f5', padding: '2px 4px', borderRadius: '3px', fontSize: '13px'}}}}>→ [Ouvrir ce PDF dans un nouvel onglet]({adapted_path})</span>'''
            
            content = re.sub(pdf_pattern, replace_pdf, content)
            self.log("Embeds PDF Jekyll convertis avec ligne de téléchargement")
        
        return content
    
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
                
                return f'''<img
  src={{useBaseUrl('{adapted_path}')}}
  style={{{{{style_content}}}}}
  alt=""
/>'''
            
            content = re.sub(img_pattern, replace_image, content)
            self.log("Images converties avec style centré (largeur 65% par défaut)")
        
        return content
    
    def adapt_asset_path(self, jekyll_path, asset_type='img'):
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
        elif asset_type == 'img' or path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')):
            # Images vers /img/
            path = re.sub(r'^img/', '', path)  # Enlever img/ du début si présent
            return f'/img/{path}'
        else:
            # Autres assets
            return f'/{path}'
    
    def standardize_iframes(self, content):
        """Standardise toutes les iframes pour une largeur 100% et hauteur adaptée"""
        
        # Pattern général pour toutes les iframes
        iframe_pattern = r'<iframe([^>]*?)></iframe>'
        
        def standardize_iframe(match):
            attrs = match.group(1)
            
            # Garder les attributs importants (src, allowfullscreen, etc.)
            src_match = re.search(r'src\s*=\s*["\']([^"\']+)["\']', attrs)
            allowfullscreen = 'allowfullscreen' in attrs.lower()
            frameborder = 'frameborder="0"'
            
            if not src_match:
                return match.group(0)  # Retourner tel quel si pas de src
            
            src = src_match.group(1)
            
            # Déterminer la hauteur selon le type de contenu
            if 'youtube.com' in src or 'youtu.be' in src:
                height = '450px'  # YouTube
            elif 'drive.google.com' in src:
                height = '600px'  # Google Drive
            else:
                height = '500px'  # Autres
            
            # Construire la nouvelle iframe standardisée
            new_attrs = [
                f'src="{src}"',
                'width="100%"',
                f'height="{height}"',
                frameborder
            ]
            
            if allowfullscreen:
                new_attrs.append('allowfullscreen')
            
            return f'<iframe {" ".join(new_attrs)}></iframe>'
        
        if re.search(iframe_pattern, content, flags=re.DOTALL):
            content = re.sub(iframe_pattern, standardize_iframe, content, flags=re.DOTALL)
            self.log("iframes standardisées (largeur 100%, hauteur adaptée)")
        
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
        
        # Supprimer les variables Liquid simples
        if re.search(r'\{\{\s*[^}]+\s*\}\}', content):
            content = re.sub(r'\{\{\s*[^}]+\s*\}\}', '', content)
            liquid_found = True
        
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
            content = self.normalize_headings(content)
            content = self.convert_front_matter(content)
            content = self.convert_links(content)
            content = self.convert_images(content)
            content = self.convert_admonitions(content)
            content = self.convert_code_blocks(content)
            content = self.convert_liquid_tags(content)
            content = self.convert_pdf_embeds(content)
            content = self.convert_image_embeds(content)
            content = self.standardize_iframes(content)
            content = self.convert_br_tags(content)
            content = self.convert_toc(content)
            content = self.clean_kramdown_attributes(content)
            
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
        """Convertit les balises <br> en retours à la ligne Markdown"""
        
        if re.search(r'<br\s*/?>', content):
            content = re.sub(r'<br\s*/?>', '  \n', content)
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
    
def get_user_input():
    """Interface interactive pour obtenir les chemins des fichiers"""
    
    print("🔄 Convertisseur Jekyll vers Docusaurus")
    print("=" * 40)
    
    # Chemins par défaut
    default_input = "convert-md/input.md"
    default_output = "convert-md/output.md"
    
    print(f"📁 Fichiers par défaut:")
    print(f"   Entrée: {default_input}")
    print(f"   Sortie: {default_output}")
    
    use_defaults = input("\n✅ Utiliser ces chemins par défaut ? (O/n) : ").strip().lower()
    
    if use_defaults == 'n' or use_defaults == 'non':
        # Demander les chemins personnalisés
        print("\n📝 Configuration personnalisée:")
        
        # Demander le fichier d'entrée
        while True:
            input_path = input("📁 Chemin du fichier Jekyll (.md) : ").strip()
            if not input_path:
                print("❌ Veuillez entrer un chemin de fichier")
                continue
            
            input_file = Path(input_path)
            if not input_file.exists():
                print(f"❌ Le fichier {input_file} n'existe pas")
                continue
            
            if input_file.suffix.lower() != '.md':
                print("❌ Le fichier doit avoir l'extension .md")
                continue
            
            break
        
        # Demander le fichier de sortie
        output_path = input("📝 Chemin du fichier de sortie (.md) : ").strip()
        if not output_path:
            output_path = input_file.parent / f"{input_file.stem}-docusaurus.md"
        else:
            output_path = Path(output_path)
            # Ajouter l'extension .md si manquante
            if output_path.suffix.lower() != '.md':
                output_path = output_path.with_suffix('.md')
        
        return str(input_file), str(output_path)
    
    else:
        # Utiliser les chemins par défaut
        input_file = Path(default_input)
        output_file = Path(default_output)
        
        # Vérifier que le fichier d'entrée existe
        if not input_file.exists():
            print(f"\n❌ Le fichier par défaut {input_file} n'existe pas")
            print("💡 Créez le fichier ou utilisez l'option personnalisée (n)")
            return get_user_input()  # Relancer la demande
        
        return str(input_file), str(output_file)

def main():
    """Fonction principale"""
    
    try:
        # Interface interactive
        input_file, output_file = get_user_input()
        
        print("\n🚀 Début de la conversion...")
        print("-" * 40)
        
        # Conversion
        converter = JekyllToDocusaurusConverter()
        success = converter.convert_file(input_file, output_file)
        
        print("-" * 40)
        if success:
            print("✅ Conversion réussie!")
            print("\n📋 Modifications appliquées:")
            for log_entry in converter.conversion_log:
                print(f"   • {log_entry}")
            
            print(f"\n📂 Fichier converti disponible: {output_file}")
            print("\n💡 Prochaines étapes:")
            print("   1. Vérifiez le fichier converti")
            print("   2. Copiez-le dans votre projet Docusaurus")
            print("   3. Testez le rendu avec 'npm start'")
        else:
            print("❌ Échec de la conversion")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ Conversion annulée par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")

if __name__ == '__main__':
    main()
