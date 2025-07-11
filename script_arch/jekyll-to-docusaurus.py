#!/usr/bin/env python3
"""
Script de conversion Jekyll vers Docusaurus
Convertit automatiquement les fichiers Markdown Jekyll en format Docusaurus
"""

import os
import re
import yaml
import argparse
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class JekyllToDocusaurusConverter:
    def __init__(self, input_dir: str, output_dir: str, verbose: bool = False):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        self.conversion_report = []
        
        # Patterns de conversion
        self.liquid_patterns = [
            (r'{%\s*assign\s+(\w+)\s*=\s*["\']([^"\']+)["\'].*?%}', ''),
            (r'{%\s*include\s+([^%]+)\s*%}', r'<!-- TODO: Convertir include \1 en composant React -->'),
            (r'{%\s*include_relative\s+([^%]+)\s*%}', r'<!-- TODO: Convertir include_relative \1 -->'),
            (r'{%\s*for\s+([^%]+)\s*%}.*?{%\s*endfor\s*%}', r'<!-- TODO: Convertir boucle for en JSX -->'),
            (r'{%\s*if\s+([^%]+)\s*%}.*?{%\s*endif\s*%}', r'<!-- TODO: Convertir condition if en JSX -->'),
            (r'{%\s*unless\s+([^%]+)\s*%}.*?{%\s*endunless\s*%}', r'<!-- TODO: Convertir unless en JSX -->'),
            (r'{%\s*highlight\s+(\w+).*?%}(.*?){%\s*endhighlight\s*%}', self._convert_highlight),
            (r'{{\s*([^}]+)\s*}}', r'<!-- TODO: Convertir variable Liquid \1 -->')
        ]
        
        self.link_patterns = [
            (r'{{\s*site\.baseurl\s*}}/([^)\s]+)', r'/\1'),
            (r'{%\s*link\s+([^%]+)\s*%}', r'TODO_CONVERT_LINK'),
            (r'{{\s*site\.url\s*}}', ''),
            (r'{{\s*site\.title\s*}}', 'TODO_SITE_TITLE'),
            (r'{{\s*site\.description\s*}}', 'TODO_SITE_DESCRIPTION')
        ]
        
        self.kramdown_patterns = [
            (r'\{:target="_blank"\}', ''),
            (r'\{:\s*\.([^}]+)\s*\}', r'<div className="\1"></div>'),
            (r'>\s*\*\*([^*]+):\*\*\s*([^\n]+)\n\{:\s*\.note\s*\}', r':::note[\1]\n\2\n:::'),
            (r'>\s*\*\*([^*]+):\*\*\s*([^\n]+)\n\{:\s*\.warning\s*\}', r':::warning[\1]\n\2\n:::'),
            (r'>\s*\*\*([^*]+):\*\*\s*([^\n]+)\n\{:\s*\.info\s*\}', r':::info[\1]\n\2\n:::'),
            (r'>\s*\*\*([^*]+):\*\*\s*([^\n]+)\n\{:\s*\.tip\s*\}', r':::tip[\1]\n\2\n:::')
        ]

    def _convert_highlight(self, match):
        """Convertit les blocs highlight Jekyll en blocs code Docusaurus"""
        language = match.group(1)
        code = match.group(2).strip()
        return f'```{language}\n{code}\n```'

    def _log(self, message: str, level: str = "INFO"):
        """Log des messages avec timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {level}: {message}"
        if self.verbose:
            print(log_message)
        self.conversion_report.append(log_message)

    def _convert_front_matter(self, content: str) -> Tuple[Dict, str]:
        """Convertit le front matter Jekyll en front matter Docusaurus"""
        if not content.startswith('---'):
            return {}, content
        
        try:
            parts = content.split('---', 2)
            if len(parts) < 3:
                return {}, content
            
            jekyll_fm = yaml.safe_load(parts[1])
            markdown_content = parts[2].strip()
            
            # Conversion du front matter
            docusaurus_fm = {}
            
            # Titre
            if 'title' in jekyll_fm:
                docusaurus_fm['title'] = jekyll_fm['title']
            
            # Date
            if 'date' in jekyll_fm:
                if isinstance(jekyll_fm['date'], str):
                    docusaurus_fm['date'] = jekyll_fm['date']
                else:
                    docusaurus_fm['date'] = jekyll_fm['date'].strftime('%Y-%m-%d')
            
            # Tags et catégories
            if 'tags' in jekyll_fm:
                docusaurus_fm['tags'] = jekyll_fm['tags']
            if 'categories' in jekyll_fm:
                if 'tags' in docusaurus_fm:
                    docusaurus_fm['tags'].extend(jekyll_fm['categories'])
                else:
                    docusaurus_fm['tags'] = jekyll_fm['categories']
            
            # Auteur
            if 'author' in jekyll_fm:
                docusaurus_fm['authors'] = jekyll_fm['author']
            
            # Description
            if 'description' in jekyll_fm:
                docusaurus_fm['description'] = jekyll_fm['description']
            elif 'excerpt' in jekyll_fm:
                docusaurus_fm['description'] = jekyll_fm['excerpt']
            
            # Permalink vers slug
            if 'permalink' in jekyll_fm:
                docusaurus_fm['slug'] = jekyll_fm['permalink']
            
            # ID
            if 'id' in jekyll_fm:
                docusaurus_fm['id'] = jekyll_fm['id']
            
            # Position dans la sidebar
            if 'order' in jekyll_fm:
                docusaurus_fm['sidebar_position'] = jekyll_fm['order']
            elif 'weight' in jekyll_fm:
                docusaurus_fm['sidebar_position'] = jekyll_fm['weight']
            
            # Image
            if 'image' in jekyll_fm:
                docusaurus_fm['image'] = jekyll_fm['image']
            
            # Cacher le TOC
            if 'toc' in jekyll_fm and not jekyll_fm['toc']:
                docusaurus_fm['hide_table_of_contents'] = True
            
            # Keywords
            if 'keywords' in jekyll_fm:
                docusaurus_fm['keywords'] = jekyll_fm['keywords']
            
            self._log(f"Front matter converti: {len(jekyll_fm)} → {len(docusaurus_fm)} champs")
            
            return docusaurus_fm, markdown_content
            
        except yaml.YAMLError as e:
            self._log(f"Erreur parsing YAML: {e}", "ERROR")
            return {}, content

    def _convert_links(self, content: str) -> str:
        """Convertit les liens Jekyll en liens Docusaurus"""
        for pattern, replacement in self.link_patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        return content

    def _convert_liquid_tags(self, content: str) -> str:
        """Convertit ou supprime les tags Liquid"""
        for pattern, replacement in self.liquid_patterns:
            if callable(replacement):
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
            else:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        return content

    def _convert_kramdown_syntax(self, content: str) -> str:
        """Convertit la syntaxe Kramdown spécifique"""
        for pattern, replacement in self.kramdown_patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        return content

    def _convert_admonitions(self, content: str) -> str:
        """Convertit les admonitions Jekyll en admonitions Docusaurus"""
        # Admonitions avec classes CSS
        admonition_patterns = [
            (r'<div class="alert alert-info">\s*<strong>([^<]+):</strong>\s*([^<]+)</div>', r':::info[\1]\n\2\n:::'),
            (r'<div class="alert alert-warning">\s*<strong>([^<]+):</strong>\s*([^<]+)</div>', r':::warning[\1]\n\2\n:::'),
            (r'<div class="alert alert-danger">\s*<strong>([^<]+):</strong>\s*([^<]+)</div>', r':::danger[\1]\n\2\n:::'),
            (r'<div class="alert alert-success">\s*<strong>([^<]+):</strong>\s*([^<]+)</div>', r':::tip[\1]\n\2\n:::'),
        ]
        
        for pattern, replacement in admonition_patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL | re.IGNORECASE)
        
        return content

    def _convert_tables(self, content: str) -> str:
        """Améliore le formatage des tableaux Markdown"""
        # Assure que les tableaux ont des espaces autour des pipes
        content = re.sub(r'\|([^|\n]+)\|', lambda m: '| ' + m.group(1).strip() + ' |', content)
        return content

    def _convert_toc(self, content: str) -> str:
        """Convertit les TOC Jekyll"""
        # Supprime les TOC manuels Jekyll (Docusaurus les génère automatiquement)
        patterns = [
            r'\*\s*TOC\s*\n\{:toc\}',
            r'\* TOC\n\{:toc\}',
            r'\{:toc\}'
        ]
        
        for pattern in patterns:
            content = re.sub(pattern, '<!-- TOC automatique généré par Docusaurus -->', content, flags=re.MULTILINE | re.IGNORECASE)
        
        return content

    def _clean_html_breaks(self, content: str) -> str:
        """Nettoie les balises HTML inutiles"""
        # Remplace les <br> multiples par des sauts de ligne Markdown
        content = re.sub(r'<br\s*/?>\s*<br\s*/?>', '\n\n', content, flags=re.IGNORECASE)
        content = re.sub(r'<br\s*/?>', '\n', content, flags=re.IGNORECASE)
        
        return content

    def _convert_math(self, content: str) -> str:
        """Convertit les formules mathématiques"""
        # Jekyll utilise souvent MathJax, Docusaurus aussi
        # Pas de conversion nécessaire généralement, mais on peut nettoyer
        return content

    def _convert_footnotes(self, content: str) -> str:
        """Nettoie les footnotes (supportées différemment)"""
        # Les footnotes Markdown standard fonctionnent dans Docusaurus
        return content

    def convert_file(self, input_file: Path, output_file: Path) -> bool:
        """Convertit un fichier Jekyll en Docusaurus"""
        try:
            self._log(f"Conversion: {input_file} → {output_file}")
            
            # Lecture du fichier
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Conversions étape par étape
            front_matter, markdown_content = self._convert_front_matter(content)
            
            # Conversions du contenu Markdown
            markdown_content = self._convert_links(markdown_content)
            markdown_content = self._convert_liquid_tags(markdown_content)
            markdown_content = self._convert_kramdown_syntax(markdown_content)
            markdown_content = self._convert_admonitions(markdown_content)
            markdown_content = self._convert_tables(markdown_content)
            markdown_content = self._convert_toc(markdown_content)
            markdown_content = self._clean_html_breaks(markdown_content)
            markdown_content = self._convert_math(markdown_content)
            markdown_content = self._convert_footnotes(markdown_content)
            
            # Reconstruction du fichier
            if front_matter:
                yaml_content = yaml.dump(front_matter, default_flow_style=False, allow_unicode=True)
                final_content = f"---\n{yaml_content}---\n\n{markdown_content}"
            else:
                final_content = markdown_content
            
            # Création du répertoire de sortie
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Écriture du fichier converti
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            # Statistiques de conversion
            changes_made = len(original_content) != len(final_content)
            self._log(f"✓ Converti: {input_file.name} ({'modifié' if changes_made else 'inchangé'})")
            
            return True
            
        except Exception as e:
            self._log(f"✗ Erreur conversion {input_file}: {e}", "ERROR")
            return False

    def convert_directory(self, input_subdir: str = "", output_subdir: str = "") -> Tuple[int, int]:
        """Convertit récursivement un répertoire"""
        input_path = self.input_dir / input_subdir if input_subdir else self.input_dir
        output_path = self.output_dir / output_subdir if output_subdir else self.output_dir
        
        success_count = 0
        total_count = 0
        
        if not input_path.exists():
            self._log(f"Répertoire source introuvable: {input_path}", "ERROR")
            return 0, 0
        
        # Parcours récursif
        for file_path in input_path.rglob("*.md"):
            if file_path.is_file():
                # Calcul du chemin relatif pour préserver la structure
                relative_path = file_path.relative_to(input_path)
                output_file = output_path / relative_path
                
                total_count += 1
                if self.convert_file(file_path, output_file):
                    success_count += 1
        
        return success_count, total_count

    def generate_report(self, output_file: str = None):
        """Génère un rapport de conversion"""
        report_content = [
            "# Rapport de conversion Jekyll → Docusaurus",
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Répertoire source: {self.input_dir}",
            f"Répertoire destination: {self.output_dir}",
            "",
            "## Log de conversion",
            ""
        ]
        
        report_content.extend(self.conversion_report)
        
        report_content.extend([
            "",
            "## Points à vérifier manuellement",
            "",
            "1. **Variables Liquid** : Rechercher 'TODO_CONVERT' dans les fichiers",
            "2. **Includes** : Convertir les includes en composants React",
            "3. **Boucles et conditions** : Remplacer la logique Liquid par du JSX",
            "4. **Links Jekyll** : Vérifier les liens TODO_CONVERT_LINK",
            "5. **Assets** : Déplacer les images vers static/img/",
            "6. **Configuration** : Adapter docusaurus.config.js",
            "7. **Admonitions** : Vérifier le formatage des admonitions converties",
            "8. **Code blocks** : Tester la coloration syntaxique",
            "9. **Front matter** : Vérifier les champs convertis",
            "10. **Liens internes** : Tester la navigation",
            "",
            "## Commandes de vérification",
            "",
            "```bash",
            "# Rechercher les TODO de conversion",
            "grep -r 'TODO_CONVERT' output/",
            "",
            "# Vérifier les liens cassés",
            "grep -r '{{.*}}' output/",
            "",
            "# Construire et tester",
            "npm run build",
            "npm run start",
            "```"
        ])
        
        report_text = "\n".join(report_content)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            self._log(f"Rapport sauvegardé: {output_file}")
        
        return report_text

def main():
    parser = argparse.ArgumentParser(description="Convertit les fichiers Jekyll en Docusaurus")
    parser.add_argument("input_dir", help="Répertoire source (Jekyll)")
    parser.add_argument("output_dir", help="Répertoire destination (Docusaurus)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Mode verbeux")
    parser.add_argument("-r", "--report", help="Fichier de rapport (optionnel)")
    
    args = parser.parse_args()
    
    # Validation des répertoires
    if not os.path.exists(args.input_dir):
        print(f"Erreur: Répertoire source '{args.input_dir}' introuvable")
        return 1
    
    # Création du convertisseur
    converter = JekyllToDocusaurusConverter(args.input_dir, args.output_dir, args.verbose)
    
    print(f"🚀 Début de la conversion Jekyll → Docusaurus")
    print(f"📁 Source: {args.input_dir}")
    print(f"📁 Destination: {args.output_dir}")
    print()
    
    # Conversion
    success, total = converter.convert_directory()
    
    # Rapport
    report_file = args.report or f"conversion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    converter.generate_report(report_file)
    
    # Résultats
    print()
    print(f"✅ Conversion terminée: {success}/{total} fichiers convertis")
    print(f"📊 Rapport: {report_file}")
    
    if success < total:
        print(f"⚠️  {total - success} fichiers ont eu des erreurs")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
