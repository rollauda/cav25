#!/usr/bin/env python3
"""
Test direct de la conversion des tableaux
"""

import sys
import os
import re
import yaml
from pathlib import Path
from datetime import datetime

# Importer directement la classe du fichier
exec(open('/Users/rollandauda/Github/docusaurus/cav25/jekyll-to-docusaurus-simple.py').read())

# Lire le fichier de test
with open('/Users/rollandauda/Github/docusaurus/cav25/test-tableau-complexe.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Créer le convertisseur et appliquer la conversion
converter = JekyllToDocusaurusConverter()
result = converter.convert_full_content(content)

# Sauvegarder le résultat
with open('/Users/rollandauda/Github/docusaurus/cav25/test-tableau-complexe-result.md', 'w', encoding='utf-8') as f:
    f.write(result)

print("✅ Conversion terminée : test-tableau-complexe-result.md")
