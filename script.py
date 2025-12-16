#!/usr/bin/env python3
"""
Convertisseur de mots en flashcards Brainscape
Utilise l'API Claude pour générer des définitions intelligentes
"""

import csv
import json
import os
import sys
from pathlib import Path
from typing import Optional
import anthropic


def load_env_file():
    """Charge le fichier .env manuellement."""
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Charger .env manuellement
load_env_file()

CONFIG_FILE = "config.json"
ENV_FILE = ".env"


def load_config() -> dict:
    """Charge la configuration depuis config.json s'il existe."""
    if Path(CONFIG_FILE).exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_config(config: dict):
    """Sauvegarde la configuration dans config.json."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except:
        pass


def get_user_inputs() -> tuple[str, str]:
    """Demande à l'utilisateur les informations nécessaires."""
    print("\n" + "="*60)
    print("CONVERTISSEUR DE MOTS EN FLASHCARDS BRAINSCAPE")
    print("="*60 + "\n")

    config = load_config()
    last_source = config.get("last_source", "")
    last_file = config.get("last_file", "words.txt")

    # Demander le nom de la source
    source_prompt = f"Quel est le nom de la source ? (ex: Friends, Cours Preply, Netflix, Livre)"
    if last_source:
        source_prompt += f"\n(dernière: {last_source})"
    source_prompt += "\n> "

    source_name = input(source_prompt).strip()
    if not source_name:
        source_name = last_source
    if not source_name:
        source_name = input("Le nom de la source ne peut pas être vide. Réessayez:\n> ").strip()

    # Demander le chemin du fichier
    file_prompt = f"Chemin vers le fichier avec les mots ? (ex: words.txt)"
    if last_file:
        file_prompt += f"\n(défaut: {last_file})"
    file_prompt += "\n> "

    file_path = input(file_prompt).strip()
    if not file_path:
        file_path = last_file

    # Sauvegarder pour la prochaine fois
    config["last_source"] = source_name
    config["last_file"] = file_path
    save_config(config)

    return source_name, file_path


def read_words_file(file_path: str) -> list[str]:
    """Lit le fichier et retourne une liste de mots valides."""
    path = Path(file_path)

    if not path.exists():
        print(f"\n❌ Erreur : Le fichier '{file_path}' n'existe pas.")
        sys.exit(1)

    try:
        with open(path, 'r', encoding='utf-8') as f:
            words = [word.strip() for word in f.readlines() if word.strip()]
    except Exception as e:
        print(f"\n❌ Erreur lors de la lecture du fichier : {e}")
        sys.exit(1)

    if not words:
        print(f"\n❌ Erreur : Le fichier est vide ou ne contient que des lignes vides.")
        sys.exit(1)

    return words


def generate_word_data(client: anthropic.Anthropic, word: str, max_retries: int = 2) -> Optional[dict]:
    """Génère les données pour un mot via l'API Claude avec retry."""
    retries = 0

    while retries <= max_retries:
        try:
            prompt = f"""Analyse ce mot anglais et fournis des informations pour des flashcards d'apprentissage du vocabulaire (niveau A1-A2).

Mot: {word}

Réponds EXACTEMENT dans ce format (avec les tirets):
PART_OF_SPEECH: [verb/noun/adjective/adverb/other]
DEFINITION: [définition en anglais, UNE SEULE PHRASE très simple et très courte, niveau débutant, pas plus de 12 mots]
FRENCH: [traduction française]
EXAMPLE_1: [une phrase d'exemple pertinente en anglais avec ce mot]
EXAMPLE_2: [une deuxième phrase d'exemple pertinente en anglais avec ce mot]

Important:
- La définition doit être TRÈS courte, TRÈS simple, et en une seule phrase (maximum 12 mots)
- Les exemples doivent être réalistes et montrer l'usage naturel du mot
- Pour les verbes: utilise l'infinitif
- Pour les noms: utilise le singulier
- Pas de formatage spécial, juste le texte simple"""

            message = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=200,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text

            # Parser la réponse
            data = parse_claude_response(response_text, word)
            return data

        except anthropic.RateLimitError:
            retries += 1
            if retries <= max_retries:
                import time
                wait_time = 2 ** retries  # Exponential backoff
                print(f"(limite atteinte, attente {wait_time}s)", end="", flush=True)
                time.sleep(wait_time)
            else:
                print(f"\n⚠️  Erreur API pour le mot '{word}': limite dépassée")
                return None

        except anthropic.APIError as e:
            print(f"\n⚠️  Erreur API pour le mot '{word}': {e}")
            return None

    return None


def parse_claude_response(response: str, word: str) -> dict:
    """Parse la réponse structurée de Claude."""
    data = {
        'word': word,
        'part_of_speech': 'unknown',
        'definition': '',
        'french': '',
        'example_1': '',
        'example_2': ''
    }

    lines = response.strip().split('\n')

    for line in lines:
        if line.startswith('PART_OF_SPEECH:'):
            data['part_of_speech'] = line.replace('PART_OF_SPEECH:', '').strip().lower()
        elif line.startswith('DEFINITION:'):
            data['definition'] = line.replace('DEFINITION:', '').strip()
        elif line.startswith('FRENCH:'):
            data['french'] = line.replace('FRENCH:', '').strip()
        elif line.startswith('EXAMPLE_1:'):
            data['example_1'] = line.replace('EXAMPLE_1:', '').strip()
        elif line.startswith('EXAMPLE_2:'):
            data['example_2'] = line.replace('EXAMPLE_2:', '').strip()

    return data


def format_front(word: str) -> str:
    """Formate la face avant de la flashcard."""
    return word


def format_back(word_data: dict, source_name: str) -> str:
    """Formate la face arrière de la flashcard."""
    part_of_speech = word_data['part_of_speech']
    definition = word_data['definition']
    french = word_data['french']
    example_1 = word_data['example_1']
    example_2 = word_data['example_2']

    # Ajouter le contexte grammatical
    english_line = f"English: {word_data['word']} ({part_of_speech}): {definition}"
    french_line = f"Français: {french} ({part_of_speech})"
    ex1_line = f"Example 1: {example_1}"
    ex2_line = f"Example 2: {example_2}"

    # Ajout d'un saut de ligne avant Example 1
    back = f"{english_line}\n{french_line}\n\n{ex1_line}\n{ex2_line}"
    return back


def create_csv_file(words_data: list[dict], source_name: str, output_path: str) -> str:
    """Crée le fichier CSV pour Brainscape."""
    try:
        # Supprimer tous les anciens fichiers brainscape_*.csv
        for old_file in Path('.').glob('brainscape_*.csv'):
            try:
                os.remove(old_file)
            except:
                pass

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # En-têtes
            writer.writerow(['Front', 'Back', 'Tags'])

            # Données
            for word_data in words_data:
                if word_data is not None:
                    front = format_front(word_data['word'])
                    back = format_back(word_data, source_name)
                    writer.writerow([front, back, source_name])

        return output_path
    except Exception as e:
        print(f"\n❌ Erreur lors de la création du fichier CSV : {e}")
        sys.exit(1)


def main():
    """Fonction principale."""
    try:
        # Obtenir les inputs utilisateur
        source_name, file_path = get_user_inputs()

        # Lire les mots
        print(f"\n📖 Lecture du fichier '{file_path}'...")
        words = read_words_file(file_path)
        print(f"✅ {len(words)} mots trouvés")

        # Initialiser le client Anthropic
        try:
            # Vérifier si la clé API est disponible
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                print(f"\n❌ Erreur : Clé API Anthropic non trouvée.")
                print(f"\n   Deux options :")
                print(f"\n   Option 1 : Fichier .env (recommandé)")
                print(f"   1. Copiez '.env.example' en '.env'")
                print(f"   2. Modifiez '.env' et ajoutez votre clé API")
                print(f"   3. Relancez le script")
                print(f"\n   Option 2 : Variable d'environnement")
                print(f"   export ANTHROPIC_API_KEY='votre-clé-api'")
                sys.exit(1)

            client = anthropic.Anthropic(api_key=api_key)
        except Exception as e:
            print(f"\n❌ Erreur : Impossible d'initialiser le client Anthropic.")
            print(f"   Vérifiez que votre clé API est correcte dans le fichier .env")
            print(f"   Erreur: {e}")
            sys.exit(1)

        # Générer les données pour chaque mot
        print(f"\n🔄 Génération des définitions via Claude...\n")
        words_data = []

        for i, word in enumerate(words, 1):
            print(f"   [{i}/{len(words)}] Traitement: {word}...", end=" ", flush=True)
            word_data = generate_word_data(client, word)
            if word_data:
                words_data.append(word_data)
                print("✓")
            else:
                print("✗ (ignoré)")

        # Créer le fichier CSV
        output_filename = f"brainscape_{source_name.lower().replace(' ', '_')}.csv"
        print(f"\n📝 Création du fichier CSV...")
        csv_path = create_csv_file(words_data, source_name, output_filename)

        # Afficher le résumé
        print("\n" + "="*60)
        print("✅ CONVERSION TERMINÉE")
        print("="*60)
        print(f"📊 Mots traités : {len(words_data)}/{len(words)}")
        print(f"📄 Fichier créé : {output_filename}")
        print(f"📍 Localisation : {os.path.abspath(output_filename)}")
        print(f"🏷️  Tags : {source_name}")
        print("="*60 + "\n")
        print("✨ Fichier prêt à importer dans Brainscape !")

    except KeyboardInterrupt:
        print("\n\n⛔ Opération annulée par l'utilisateur.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur inattendue : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
