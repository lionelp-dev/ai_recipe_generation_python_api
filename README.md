# API REST de génération de recettes et de leur visuels avec de l'intelligence artificielle

## Prérequis

- Python 3.12 ou supérieur
- Une clé API OpenRouter pour activer le mode Discovery

## Installation et lancement

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

## Configuration

Créez `.env` à partir de `.env.example` et ajustez les variables suivantes :

| Variable | Rôle |
| --- | --- |
| `SECRET_KEY` | Clé secrète Django ; remplacez la valeur de développement en production. |
| `PORT` | Port de Django, `8000` par défaut. |
| `OPENROUTER_API_KEY` | Active le mode Discovery. Laissez-la vide pour le masquer. |

## API Endpoints

### `POST /internal/recipes/discover/`

Génère un batch de recette à partir d'un prompt.

```bash
curl -X POST http://127.0.0.1:8000/internal/recipes/discover \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Une idée de dîner végétarien rapide pour deux personnes",
  }'
```
