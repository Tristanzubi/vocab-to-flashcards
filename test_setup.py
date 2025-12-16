#!/usr/bin/env python3
"""
Script de vérification de la configuration
Vérifie que tout est correctement configuré avant de lancer le convertisseur
"""

import os
import sys
from pathlib import Path

def check_python_version():
    """Vérifie la version de Python."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print("✅ Python version OK:", f"{version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print("❌ Python 3.10+ requis (vous avez:", f"{version.major}.{version.minor})")
        return False

def check_dependencies():
    """Vérifie les dépendances."""
    deps = {
        'anthropic': 'anthropic',
        'dotenv': 'python-dotenv'
    }

    all_ok = True
    for module, package in deps.items():
        try:
            __import__(module)
            print(f"✅ {package} installé")
        except ImportError:
            print(f"❌ {package} manquant - Installez avec: pip install {package}")
            all_ok = False

    return all_ok

def check_env_file():
    """Vérifie le fichier .env."""
    if Path(".env").exists():
        with open(".env", 'r') as f:
            content = f.read()
            if "ANTHROPIC_API_KEY" in content:
                if "votre-clé-api-ici" in content:
                    print("⚠️  .env existe mais contient le placeholder 'votre-clé-api-ici'")
                    print("   👉 Éditez .env et remplacez par votre vraie clé API")
                    return False
                else:
                    print("✅ Fichier .env trouvé avec une clé API")
                    return True
            else:
                print("⚠️  .env existe mais ne contient pas ANTHROPIC_API_KEY")
                return False
    else:
        print("❌ Fichier .env manquant")
        print("   👉 Copiez .env.example en .env et éditez-le avec votre clé API")
        if Path(".env.example").exists():
            print("   👉 Utilisez: cp .env.example .env")
        return False

def check_requirements_file():
    """Vérifie le fichier requirements.txt."""
    if Path("requirements.txt").exists():
        print("✅ Fichier requirements.txt trouvé")
        return True
    else:
        print("❌ Fichier requirements.txt manquant")
        return False

def check_script_file():
    """Vérifie le script principal."""
    if Path("script.py").exists():
        print("✅ Fichier script.py trouvé")
        return True
    else:
        print("❌ Fichier script.py manquant")
        return False

def check_api_key():
    """Vérifie que la clé API est accessible."""
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if api_key:
        # Vérifier le format
        if api_key.startswith("sk-ant-"):
            print("✅ Clé API valide (format correct)")
            return True
        elif api_key == "votre-clé-api-ici":
            print("⚠️  Clé API non configurée (placeholder)")
            return False
        else:
            print("⚠️  Clé API suspecte (ne commence pas par sk-ant-)")
            return False
    else:
        print("❌ Clé API non trouvée dans l'environnement")
        print("   👉 Configurez .env avec votre clé API")
        return False

def main():
    """Fonction principale."""
    print("\n" + "="*60)
    print("VÉRIFICATION DE LA CONFIGURATION")
    print("="*60 + "\n")

    checks = [
        ("Python version", check_python_version),
        ("Dépendances Python", check_dependencies),
        ("Fichier requirements.txt", check_requirements_file),
        ("Fichier script.py", check_script_file),
        ("Fichier .env", check_env_file),
        ("Clé API Anthropic", check_api_key),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n🔍 Vérification: {name}")
        print("-" * 40)
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Erreur lors de la vérification: {e}")
            results.append((name, False))

    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")

    print("\n" + "="*60)
    print(f"Résultat: {passed}/{total} vérifications réussies")
    print("="*60 + "\n")

    if passed == total:
        print("🎉 Tout est configuré correctement !")
        print("   Vous pouvez maintenant lancer: python script.py")
        return 0
    else:
        print("⚠️  Veuillez corriger les erreurs ci-dessus")
        print("\n   Prochaines étapes:")
        print("   1. Copiez .env.example en .env")
        print("   2. Éditez .env avec votre clé API")
        print("   3. Relancez ce script: python test_setup.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
