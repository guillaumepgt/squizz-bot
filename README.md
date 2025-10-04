# Squizz-bot

Ce document explique comment configurer et exécuter le script Python fourni, qui utilise Selenium pour automatiser une session de navigateur sur le site `https://squiz.gg/room/0`. Le script charge des cookies et du localStorage, attend des questions sur la page, les traite via une API externe (`groq`), et envoie des réponses automatisées.

Le script est initialement configuré pour Firefox (avec geckodriver)

## Prérequis Généraux

- **Python 3.x** : Assurez-vous d'avoir Python installé (version 3.12 recommandée, mais compatible avec 3.8+).
- **Dépendances Python** : Installez les paquets nécessaires via pip :
  ```
  pip install -r requirements.txt
  ```
  ou
  ```
  pip install selenium
  ```
  (Le script utilise également `json`, `time`, `os`, `signal`, `getpass`, `sys`, qui sont standards. Si `psutil` est utilisé pour le nettoyage, installez-le avec `pip install psutil`.)
- **Fichiers de configuration** :
   - `cookies.json` : Fichier JSON contenant les cookies à charger (optionnel, exportable via les outils de développement du navigateur).
   - `local.json` : Fichier JSON contenant les entrées localStorage à charger (requis pour une session persistante ; exportez-le via DevTools > Application > Local Storage).
- **API externe** : Le script appelle `api_ia.poser_question(texte)`. Assurez-vous que la clé API `groq` est disponible et fonctionnel (non fourni dans le code).
- **Navigateur et Driver** : Téléchargez le driver correspondant à votre navigateur (voir sections ci-dessous). Assurez-vous que la version du driver correspond à celle du navigateur installé.

## Configuration et Exécution avec Firefox

### Étapes de Setup
1. **Téléchargez geckodriver** :
   - Allez sur [Mozilla GeckoDriver Releases](https://github.com/mozilla/geckodriver/releases).
   - Téléchargez la version compatible avec votre OS et votre version de Firefox (ex. : geckodriver-v0.35.0-linux64.tar.gz pour Linux).
   - Extrayez et placez `geckodriver` dans un répertoire accessible (ex. : `/usr/local/bin/` ou le répertoire du script).
   - Rendez-le exécutable : `chmod +x geckodriver`.
2. **Mettez à jour le script** :
   - Dans le code, `GECKODRIVER_PATH = "geckodriver"` pointe vers le driver. Utilisez un chemin absolu si nécessaire (ex. : `/usr/local/bin/geckodriver`).
3. **Installez Firefox** : Assurez-vous que Firefox est installé sur votre machine.

### Lancement
- Exécutez le script :
  ```
  python squizz.py
  ```
- Le navigateur s'ouvrira, chargera la page, et entrera en boucle pour traiter les questions.
- Pour arrêter : Appuyez sur Ctrl+C (le script gère la fermeture proprement).

**Dépannage** :
- Si des processus geckodriver persistent, le script tente de les tuer via `psutil` ou suggère `pkill -u $(whoami) -f geckodriver`.

## Récupérer les Cookies et le LocalStorage pour se Connecter sur Squiz.gg

**Prérequis :**
- Un navigateur web moderne (Chrome, Firefox, Edge... recommandé : Firefox pour compatibilité avec GeckoDriver).
- Être connecté à votre compte sur squiz.gg.
- Aucune extension ou outil supplémentaire n'est requis, mais les Outils de Développement (DevTools) du navigateur suffisent.

**Attention :**
- Les cookies et le localStora  ge contiennent des données sensibles (comme des tokens d'authentification). Ne les partagez pas et stockez-les en sécurité.
- Ces données expirent souvent (session-based), donc répétez l'opération si nécessaire.

## Étape 1 : Se Connecter sur Squiz.gg
1. Ouvrez votre navigateur et allez sur [https://squiz.gg](https://squiz.gg).
2. Connectez-vous à votre compte (via twitch).
3. Naviguez vers une page nécessitant l'authentification, comme [https://squiz.gg/room/0](https://squiz.gg/room/0), pour que les cookies et localStorage soient chargés.

## Étape 2 : Ouvrir les Outils de Développement (DevTools)
1. Une fois sur la page authentifiée, ouvrez les DevTools :
    - **Chrome/Edge** : Appuyez sur `F12` ou `Ctrl + Shift + I` (Windows/Linux) / `Cmd + Option + I` (Mac). Ou clic droit > "Inspecter".
    - **Firefox** : Appuyez sur `F12` ou `Ctrl + Shift + I` (Windows/Linux) / `Cmd + Option + I` (Mac).
2. Passez à l'onglet **Application** (ou **Stockage** dans Firefox).

## Étape 3 : Exporter les Cookies
Les cookies sont stockés sous le domaine `squiz.gg`.

1. Dans l'onglet **Application** > Section **Cookies** (ou **Stockage > Cookies** dans Firefox).
2. Sélectionnez le domaine `https://squiz.gg` (ou `.squiz.gg` si listé).
3. Vous verrez une liste de cookies avec des colonnes comme : Name, Value, Domain, Path, Expires, etc.
4. Pour exporter en JSON (format requis par votre script) :
    - Utilisez la console JavaScript pour extraire tous les cookies :
        - Passez à l'onglet **Console**.
        - Collez et exécutez ce script :
          ```javascript:disable-run
          const cookies = document.cookie.split('; ').map(c => {
            const [name, value] = c.split('=');
            return { name, value, domain: '.squiz.gg', path: '/', secure: true, httpOnly: false }; // Ajustez domain/path si nécessaire
          });
          console.log(JSON.stringify(cookies, null, 2));
          ```
        - Copiez la sortie JSON affichée dans la console.
    - Alternative manuelle : Copiez chaque cookie un par un et construisez un tableau JSON comme suit :
      ```json
      [
        {
          "name": "nom_du_cookie1",
          "value": "valeur_du_cookie1",
          "domain": ".squiz.gg",
          "path": "/",
          "secure": true,
          "httpOnly": false,
          "expiry": 1234567890
        }
      ]
      ```
5. Enregistrez ce JSON dans un fichier nommé `cookies.json` (dans le même dossier que votre script).

**Note :** Dans votre script, seuls les champs "name", "value", "domain", "path", "secure", "httpOnly", "expiry" sont utilisés. Assurez-vous qu'ils sont présents. Si un cookie manque, cela pourrait causer des erreurs lors du chargement.

## Étape 4 : Exporter le LocalStorage
Le localStorage contient des données persistantes comme des tokens ou préférences utilisateur.

1. Dans l'onglet **Application** > Section **Local Storage** (ou **Stockage > Stockage Local** dans Firefox).
2. Sélectionnez le domaine `https://squiz.gg`.
3. Vous verrez une liste de clés/valeurs (ex. : clé "auth_token" avec une valeur JSON).
4. Pour exporter en JSON :
    - Passez à l'onglet **Console**.
    - Collez et exécutez ce script :
      ```javascript
      const ls = {};
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        ls[key] = localStorage.getItem(key);
      }
      console.log(JSON.stringify(ls, null, 2));
      ```
    - Copiez la sortie JSON (un objet `{ "clé1": "valeur1", "clé2": "valeur2" }`).
5. Enregistrez ce JSON dans un fichier nommé `local.json`.

**Note :** Si le fichier `local.json` est manquant, votre script affiche un message d'info. Mais pour une connexion complète, il est souvent essentiel (ex. : tokens JWT).

## Étape 5 : Tester la Connexion avec les Fichiers
1. Placez `cookies.json` et `local.json` dans le dossier de votre script.
2. Exécutez votre script Python (celui avec Selenium).
3. Le script chargera les cookies et localStorage, rafraîchira la page, et devrait être connecté sans login manuel.
4. Si ça ne marche pas :
    - Vérifiez les erreurs dans la console (ex. : cookies expirés).
    - Répétez les étapes 1-4 pour rafraîchir les données.
    - Assurez-vous que le domaine dans les cookies est correct (`.squiz.gg` ou `squiz.gg`).