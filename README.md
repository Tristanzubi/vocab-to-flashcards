# Script Word - Convertisseur de Mots en Flashcards Brainscape

Un script Python qui convertit une liste de mots anglais en flashcards pour Brainscape, en utilisant l'API Claude pour générer des définitions intelligentes.

## Fonctionnalités

- 📖 Lecture d'une liste de mots depuis un fichier texte
- 🤖 Génération automatique de définitions via l'API Claude
- 📝 Création de flashcards avec :
  - Mot en anglais (face avant)
  - Définition simple et courte
  - Traduction en français
  - Catégorie grammaticale (verbe, nom, adjectif, etc.)
  - 2 exemples d'utilisation
- 📊 Export en format CSV compatible avec Brainscape
- 🏷️ Support des tags pour organiser vos flashcards par source

## Installation

### Prérequis

- Python 3.8+
- Une clé API Anthropic

### Étapes

1. Clonez ou téléchargez ce projet
2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Créez un fichier `.env` à la racine du projet :
```bash
cp .env.example .env
```

4. Modifiez `.env` et ajoutez votre clé API Anthropic :
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx
```

## Utilisation

### 1. Préparez votre fichier de mots

Créez un fichier texte (par exemple `words.txt`) avec un mot par ligne :
```
provide
stole
browser
unable
replied
```

### 2. Lancez le script

```bash
python script.py
```

### 3. Répondez aux questions

Le script vous demandera :
- **Nom de la source** : où proviennent ces mots (ex: "Friends", "Cours Preply", "Netflix", "Livre")
- **Chemin du fichier** : où se trouve votre fichier de mots (ex: `words.txt`)

### 4. Résultat

Le script génère un fichier CSV nommé `brainscape_{nom_source}.csv` prêt à importer dans Brainscape.

Exemple de sortie :
```
brainscape_friends.csv
brainscape_netflix.csv
```

> **Note** : À chaque exécution, les anciens fichiers CSV sont automatiquement supprimés. Seul le dernier fichier généré est conservé.

## Configuration

Le script sauvegarde votre dernière source et votre dernier fichier utilisé dans `config.json` pour accélérer les prochaines exécutions.

## Format du fichier CSV généré

| Colonne | Contenu |
|---------|---------|
| **Front** | Le mot en anglais |
| **Back** | Définition, traduction, catégorie grammaticale et 2 exemples |
| **Tags** | La source (pour organiser vos flashcards) |

Exemple de contenu "Back" :
```
English: provide (verb): Supply or make available
Français: fournir (verb)

Example 1: The company provides health insurance to its employees.
Example 2: Can you provide me with more information about this project?
```

## Gestion des erreurs

Le script gère automatiquement :
- Les limites de taux API (avec retry exponentiel)
- Les erreurs de fichier
- Les erreurs de connexion API

Les mots en erreur sont ignorés avec un message ⚠️.

## Configuration avancée

### Modèle IA utilisé

Le script utilise `claude-haiku-4-5-20251001` pour un bon équilibre entre coût et qualité. Vous pouvez le modifier à la ligne 141 de `script.py` :

```python
model="claude-sonnet-4-5-20250929",  # Plus puissant mais plus coûteux
```

### Paramètres de génération

- **Max tokens** : 200 (limité pour des définitions courtes)
- **Retry max** : 2 tentatives en cas de limite API

## Troubleshooting

### "Le fichier '{file_path}' n'existe pas"
Vérifiez que le chemin vers votre fichier de mots est correct.

### "Clé API Anthropic non trouvée"
Vérifiez que votre `.env` existe et contient `ANTHROPIC_API_KEY=sk-ant-...`

### "Limite API dépassée"
Le script attend automatiquement avant de réessayer. Les mots en erreur seront ignorés.

## Importer dans Brainscape

1. Allez sur Brainscape.com
2. Créez un nouveau cours ou classe
3. Utilisez l'option d'import CSV
4. Sélectionnez le fichier `brainscape_*.csv` généré
5. Les flashcards sont automatiquement créées avec les tags

## Licence

Libre d'utilisation.
