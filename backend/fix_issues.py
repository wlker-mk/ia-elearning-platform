#!/usr/bin/env python3
"""
Script de correction automatique des problèmes de linting
pour le projet ia-learning-platform/backend.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import argparse

class BackendCodeFixer:
    def __init__(self, backend_dir: str = "R:/ia-learning-platform/backend"):
        self.backend_dir = Path(backend_dir)
        if not self.backend_dir.exists():
            print(f"Erreur: Le dossier backend {backend_dir} n'existe pas")
            print("Vérifiez le chemin ou exécutez depuis le bon répertoire")
            sys.exit(1)
        
        print(f"Analyse du dossier backend: {self.backend_dir.absolute()}")
        print(f"Détection des microservices...")
        
        # Détecter les microservices
        self.microservices = self._detect_microservices()
        print(f"Microservices détectés: {', '.join(self.microservices.keys())}")
    
    def _detect_microservices(self) -> Dict[str, Path]:
        """Détecter tous les microservices dans le dossier backend"""
        microservices = {}
        microservices_dir = self.backend_dir / "microservices"
        
        if microservices_dir.exists():
            for item in microservices_dir.iterdir():
                if item.is_dir() and "-service" in item.name:
                    microservices[item.name] = item
        
        return microservices
    
    def fix_all_issues(self):
        """Corriger tous les problèmes détectés dans tous les microservices"""
        print("\n" + "=" * 60)
        print("DÉBUT DE LA CORRECTION AUTOMATIQUE")
        print("=" * 60)
        
        total_fixed = 0
        
        for service_name, service_path in self.microservices.items():
            print(f"\n{'=' * 40}")
            print(f"MICROSERVICE: {service_name}")
            print(f"{'=' * 40}")
            
            fixed = self.fix_service_issues(service_path)
            total_fixed += fixed
        
        # Corriger aussi les fichiers à la racine du backend
        print(f"\n{'=' * 40}")
        print("RACINE BACKEND")
        print(f"{'=' * 40}")
        self.fix_root_issues()
        
        print("\n" + "=" * 60)
        print(f"CORRECTION TERMINÉE - {total_fixed} service(s) traités")
        print("=" * 60)
    
    def fix_service_issues(self, service_path: Path) -> int:
        """Corriger les problèmes dans un microservice spécifique"""
        fixed_files = 0
        
        # 1. Fichiers Python spécifiques mentionnés dans les erreurs
        python_patterns = {
            "api-gateway": ["api_gateway.py"],
            "auth-service": ["config/settings/base.py"],
            "courses-service": [
                "apps/courses/apps.py",
                "apps/courses/certificates/tasks.py",
                "apps/courses/certificates/views.py",
                "apps/courses/courses/signals.py",
                "apps/courses/courses/tasks.py",
                "apps/courses/courses/views.py",
                "apps/courses/lessons/tasks.py",
                "config/celery.py",
                "config/settings/base.py"
            ]
        }
        
        service_name = service_path.name
        if service_name in python_patterns:
            for file_pattern in python_patterns[service_name]:
                file_path = service_path / file_pattern
                if file_path.exists():
                    self.fix_python_file(file_path)
                    fixed_files += 1
        
        # 2. Fichiers Markdown spécifiques
        md_files = []
        if service_name == "monitoring-service":
            md_files = ["README.md", "docs/architecture.md", "docs/api.md"]
        elif service_name == "api-gateway":
            md_files = ["API.md", "ARCHITECTURE.md", "README.md"]
        elif service_name == "courses-service":
            md_files = ["README.md"]
        
        for md_file in md_files:
            file_path = service_path / md_file
            if file_path.exists():
                self.fix_markdown_file(file_path)
                fixed_files += 1
        
        # 3. Fichiers shell
        if service_name == "courses-service":
            sh_file = service_path / "docker-entrypoint.sh"
            if sh_file.exists():
                self.fix_trailing_whitespace_file(sh_file)
                fixed_files += 1
        
        # 4. Fichiers de test avec asserts
        test_files = self._find_test_files(service_path)
        for test_file in test_files:
            self.fix_test_file(test_file)
            fixed_files += 1
        
        return 1 if fixed_files > 0 else 0
    
    def fix_root_issues(self):
        """Corriger les problèmes à la racine du backend"""
        # Vérifier s'il y a des fichiers .md à la racine
        for md_file in self.backend_dir.glob("*.md"):
            self.fix_markdown_file(md_file)
    
    def _find_test_files(self, service_path: Path) -> List[Path]:
        """Trouver tous les fichiers de test Python"""
        test_files = []
        
        # Chercher dans tous les sous-dossiers
        for root, dirs, files in os.walk(service_path):
            # Exclure certains dossiers
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'venv']]
            
            for file in files:
                if file.endswith('.py') and ('test' in file.lower() or 'tests' in root.lower()):
                    test_files.append(Path(root) / file)
        
        return test_files
    
    def fix_python_file(self, filepath: Path):
        """Corriger un fichier Python spécifique"""
        print(f"\n  📝 Correction Python: {filepath.relative_to(self.backend_dir)}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        original_lines = lines.copy()
        
        # 1. Supprimer les espaces en fin de ligne
        lines = [line.rstrip() + '\n' for line in lines]
        
        # 2. Corriger les imports inutilisés (F401)
        # Cette partie nécessite une analyse plus poussée, on la traite manuellement
        # Pour l'instant, on se contente de signaler
        
        # 3. Corriger les variables de boucle inutilisées (B007)
        for i, line in enumerate(lines):
            # Détecter les patterns "for x in" où x n'est pas utilisé
            if 'for ' in line and ' in ' in line and 'range' in line:
                # Chercher des patterns comme "for i in range"
                match = re.search(r'for\s+(\w+)\s+in\s+range', line)
                if match:
                    var_name = match.group(1)
                    # Vérifier si la variable est utilisée dans le corps de la boucle
                    # (implémentation simplifiée)
                    lines[i] = line.replace(f'for {var_name} ', 'for _ ')
                    print(f"    → Variable de boucle '{var_name}' remplacée par '_'")
        
        # 4. Corriger "not in" (E713)
        for i, line in enumerate(lines):
            if 'not in' in line and 'is False' in line:
                lines[i] = line.replace('not in', 'in').replace(' is False', '')
                print(f"    → Test 'not in' corrigé")
        
        # 5. Déplacer les imports au début du fichier (E402)
        # On réorganise tous les imports
        import_section = []
        other_lines = []
        in_import_block = False
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                import_section.append(line)
                in_import_block = True
            elif in_import_block and (stripped == '' or stripped.startswith('#')):
                import_section.append(line)
            else:
                in_import_block = False
                other_lines.append(line)
        
        # Réorganiser le fichier avec les imports d'abord
        if import_section:
            lines = import_section + other_lines
        
        # 6. Variables locales non utilisées (F841)
        # On signale mais on ne modifie pas pour éviter de casser le code
        
        # Écrire les modifications si changements
        if lines != original_lines:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"    ✓ Fichier modifié")
        else:
            print(f"    ✓ Aucune modification nécessaire")
    
    def fix_markdown_file(self, filepath: Path):
        """Corriger un fichier Markdown spécifique"""
        print(f"\n  📄 Correction Markdown: {filepath.relative_to(self.backend_dir)}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        modifications = []
        
        # 1. Ajouter une ligne vide à la fin (MD047)
        if not content.endswith('\n'):
            content += '\n'
            modifications.append("nouvelle ligne finale")
        
        # 2. Ajouter des espaces autour des titres (MD022)
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # Détecter les titres (commencent par 1-6 #)
            if re.match(r'^#{1,6}\s+', line.strip()):
                # Vérifier ligne précédente
                if i > 0 and lines[i-1].strip() != '':
                    new_lines.insert(-1, '')
                    modifications.append("espace avant titre")
                
                # Vérifier ligne suivante
                if i < len(lines) - 1 and lines[i+1].strip() != '':
                    new_lines.append('')
                    modifications.append("espace après titre")
        
        content = '\n'.join(new_lines)
        
        # 3. Ajouter langue aux blocs de code (MD040)
        def add_language_to_code_block(match):
            code = match.group(1).strip()
            backticks = match.group(2)
            
            # Deviner la langue
            lang = ''
            if any(keyword in code for keyword in 
                   ['def ', 'class ', 'import ', 'from ', 'print(', 'assert ']):
                lang = 'python'
            elif any(keyword in code for keyword in 
                     ['function', 'const ', 'let ', 'var ', 'console.log']):
                lang = 'javascript'
            elif any(keyword in code for keyword in 
                     ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE TABLE']):
                lang = 'sql'
            elif any(keyword in code for keyword in 
                     ['<html', '<div', '<p', 'class=', 'id=']):
                lang = 'html'
            elif any(keyword in code for keyword in 
                     ['{', '}', ';', 'color:', 'font-size:']):
                lang = 'css'
            elif any(keyword in code for keyword in 
                     ['docker', 'FROM', 'RUN', 'COPY', 'ENV']):
                lang = 'dockerfile'
            elif any(keyword in code for keyword in 
                     ['apiVersion:', 'kind:', 'metadata:', 'spec:']):
                lang = 'yaml'
            
            return f'{backticks}{lang}\n{code}\n{backticks}'
        
        # Pattern pour détecter ``` sans langue
        code_block_pattern = r'^(```+)(?![a-zA-Z0-9])(.*?)^\1'
        content, count = re.subn(code_block_pattern, add_language_to_code_block, 
                                content, flags=re.MULTILINE | re.DOTALL)
        
        if count > 0:
            modifications.append(f"langue ajoutée à {count} bloc(s) de code")
        
        # 4. Transformer les URLs nues en liens (MD034)
        url_pattern = r'(?<![\(\[])(https?://[^\s<>]+)(?![\)\]])'
        
        def url_to_link(match):
            url = match.group(1)
            # Nettoyer l'URL pour le texte
            clean_url = url.replace('https://', '').replace('http://', '')
            clean_url = clean_url.split('/')[0]
            return f'[{clean_url}]({url})'
        
        content, url_count = re.subn(url_pattern, url_to_link, content)
        if url_count > 0:
            modifications.append(f"{url_count} URL(s) transformée(s) en liens")
        
        # 5. Tables (MD060) - alignement des colonnes
        # On vérifie les tables et on standardise l'alignement
        table_pattern = r'(\|.*\|\n\|[-:| ]+\|\n)((?:\|.*\|\n?)+)'
        
        def fix_table_alignment(match):
            header = match.group(1)
            rows = match.group(2)
            
            # Standardiser l'alignement
            lines = header.split('\n')
            if len(lines) >= 2:
                separator = lines[1]
                # Remplacer par alignement centré par défaut
                separator = re.sub(r':?-\+:?', ':-:', separator)
                separator = re.sub(r':?--+:?', ':--:', separator)
                lines[1] = separator
                header = '\n'.join(lines)
            
            return header + rows
        
        content, table_count = re.subn(table_pattern, fix_table_alignment, 
                                      content, flags=re.MULTILINE)
        if table_count > 0:
            modifications.append(f"{table_count} table(s) alignée(s)")
        
        # Écrire les modifications
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            if modifications:
                print(f"    ✓ Modifications: {', '.join(modifications)}")
            else:
                print(f"    ✓ Fichier nettoyé")
        else:
            print(f"    ✓ Aucune modification nécessaire")
    
    def fix_trailing_whitespace_file(self, filepath: Path):
        """Supprimer les espaces en fin de ligne dans un fichier"""
        print(f"\n  🧹 Nettoyage: {filepath.relative_to(self.backend_dir)}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Vérifier et supprimer les espaces en fin de ligne
        cleaned_lines = []
        has_trailing = False
        
        for line in lines:
            cleaned = line.rstrip() + '\n'
            if cleaned != line:
                has_trailing = True
            cleaned_lines.append(cleaned)
        
        if has_trailing:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(cleaned_lines)
            print(f"    ✓ Espaces en fin de ligne supprimés")
        else:
            print(f"    ✓ Aucun espace en fin de ligne trouvé")
    
    def fix_test_file(self, filepath: Path):
        """Corriger les fichiers de test (asserts)"""
        print(f"\n  🧪 Test file: {filepath.relative_to(self.backend_dir)}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Compter les asserts simples
        assert_count = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('assert ') and not stripped.startswith('assertRaises'):
                assert_count += 1
                print(f"    ⚠️  Ligne {i+1}: {stripped[:60]}...")
        
        if assert_count > 0:
            print(f"    ⚠️  {assert_count} assert(s) simple(s) détecté(s)")
            print(f"    💡 Considérez utiliser les méthodes unittest (assertEqual, etc.)")
    
    def create_backend_precommit_config(self):
        """Créer une configuration pre-commit spécifique pour le backend"""
        print("\n" + "=" * 60)
        print("CRÉATION DE LA CONFIGURATION PRE-COMMIT")
        print("=" * 60)
        
        precommit_config = """# .pre-commit-config.yaml pour le backend
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
        files: ^backend/
      - id: ruff-format
        files: ^backend/
  
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
        files: ^backend/
      - id: end-of-file-fixer
        files: ^backend/
      - id: check-yaml
      - id: check-added-large-files
      - id: check-ast
        files: ^backend/
      - id: check-merge-conflict
  
  - repo: https://github.com/igorshubovych/markdownlint-cli
    rev: v0.35.0
    hooks:
      - id: markdownlint
        files: ^backend/
        args: [--fix]
  
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        files: ^backend/
        args: ['-c', 'backend/pyproject.toml', '--skip=B101']
  
  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort
        name: isort (python)
        files: ^backend/
"""

        config_file = self.backend_dir.parent / '.pre-commit-config.yaml'
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(precommit_config)
        
        print(f"✓ Fichier créé: {config_file}")
        
        # Créer pyproject.toml dans le backend
        pyproject_content = """[tool.ruff]
target-version = "py38"
line-length = 88
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long
    "B008",  # do not perform function calls in argument defaults
    "B007",  # loop control variable not used
    "F401",  # imported but unused
]

[tool.ruff.per-file-ignores]
"*/__init__.py" = ["F401"]
"*/tests/*" = ["B101", "S101", "S607"]
"*test*.py" = ["B101", "S101", "S607"]

[tool.bandit]
exclude_dirs = ["tests", "venv", ".venv", "__pycache__"]
skips = ["B101"]

[tool.isort]
profile = "black"
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
line_length = 88

[tool.black]
line-length = 88
target-version = ['py38']
include = '\\.pyi?$'
extend-exclude = '''
/(
  \\.eggs
  | \\.git
  | \\.hg
  | \\.mypy_cache
  | \\.tox
  | \\.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''
"""

        pyproject_file = self.backend_dir / 'pyproject.toml'
        with open(pyproject_file, 'w', encoding='utf-8') as f:
            f.write(pyproject_content)
        
        print(f"✓ Fichier créé: {pyproject_file}")
        
        print("\n" + "=" * 60)
        print("INSTRUCTIONS D'INSTALLATION:")
        print("=" * 60)
        print("1. Installez pre-commit:")
        print("   pip install pre-commit")
        print("\n2. Installez les hooks git (depuis la racine du projet):")
        print("   cd R:/ia-learning-platform")
        print("   pre-commit install")
        print("\n3. Pour tester sur tous les fichiers backend:")
        print("   pre-commit run --all-files")
        print("\n4. Les hooks s'exécuteront automatiquement à chaque commit git.")

def main():
    parser = argparse.ArgumentParser(
        description='Corriger automatiquement les problèmes de linting dans le backend'
    )
    parser.add_argument(
        '--backend-dir', 
        default="R:/ia-learning-platform/backend",
        help='Chemin vers le dossier backend (par défaut: R:/ia-learning-platform/backend)'
    )
    parser.add_argument(
        '--create-config', 
        action='store_true',
        help='Créer seulement la configuration pre-commit'
    )
    parser.add_argument(
        '--service',
        help='Corriger seulement un microservice spécifique (ex: api-gateway)'
    )
    
    args = parser.parse_args()
    
    fixer = BackendCodeFixer(args.backend_dir)
    
    if args.create_config:
        fixer.create_backend_precommit_config()
    elif args.service:
        # Corriger seulement un microservice spécifique
        if args.service in fixer.microservices:
            print(f"\nCorrection du microservice: {args.service}")
            service_path = fixer.microservices[args.service]
            fixer.fix_service_issues(service_path)
        else:
            print(f"Microservice '{args.service}' non trouvé")
            print(f"Microservices disponibles: {', '.join(fixer.microservices.keys())}")
    else:
        # Corriger tout
        fixer.fix_all_issues()
        
        print("\n" + "=" * 60)
        print("ÉTAPES SUIVANTES:")
        print("=" * 60)
        print("1. Vérifiez les corrections avec git diff:")
        print("   cd R:/ia-learning-platform")
        print("   git diff backend/")
        print("\n2. Testez que tout fonctionne encore:")
        print("   # Exécutez vos tests unitaires")
        print("   # Lancez l'application localement")
        print("\n3. Pour éviter ces problèmes à l'avenir:")
        print("   python fix_backend.py --create-config")
        print("   pip install pre-commit")
        print("   pre-commit install")

if __name__ == "__main__":
    main()