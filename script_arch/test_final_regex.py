#!/usr/bin/env python3
import re

# Test de la regex pour les PDF embeds
test_content = '{% pdf "../../assets/pdf/ressources/vocabulaire-cinema.pdf" width=80% height=700px no_link %}'

print("Tests avec les bons échappements:")

patterns = [
    r'\{% pdf "([^"]+)" ([^%]+) %\}',              # Pattern simple avec échappement correct
    r'\{%\s*pdf\s+"([^"]+)"\s*([^%]*)\s*%\}',     # Pattern avec espaces flexibles
    r'\{%\s*pdf\s+"([^"]+\.pdf)"\s*([^}]*)\s*%\}', # En s'arrêtant avant }
]

for i, pattern in enumerate(patterns):
    match = re.search(pattern, test_content)
    print(f"Pattern {i+1}: {'✓' if match else '✗'}")
    print(f"  {pattern}")
    if match:
        print(f"  Path: '{match.group(1)}'")
        print(f"  Options: '{match.group(2)}'")
    print()

# Test du pattern final
final_pattern = r'\{%\s*pdf\s+"([^"]+\.pdf)"\s*([^%]*)\s*%\}'
match = re.search(final_pattern, test_content)
print(f"Pattern final: {final_pattern}")
print(f"Match: {'✓' if match else '✗'}")

if match:
    pdf_path = match.group(1).strip()
    options = match.group(2).strip()
    
    print(f"  Path: '{pdf_path}'")
    print(f"  Options: '{options}'")
    
    # Test des options
    width = "100%"
    height = "600px"
    
    if "width=" in options:
        width_match = re.search(r'width=([^\s]+)', options)
        if width_match:
            width = width_match.group(1)
            print(f"  Extracted width: '{width}'")
    
    if "height=" in options:
        height_match = re.search(r'height=([^\s]+)', options)
        if height_match:
            height = height_match.group(1)
            print(f"  Extracted height: '{height}'")
