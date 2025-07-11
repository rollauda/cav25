#!/usr/bin/env python3
import re

# Test de la regex pour les PDF embeds
test_content = '{% pdf "../../assets/pdf/ressources/vocabulaire-cinema.pdf" width=80% height=700px no_link %}'

print("Analyse caractère par caractère:")
for i, char in enumerate(test_content):
    print(f"{i:2d}: '{char}' (ASCII: {ord(char)})")

print("\n" + "="*50)

# Regex étape par étape
patterns = [
    r'\{%',                                        # Début
    r'\{%\s*pdf',                                 # {% pdf
    r'\{%\s*pdf\s+',                              # {% pdf + espace(s)
    r'\{%\s*pdf\s+"',                             # {% pdf + espace(s) + "
    r'\{%\s*pdf\s+"[^"]+\.pdf"',                  # {% pdf "path.pdf"
    r'\{%\s*pdf\s+"[^"]+\.pdf"\s*[^%]*%}',        # Tout le pattern
]

for i, pattern in enumerate(patterns):
    match = re.search(pattern, test_content)
    print(f"Étape {i+1}: {pattern:<40} -> {'✓' if match else '✗'}")
    if match:
        print(f"         Match: '{match.group(0)}'")

print("\n" + "="*50)

# Essayons une regex simple et robuste
simple_pattern = r'\{% pdf "([^"]+)" ([^%]+) %\}'
match = re.search(simple_pattern, test_content)
print(f"Pattern simple: {simple_pattern}")
print(f"Match: {'✓' if match else '✗'}")

if match:
    print(f"  Path: {repr(match.group(1))}")
    print(f"  Options: {repr(match.group(2))}")
