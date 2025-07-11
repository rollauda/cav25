#!/usr/bin/env python3
"""
Test simple pour la conversion des tableaux sans en-tête
"""

import re

def convert_simple_table(content):
    """Convertit un tableau simple sans en-tête vers Docusaurus"""
    
    # Rechercher les tableaux avec une seule ligne
    simple_table_pattern = r'^\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|$'
    
    if re.search(simple_table_pattern, content, re.MULTILINE):
        def replace_simple_table(match):
            cell1 = match.group(1).strip()
            cell2 = match.group(2).strip()
            
            # Convertir en tableau Markdown propre SANS en-tête
            return f"""| {cell1} | {cell2} |
|----------|----------|"""
        
        content = re.sub(simple_table_pattern, replace_simple_table, content, flags=re.MULTILINE)
        print("✓ Tableau simple converti")
    
    return content

# Test
test_input = """---
title: Test
---

## Titre

| Texte long ici | <img src="/assets/img/image.png" /> |

Autre contenu...
"""

print("AVANT:")
print(test_input)
print("\nAPRÈS:")
result = convert_simple_table(test_input)
print(result)
