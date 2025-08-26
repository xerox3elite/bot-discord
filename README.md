# Arsenal Bot

Arsenal Bot est un bot Discord multifonctionnel conçu pour la modération, la musique, l'économie, et bien plus encore. Il est construit avec `discord.py`.

## Configuration

1.  **Cloner le dépôt :**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Installer les dépendances :**
    Assurez-vous d'avoir Python 3.8 ou supérieur installé. Ensuite, installez les dépendances requises en utilisant pip :
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurer les variables d'environnement :**
    Créez un fichier `.env` à la racine du projet et ajoutez votre token de bot Discord :
    ```
    DISCORD_TOKEN=VOTRE_TOKEN_DISCORD_ICI
    CREATOR_ID=VOTRE_ID_CREATEUR_ICI
    ```
    Remplacez `VOTRE_TOKEN_DISCORD_ICI` par le token de votre bot et `VOTRE_ID_CREATEUR_ICI` par votre ID utilisateur Discord.

## Lancement

Pour lancer le bot, exécutez la commande suivante :
```bash
python main.py
```

Le bot devrait maintenant être en ligne et prêt à être utilisé sur vos serveurs Discord.
