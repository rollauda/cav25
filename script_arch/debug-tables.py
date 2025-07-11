#!/usr/bin/env python3
"""
Test debug pour la fonction convert_tables
"""

import re

def debug_convert_tables(content):
    """Debug de la fonction convert_tables"""
    
    print("=== DEBUG CONVERT_TABLES ===")
    print(f"Contenu d'entrée (extrait) :")
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '|' in line:
            print(f"Ligne {i}: '{line}'")
    
    print("\n=== DÉTECTION DES TABLEAUX ===")
    
    result_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Détecter une ligne de tableau (commence et finit par |)
        if line.startswith('|') and line.endswith('|') and '|' in line[1:-1]:
            print(f"✓ Ligne de tableau détectée : '{line}'")
            
            # C'est une ligne de tableau
            table_lines = [lines[i]]  # Commencer avec la ligne actuelle
            j = i + 1
            
            # Chercher les lignes suivantes qui font partie du tableau
            while j < len(lines):
                next_line = lines[j].strip()
                
                # Si la ligne suivante est aussi une ligne de tableau
                if next_line.startswith('|') and next_line.endswith('|') and '|' in next_line[1:-1]:
                    table_lines.append(lines[j])
                    j += 1
                # Si c'est une ligne vide, on continue à chercher
                elif not next_line:
                    j += 1
                    break
                else:
                    # Fin du tableau
                    break
            
            print(f"Table détectée avec {len(table_lines)} lignes")
            
            # Traiter le tableau détecté
            if len(table_lines) == 1:
                # Tableau Jekyll à une seule ligne - ajouter la ligne de séparation
                table_line = table_lines[0]
                
                # Compter le nombre de colonnes
                cells = table_line.split('|')[1:-1]  # Exclure les | du début et de la fin
                num_columns = len(cells)
                
                print(f"🔧 Tableau à une ligne avec {num_columns} colonnes - ajout de séparateur")
                
                # Ajouter la ligne de tableau
                result_lines.append(table_line)
                
                # Ajouter la ligne de séparation obligatoire pour Docusaurus
                separator_parts = ['----------' for _ in range(num_columns)]
                separator = '|' + '|'.join(separator_parts) + '|'
                result_lines.append(separator)
                
                print(f"✅ Séparateur ajouté : '{separator}'")
            else:
                # Tableau multi-lignes - l'ajouter tel quel
                result_lines.extend(table_lines)
                print(f"📋 Tableau multi-lignes conservé tel quel")
            
            # Continuer après le tableau
            i = j
        else:
            # Ligne normale
            result_lines.append(lines[i])
            i += 1
    
    print("\n=== RÉSULTAT ===")
    result = '\n'.join(result_lines)
    result_lines_final = result.split('\n')
    for i, line in enumerate(result_lines_final):
        if '|' in line:
            print(f"Ligne {i}: '{line}'")
    
    return result

# Test avec le fichier
with open('convert-md/input.md', 'r', encoding='utf-8') as f:
    content = f.read()

result = debug_convert_tables(content)

print("\n=== DIFFÉRENCE ===")
if result != content:
    print("✅ Contenu modifié")
else:
    print("❌ Aucune modification")
