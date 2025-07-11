#!/usr/bin/env python3
"""
Script de test pour les tableaux
"""

import os
import re
import yaml
from pathlib import Path
from datetime import datetime

# Importer la classe
exec(open('/Users/rollandauda/Github/docusaurus/cav25/jekyll-to-docusaurus-simple.py').read())

# Créer le convertisseur
converter = JekyllToDocusaurusConverter()

# Contenu de test avec un tableau complexe
test_content = """---
title: Test tableau complexe
---

# Test de conversion de tableaux

## Tableau avec retours à la ligne dans les cellules

| Colonne A | Colonne B |
|-----------|-----------|
| Première ligne
avec du texte sur plusieurs
lignes ici | Deuxième colonne
aussi avec du texte
sur plusieurs lignes |
| Ligne 2 simple | Autre cellule
avec saut de ligne |
"""

print("Contenu original:")
print("-" * 40)
print(test_content)
print("-" * 40)

# Tester spécifiquement la conversion des tableaux
result = converter.convert_tables(test_content)

print("\nRésultat de la conversion des tableaux:")
print("-" * 40)
print(result)
print("-" * 40)

# Sauvegarder le résultat
with open('/Users/rollandauda/Github/docusaurus/cav25/test-tableau-result.md', 'w', encoding='utf-8') as f:
    f.write(result)

print("\n✅ Test terminé. Résultat sauvegardé dans test-tableau-result.md")
