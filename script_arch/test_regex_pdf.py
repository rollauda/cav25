#!/usr/bin/env python3
import re

# Test de la regex pour les PDF embeds
test_content = '{% pdf "../../assets/pdf/ressources/vocabulaire-cinema.pdf" width=80% height=700px no_link %}'

# Notre regex corrigée
pdf_pattern = r'\{\%\s*pdf\s+[\'\"]*([^\'\"]+?\.pdf)[\'\"]*([^%]*)\%\}'

match = re.search(pdf_pattern, test_content)

print("Contenu de test:")
print(test_content)
print("\nRegex pattern:")
print(pdf_pattern)
print("\nMatch found:", match is not None)

if match:
    print("Group 1 (path):", repr(match.group(1)))
    print("Group 2 (options):", repr(match.group(2)))
else:
    print("Aucun match trouvé!")

# Testons différentes variations de la regex
patterns_to_test = [
    r'\{\%\s*pdf\s+"([^"]+)"([^%]*)\%\}',  # Avec guillemets obligatoires
    r'\{\%\s*pdf\s+[\'\"]*([^\'\"]+\.pdf)[\'\"]*([^%]*)\%\}',  # Notre version
    r'\{\%\s*pdf\s+[\'\"]*([^\s\'\"]+\.pdf)[\'\"]*([^%]*)\%\}',  # Pas d'espaces dans le path
]

for i, pattern in enumerate(patterns_to_test):
    match = re.search(pattern, test_content)
    print(f"\nPattern {i+1}: {'✓' if match else '✗'}")
    if match:
        print(f"  Path: {repr(match.group(1))}")
        print(f"  Options: {repr(match.group(2))}")
