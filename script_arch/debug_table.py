#!/usr/bin/env python3
"""
Script de debug pour les tableaux
"""

# Test avec la vraie structure du fichier
test_content = """---
title: Test Tableaux
---

## Test tableau avec retours à la ligne

|**Plan de la leçon**     | **Introduction : le problème de l'identité personnelle  
1. Je suis une chose qui pense  
2. Le Moi est introuvable  
3. Je est un autre   
 Conclusion : Qu'est-ce que penser ?** | 
| Perspective           | 1. L'existence et la culture / 3. La connaissance | 
| Notion principale |`CONSCIENCE`, `INCONSCIENT`  | 
|  Notions secondaires | *`Vérité`, `Raison`, `Nature`* |   
| Repères           | `Identité/Égalité/Différence` -  `Médiat/Immédiat` | 
| Méthode           | L'explication de texte     |
| Auteurs étudiés         | Plutarque, R. Descartes, B. Pascal, S. Freud  |
| **Travaux**             | **- Reprendre dans un carnet les définitions du cours à retenir**.   
 **- Écrire une courte synthèse de la leçon lorsqu'elle est terminée (vous pourrez être interrogés au début de la leçon suivante)** : Qu'est-ce que j'ai retenu ? (*Je note les idées-clés que je retiens de la leçon, les thèses des auteurs lus ou les questions qu'ils posent*)   
 **- Exercice** : analyser un texte philosophique en vue d'une explication |
"""

def debug_table_structure():
    """Analyse la structure du tableau pour comprendre le problème"""
    
    # Extraire juste le tableau
    lines = test_content.split('\n')
    table_lines = []
    in_table = False
    
    for line in lines:
        if '|' in line:
            in_table = True
            table_lines.append(line)
        elif in_table and line.strip():
            # Ligne qui suit une ligne de tableau
            table_lines.append(line)
        elif in_table and not line.strip():
            # Ligne vide = fin du tableau
            break
    
    print("=== STRUCTURE DU TABLEAU ===")
    for i, line in enumerate(table_lines):
        print(f"{i:2d}: '{line}'")
    
    print("\n=== ANALYSE ===")
    
    # Analyser chaque ligne
    for i, line in enumerate(table_lines):
        line = line.strip()
        if line.startswith('|'):
            if line.endswith('|'):
                print(f"Ligne {i}: Complète - {line.count('|')-1} cellules")
            else:
                print(f"Ligne {i}: Incomplète - commence par |")
        else:
            print(f"Ligne {i}: Continuation - '{line}'")

def simple_table_fix():
    """Approche simplifiée pour reconstruire le tableau"""
    
    # Extraire juste le tableau
    lines = test_content.split('\n')
    table_lines = []
    in_table = False
    
    for line in lines:
        if '|' in line:
            in_table = True
            table_lines.append(line)
        elif in_table and line.strip():
            table_lines.append(line)
        elif in_table and not line.strip():
            break
    
    print("\n=== RECONSTRUCTION SIMPLIFIÉE ===")
    
    # Reconstruire ligne par ligne
    rows = []
    current_row = None
    
    for line in table_lines:
        line = line.strip()
        
        if line.startswith('|'):
            # Nouvelle ligne de tableau
            if current_row is not None:
                # Sauvegarder la ligne précédente
                rows.append(current_row)
            
            # Commencer une nouvelle ligne
            current_row = line
            
            # Si la ligne se termine par |, elle est complète
            if line.endswith('|'):
                rows.append(current_row)
                current_row = None
        else:
            # Ligne de continuation
            if current_row is not None:
                # Ajouter le contenu à la ligne en cours
                if current_row.endswith('|'):
                    # Insérer avant le | final
                    current_row = current_row[:-1] + ' <br /> ' + line + '|'
                else:
                    # Ajouter simplement
                    current_row += ' <br /> ' + line
    
    # Ajouter la dernière ligne
    if current_row is not None:
        rows.append(current_row)
    
    print("Lignes reconstruites :")
    for i, row in enumerate(rows):
        print(f"{i}: {row}")
    
    # Maintenant convertir en Markdown propre
    print("\n=== CONVERSION MARKDOWN ===")
    
    final_rows = []
    for row in rows:
        if row.startswith('|') and row.endswith('|'):
            # Extraire les cellules
            content = row[1:-1]  # Supprimer | début et fin
            cells = [cell.strip() for cell in content.split('|')]
            final_rows.append(cells)
    
    if final_rows:
        # Déterminer le nombre de colonnes
        max_cols = max(len(row) for row in final_rows)
        
        # Construire le tableau final
        result = []
        for i, row in enumerate(final_rows):
            # Compléter avec des cellules vides
            while len(row) < max_cols:
                row.append('')
            
            # Construire la ligne
            line = '| ' + ' | '.join(row) + ' |'
            result.append(line)
            
            # Ajouter la ligne de séparation après l'en-tête
            if i == 0:
                sep_parts = [' -------------------- ' for _ in range(max_cols)]
                separator = '|' + '|'.join(sep_parts) + '|'
                result.append(separator)
        
        print("Tableau final :")
        for line in result:
            print(line)

if __name__ == '__main__':
    debug_table_structure()
    simple_table_fix()
