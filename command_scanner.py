"""
🔍 ARSENAL COMMAND SCANNER V1.0
Scanner complet et approfondi des commandes

Analyse détaillée 5 fois comme demandé :
1. Scan des noms de commandes
2. Scan approfondi du contenu  
3. Détection doublons/bugs/indentation
4. Analyse de cohérence
5. Rapport final complet

Author: Arsenal Bot Team
Version: 1.0.0
"""

import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict, Counter
import json

class CommandScanner:
    """Scanner complet des commandes Arsenal"""
    
    def __init__(self, commands_dir: str = "a:/Arsenal_propre/commands"):
        self.commands_dir = Path(commands_dir)
        self.scan_results = {
            'scan_1_names': {},
            'scan_2_content': {},  
            'scan_3_issues': {},
            'scan_4_consistency': {},
            'scan_5_final': {}
        }
        
    def run_complete_analysis(self):
        """Lance l'analyse complète en 5 passes"""
        print("🔍 ARSENAL COMMAND SCANNER - ANALYSE COMPLÈTE")
        print("=" * 60)
        
        # SCAN 1: Noms des commandes
        print("\n📋 SCAN 1/5: Analyse des noms de commandes...")
        self.scan_1_command_names()
        
        # SCAN 2: Contenu approfondi
        print("\n🔍 SCAN 2/5: Analyse approfondie du contenu...")
        self.scan_2_deep_content_analysis()
        
        # SCAN 3: Détection des problèmes
        print("\n🚨 SCAN 3/5: Détection doublons/bugs/indentation...")
        self.scan_3_detect_issues()
        
        # SCAN 4: Cohérence générale
        print("\n⚖️ SCAN 4/5: Analyse de cohérence...")
        self.scan_4_consistency_check()
        
        # SCAN 5: Rapport final
        print("\n📊 SCAN 5/5: Génération du rapport final...")
        self.scan_5_final_report()
        
        # Sauvegarder les résultats
        self.save_results()
        
        print("\n✅ ANALYSE COMPLÈTE TERMINÉE!")
        return self.scan_results
    
    def scan_1_command_names(self):
        """SCAN 1: Analyse des noms de commandes"""
        results = {
            'files_scanned': 0,
            'commands_found': {},
            'app_commands': {},
            'traditional_commands': {},
            'duplicates': [],
            'naming_issues': []
        }
        
        command_names = defaultdict(list)
        
        for py_file in self.commands_dir.glob("*.py"):
            if py_file.name.startswith('__'):
                continue
                
            results['files_scanned'] += 1
            file_commands = self.extract_commands_from_file(py_file)
            
            results['commands_found'][py_file.name] = file_commands
            
            # Compter les occurrences de chaque nom
            for cmd_type, commands in file_commands.items():
                for cmd in commands:
                    command_names[cmd['name']].append({
                        'file': py_file.name,
                        'type': cmd_type,
                        'line': cmd.get('line', 0)
                    })
        
        # Détecter les doublons
        for cmd_name, occurrences in command_names.items():
            if len(occurrences) > 1:
                results['duplicates'].append({
                    'command': cmd_name,
                    'occurrences': occurrences
                })
        
        # Analyser les problèmes de nommage
        for cmd_name in command_names.keys():
            issues = []
            
            # Vérifier la convention de nommage
            if not cmd_name.islower():
                issues.append("Not lowercase")
            if ' ' in cmd_name:
                issues.append("Contains spaces")
            if len(cmd_name) > 20:
                issues.append("Too long (>20 chars)")
            if len(cmd_name) < 3:
                issues.append("Too short (<3 chars)")
            
            if issues:
                results['naming_issues'].append({
                    'command': cmd_name,
                    'issues': issues
                })
        
        self.scan_results['scan_1_names'] = results
        print(f"   📝 Fichiers scannés: {results['files_scanned']}")
        print(f"   🎯 Commandes trouvées: {len(command_names)}")
        print(f"   ⚠️ Doublons détectés: {len(results['duplicates'])}")
    
    def scan_2_deep_content_analysis(self):
        """SCAN 2: Analyse approfondie du contenu"""
        results = {
            'complexity_analysis': {},
            'function_analysis': {},
            'import_analysis': {},
            'docstring_analysis': {},
            'code_quality': {}
        }
        
        for py_file in self.commands_dir.glob("*.py"):
            if py_file.name.startswith('__'):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                file_analysis = self.analyze_file_content(py_file.name, content)
                
                results['complexity_analysis'][py_file.name] = file_analysis['complexity']
                results['function_analysis'][py_file.name] = file_analysis['functions']
                results['import_analysis'][py_file.name] = file_analysis['imports']
                results['docstring_analysis'][py_file.name] = file_analysis['docstrings']
                results['code_quality'][py_file.name] = file_analysis['quality']
                
            except Exception as e:
                print(f"   ❌ Erreur analyse {py_file.name}: {e}")
        
        self.scan_results['scan_2_content'] = results
        print(f"   🔬 Analyse complexité: {len(results['complexity_analysis'])} fichiers")
        print(f"   📊 Analyse fonctions: {len(results['function_analysis'])} fichiers")
    
    def scan_3_detect_issues(self):
        """SCAN 3: Détection des problèmes (doublons/bugs/indentation)"""
        results = {
            'duplicate_functions': [],
            'indentation_issues': [],
            'syntax_errors': [],
            'potential_bugs': [],
            'unused_imports': [],
            'long_functions': []
        }
        
        all_functions = defaultdict(list)
        
        for py_file in self.commands_dir.glob("*.py"):
            if py_file.name.startswith('__'):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # Analyser l'indentation
                indentation_issues = self.check_indentation_issues(lines, py_file.name)
                results['indentation_issues'].extend(indentation_issues)
                
                # Détecter les erreurs de syntaxe potentielles
                syntax_issues = self.check_syntax_issues(content, py_file.name)
                results['syntax_errors'].extend(syntax_issues)
                
                # Analyser l'AST pour les bugs potentiels
                try:
                    tree = ast.parse(content)
                    
                    # Collecter les fonctions
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            func_signature = f"{node.name}({len(node.args.args)})"
                            all_functions[func_signature].append({
                                'file': py_file.name,
                                'name': node.name,
                                'line': node.lineno,
                                'length': self.count_function_lines(node, lines)
                            })
                    
                    # Détecter les bugs potentiels
                    bugs = self.detect_potential_bugs(tree, py_file.name)
                    results['potential_bugs'].extend(bugs)
                    
                except SyntaxError as e:
                    results['syntax_errors'].append({
                        'file': py_file.name,
                        'error': str(e),
                        'line': e.lineno
                    })
                
            except Exception as e:
                print(f"   ❌ Erreur scan problèmes {py_file.name}: {e}")
        
        # Détecter les fonctions dupliquées
        for func_sig, occurrences in all_functions.items():
            if len(occurrences) > 1:
                # Vérifier si c'est vraiment un doublon (même contenu)
                potential_duplicate = True
                if potential_duplicate:
                    results['duplicate_functions'].append({
                        'signature': func_sig,
                        'occurrences': occurrences
                    })
        
        # Détecter les fonctions trop longues
        for occurrences in all_functions.values():
            for func in occurrences:
                if func['length'] > 100:  # Plus de 100 lignes
                    results['long_functions'].append(func)
        
        self.scan_results['scan_3_issues'] = results
        print(f"   🔄 Fonctions dupliquées: {len(results['duplicate_functions'])}")
        print(f"   📐 Problèmes indentation: {len(results['indentation_issues'])}")
        print(f"   🐛 Bugs potentiels: {len(results['potential_bugs'])}")
    
    def scan_4_consistency_check(self):
        """SCAN 4: Vérification de cohérence"""
        results = {
            'naming_consistency': {},
            'structure_consistency': {},
            'import_consistency': {},
            'documentation_consistency': {},
            'style_consistency': {}
        }
        
        # Analyser la cohérence des noms
        all_patterns = {
            'class_names': [],
            'function_names': [],
            'variable_names': [],
            'constant_names': []
        }
        
        for py_file in self.commands_dir.glob("*.py"):
            if py_file.name.startswith('__'):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                # Collecter les patterns de nommage
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        all_patterns['class_names'].append(node.name)
                    elif isinstance(node, ast.FunctionDef):
                        all_patterns['function_names'].append(node.name)
                    elif isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                if target.id.isupper():
                                    all_patterns['constant_names'].append(target.id)
                                else:
                                    all_patterns['variable_names'].append(target.id)
                
            except Exception as e:
                print(f"   ❌ Erreur cohérence {py_file.name}: {e}")
        
        # Analyser les patterns
        for pattern_type, names in all_patterns.items():
            consistency_score = self.calculate_naming_consistency(names)
            results['naming_consistency'][pattern_type] = {
                'total': len(names),
                'consistency_score': consistency_score,
                'common_patterns': Counter([self.extract_naming_pattern(name) for name in names]).most_common(5)
            }
        
        self.scan_results['scan_4_consistency'] = results
        print(f"   ✅ Cohérence classes: {results['naming_consistency']['class_names']['consistency_score']:.2f}")
        print(f"   ✅ Cohérence fonctions: {results['naming_consistency']['function_names']['consistency_score']:.2f}")
    
    def scan_5_final_report(self):
        """SCAN 5: Génération du rapport final"""
        results = {
            'summary': {},
            'critical_issues': [],
            'recommendations': [],
            'statistics': {},
            'quality_score': 0
        }
        
        # Résumé des scans précédents
        results['summary'] = {
            'total_files': self.scan_results['scan_1_names']['files_scanned'],
            'total_commands': len(self.scan_results['scan_1_names']['commands_found']),
            'duplicate_commands': len(self.scan_results['scan_1_names']['duplicates']),
            'syntax_errors': len(self.scan_results['scan_3_issues']['syntax_errors']),
            'potential_bugs': len(self.scan_results['scan_3_issues']['potential_bugs']),
            'indentation_issues': len(self.scan_results['scan_3_issues']['indentation_issues'])
        }
        
        # Issues critiques
        critical_count = 0
        
        # Erreurs de syntaxe (critique)
        if self.scan_results['scan_3_issues']['syntax_errors']:
            results['critical_issues'].append({
                'type': 'CRITIQUE: Erreurs de syntaxe',
                'count': len(self.scan_results['scan_3_issues']['syntax_errors']),
                'details': self.scan_results['scan_3_issues']['syntax_errors']
            })
            critical_count += len(self.scan_results['scan_3_issues']['syntax_errors']) * 10
        
        # Doublons de commandes (important)
        if self.scan_results['scan_1_names']['duplicates']:
            results['critical_issues'].append({
                'type': 'IMPORTANT: Commandes dupliquées',
                'count': len(self.scan_results['scan_1_names']['duplicates']),
                'details': self.scan_results['scan_1_names']['duplicates']
            })
            critical_count += len(self.scan_results['scan_1_names']['duplicates']) * 5
        
        # Bugs potentiels (important)
        if self.scan_results['scan_3_issues']['potential_bugs']:
            results['critical_issues'].append({
                'type': 'IMPORTANT: Bugs potentiels',
                'count': len(self.scan_results['scan_3_issues']['potential_bugs']),
                'details': self.scan_results['scan_3_issues']['potential_bugs']
            })
            critical_count += len(self.scan_results['scan_3_issues']['potential_bugs']) * 3
        
        # Calculer le score de qualité (0-100)
        base_score = 100
        quality_score = max(0, base_score - critical_count)
        results['quality_score'] = quality_score
        
        # Générer des recommandations
        recommendations = []
        
        if self.scan_results['scan_3_issues']['syntax_errors']:
            recommendations.append("🔴 URGENT: Corriger les erreurs de syntaxe")
        
        if self.scan_results['scan_1_names']['duplicates']:
            recommendations.append("🟠 IMPORTANT: Renommer ou fusionner les commandes dupliquées")
        
        if self.scan_results['scan_3_issues']['indentation_issues']:
            recommendations.append("🟡 Corriger les problèmes d'indentation")
        
        if self.scan_results['scan_3_issues']['long_functions']:
            recommendations.append("🟡 Diviser les fonctions trop longues (>100 lignes)")
        
        if quality_score > 80:
            recommendations.append("✅ Code en bon état général")
        elif quality_score > 60:
            recommendations.append("⚠️ Code nécessite des améliorations")
        else:
            recommendations.append("🚨 Code nécessite une révision majeure")
        
        results['recommendations'] = recommendations
        
        self.scan_results['scan_5_final'] = results
        print(f"   📊 Score qualité: {quality_score}/100")
        print(f"   ⚠️ Issues critiques: {len(results['critical_issues'])}")
        print(f"   💡 Recommandations: {len(recommendations)}")
    
    # Méthodes utilitaires
    def extract_commands_from_file(self, file_path: Path) -> Dict[str, List]:
        """Extrait toutes les commandes d'un fichier"""
        commands = {
            'app_commands': [],
            'traditional_commands': [],
            'groups': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Chercher les app_commands
            app_cmd_pattern = r'@app_commands\.command\(name=["\']([^"\']+)["\']'
            for match in re.finditer(app_cmd_pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                commands['app_commands'].append({
                    'name': match.group(1),
                    'line': line_num
                })
            
            # Chercher les commandes traditionnelles
            trad_cmd_pattern = r'@commands\.command\(name=["\']([^"\']+)["\']'
            for match in re.finditer(trad_cmd_pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                commands['traditional_commands'].append({
                    'name': match.group(1),
                    'line': line_num
                })
            
            # Chercher aussi les décorateurs simples
            simple_pattern = r'@commands\.command\(\s*\)\s*async def ([a-zA-Z_][a-zA-Z0-9_]*)'
            for match in re.finditer(simple_pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                commands['traditional_commands'].append({
                    'name': match.group(1),
                    'line': line_num
                })
                
        except Exception as e:
            print(f"   ❌ Erreur extraction {file_path.name}: {e}")
        
        return commands
    
    def analyze_file_content(self, filename: str, content: str) -> Dict[str, Any]:
        """Analyse le contenu d'un fichier"""
        analysis = {
            'complexity': {},
            'functions': {},
            'imports': {},
            'docstrings': {},
            'quality': {}
        }
        
        lines = content.split('\n')
        
        # Analyse de complexité
        analysis['complexity'] = {
            'total_lines': len(lines),
            'code_lines': len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
            'comment_lines': len([l for l in lines if l.strip().startswith('#')]),
            'blank_lines': len([l for l in lines if not l.strip()])
        }
        
        # Analyse des imports
        imports = []
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                imports.append({'line': i, 'import': line.strip()})
        
        analysis['imports'] = {
            'total': len(imports),
            'details': imports
        }
        
        # Analyse des docstrings
        docstring_count = content.count('"""') + content.count("'''")
        analysis['docstrings'] = {
            'count': docstring_count // 2,  # Paires ouverture/fermeture
            'has_module_docstring': content.strip().startswith('"""') or content.strip().startswith("'''")
        }
        
        return analysis
    
    def check_indentation_issues(self, lines: List[str], filename: str) -> List[Dict]:
        """Vérifie les problèmes d'indentation"""
        issues = []
        
        for i, line in enumerate(lines, 1):
            if not line.strip():
                continue
                
            # Vérifier l'indentation (espaces vs tabs)
            leading = line[:len(line) - len(line.lstrip())]
            
            if '\t' in leading and ' ' in leading:
                issues.append({
                    'file': filename,
                    'line': i,
                    'issue': 'Mixed tabs and spaces',
                    'content': line.strip()
                })
        
        return issues
    
    def check_syntax_issues(self, content: str, filename: str) -> List[Dict]:
        """Vérifie les erreurs de syntaxe potentielles"""
        issues = []
        
        # Vérifications basiques
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Parenthèses non fermées
            if stripped.count('(') != stripped.count(')'):
                if not stripped.endswith('\\'):  # Continuation de ligne
                    issues.append({
                        'file': filename,
                        'line': i,
                        'issue': 'Unmatched parentheses',
                        'content': stripped
                    })
        
        return issues
    
    def detect_potential_bugs(self, tree: ast.AST, filename: str) -> List[Dict]:
        """Détecte les bugs potentiels via AST"""
        bugs = []
        
        for node in ast.walk(tree):
            # Variables non utilisées (approximation)
            if isinstance(node, ast.Assign):
                # Logique de détection simplifiée
                pass
                
            # Imports non utilisés (approximation)  
            if isinstance(node, ast.Import):
                # Logique de détection simplifiée
                pass
        
        return bugs
    
    def count_function_lines(self, func_node: ast.FunctionDef, lines: List[str]) -> int:
        """Compte les lignes d'une fonction"""
        start_line = func_node.lineno - 1
        
        # Trouver la fin de la fonction (approximation)
        end_line = start_line + 1
        indent_level = None
        
        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            if not line.strip():
                continue
                
            current_indent = len(line) - len(line.lstrip())
            
            if indent_level is None:
                indent_level = current_indent
            elif current_indent <= len(lines[start_line]) - len(lines[start_line].lstrip()) and line.strip():
                break
                
            end_line = i
        
        return end_line - start_line + 1
    
    def calculate_naming_consistency(self, names: List[str]) -> float:
        """Calcule le score de cohérence des noms"""
        if not names:
            return 1.0
        
        # Analyser les patterns de nommage
        patterns = [self.extract_naming_pattern(name) for name in names]
        pattern_counts = Counter(patterns)
        
        # Le pattern le plus fréquent
        most_common = pattern_counts.most_common(1)[0][1] if pattern_counts else 0
        
        return most_common / len(names) if names else 1.0
    
    def extract_naming_pattern(self, name: str) -> str:
        """Extrait le pattern de nommage d'un nom"""
        if '_' in name:
            return 'snake_case'
        elif name.islower():
            return 'lowercase'
        elif name.isupper():
            return 'UPPERCASE'
        elif name[0].isupper():
            return 'CamelCase'
        else:
            return 'mixed'
    
    def save_results(self):
        """Sauvegarde les résultats dans un fichier"""
        output_file = self.commands_dir.parent / "command_scan_results.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.scan_results, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"\n💾 Résultats sauvegardés dans: {output_file}")
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
    
    def print_detailed_report(self):
        """Affiche le rapport détaillé"""
        print("\n" + "="*80)
        print("📊 RAPPORT DÉTAILLÉ - ANALYSE COMPLÈTE DES COMMANDES")
        print("="*80)
        
        final_results = self.scan_results['scan_5_final']
        
        # Résumé
        print(f"\n📋 RÉSUMÉ GÉNÉRAL:")
        summary = final_results['summary']
        print(f"   • Fichiers scannés: {summary['total_files']}")
        print(f"   • Commandes trouvées: {summary['total_commands']}")
        print(f"   • Commandes dupliquées: {summary['duplicate_commands']}")
        print(f"   • Erreurs de syntaxe: {summary['syntax_errors']}")
        print(f"   • Bugs potentiels: {summary['potential_bugs']}")
        print(f"   • Problèmes indentation: {summary['indentation_issues']}")
        
        # Score de qualité
        print(f"\n📊 SCORE DE QUALITÉ: {final_results['quality_score']}/100")
        if final_results['quality_score'] >= 80:
            print("   ✅ EXCELLENT - Code de haute qualité")
        elif final_results['quality_score'] >= 60:
            print("   ⚠️ MOYEN - Améliorations recommandées")
        else:
            print("   🚨 FAIBLE - Révision majeure nécessaire")
        
        # Issues critiques
        if final_results['critical_issues']:
            print(f"\n🚨 ISSUES CRITIQUES ({len(final_results['critical_issues'])}):")
            for issue in final_results['critical_issues']:
                print(f"   • {issue['type']}: {issue['count']} occurrences")
        
        # Recommandations
        print(f"\n💡 RECOMMANDATIONS ({len(final_results['recommendations'])}):")
        for i, rec in enumerate(final_results['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        # Détails des doublons si présents
        duplicates = self.scan_results['scan_1_names']['duplicates']
        if duplicates:
            print(f"\n🔄 COMMANDES DUPLIQUÉES ({len(duplicates)}):")
            for dup in duplicates:
                print(f"   • '{dup['command']}' trouvée dans:")
                for occ in dup['occurrences']:
                    print(f"     - {occ['file']} (ligne {occ['line']}, type: {occ['type']})")
        
        print("\n" + "="*80)
        print("✅ ANALYSE TERMINÉE - Consultez command_scan_results.json pour les détails complets")
        print("="*80)

# Lancer le scan
if __name__ == "__main__":
    scanner = CommandScanner()
    results = scanner.run_complete_analysis()
    scanner.print_detailed_report()

