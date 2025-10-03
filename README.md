# Squizz-bot
# Documentation pour le Script d'Automatisation Selenium

Ce document explique comment configurer et exécuter le script Python fourni, qui utilise Selenium pour automatiser une session de navigateur sur le site `https://squiz.gg/room/0`. Le script charge des cookies et du localStorage, attend des questions sur la page, les traite via une API externe (`api_ia`), et envoie des réponses automatisées.

Le script est initialement configuré pour Firefox (avec geckodriver), mais cette documentation couvre également les adaptations pour Chrome (avec chromedriver) et pour une exécution en conteneur Docker. Cela permet d'adapter le lancement en fonction des préférences ou contraintes des utilisateurs (par exemple, pour éviter des problèmes de compatibilité ou pour isoler l'environnement).

## Prérequis Généraux

- **Python 3.x** : Assurez-vous d'avoir Python installé (version 3.12 recommandée, mais compatible avec 3.8+).
- **Dépendances Python** : Installez les paquets nécessaires via pip :
  ```
  pip install selenium
  ```
  (Le script utilise également `json`, `time`, `os`, `signal`, `getpass`, `sys`, qui sont standards. Si `psutil` est utilisé pour le nettoyage, installez-le avec `pip install psutil`.)
- **Fichiers de configuration** :
   - `cookies.json` : Fichier JSON contenant les cookies à charger (optionnel, exportable via les outils de développement du navigateur).
   - `local.json` : Fichier JSON contenant les entrées localStorage à charger (requis pour une session persistante ; exportez-le via DevTools > Application > Local Storage).
- **API externe** : Le script appelle `api_ia.poser_question(texte)`. Assurez-vous que le module `api_ia` est disponible et fonctionnel (non fourni dans le code).
- **Navigateur et Driver** : Téléchargez le driver correspondant à votre navigateur (voir sections ci-dessous). Assurez-vous que la version du driver correspond à celle du navigateur installé.

**Note de sécurité** : Ce script automatise des interactions sur un site web. Vérifiez les conditions d'utilisation du site pour éviter des violations. Utilisez-le à des fins éducatives ou autorisées seulement.

## Configuration et Exécution avec Firefox (Configuration par Défaut)

Le script est déjà configuré pour Firefox.

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
  python votre_script.py
  ```
- Le navigateur s'ouvrira, chargera la page, et entrera en boucle pour traiter les questions.
- Pour arrêter : Appuyez sur Ctrl+C (le script gère la fermeture proprement).

**Dépannage** :
- Si des processus geckodriver persistent, le script tente de les tuer via `psutil` ou suggère `pkill -u $(whoami) -f geckodriver`.

## Configuration et Exécution avec Chrome

Pour utiliser Chrome au lieu de Firefox, modifiez le script pour utiliser `webdriver.Chrome`.

### Étapes de Setup
1. **Téléchargez chromedriver** :
   - Allez sur [ChromeDriver Downloads](https://googlechromelabs.github.io/chrome-for-testing/).
   - Téléchargez la version correspondant à votre version de Chrome (ex. : chromedriver-linux64.zip pour Linux).
   - Extrayez et placez `chromedriver` dans un répertoire accessible (ex. : `/usr/local/bin/`).
   - Rendez-le exécutable : `chmod +x chromedriver`.
2. **Installez Chrome** : Assurez-vous que Google Chrome est installé.
3. **Modifiez le script** :
   - Importez les modules pour Chrome :
     ```
     from selenium.webdriver.chrome.service import Service
     ```
   - Remplacez la section `--- CONFIG ---` pour le path :
     ```
     CHROMEDRIVER_PATH = "chromedriver"  # chemin absolu recommandé
     ```
   - Remplacez la création du service et du driver :
     ```
     service = Service(
         executable_path=CHROMEDRIVER_PATH,
         log_path=os.devnull  # ou un fichier log
     )
     driver = webdriver.Chrome(service=service)
     ```
   - Dans la fonction `kill_geckodriver_for_current_user()`, adaptez pour tuer `chromedriver` au lieu de `geckodriver` (remplacez `'geckodriver'` par `'chromedriver'` dans les checks).
   - Dans le `finally`, adaptez le nettoyage pour `chromedriver`.

### Lancement
- Même commande que pour Firefox :
  ```
  python votre_script.py
  ```
- Le comportement est identique, mais avec Chrome.

**Dépannage** : Si Chrome bloque les automatisations, ajoutez des options comme `options = webdriver.ChromeOptions(); options.add_argument('--disable-blink-features=AutomationControlled'); driver = webdriver.Chrome(service=service, options=options)`.

## Configuration et Exécution avec Docker

Pour isoler l'exécution (utile pour des environnements sans navigateur installé, ou pour des déploiements), conteneurisez le script avec Docker. Cela utilise un conteneur Selenium standalone.

### Étapes de Setup
1. **Installez Docker** : Téléchargez et installez Docker depuis [docker.com](https://www.docker.com/products/docker-desktop).
2. **Créez un Dockerfile** : Dans le répertoire du script, créez un fichier `Dockerfile` avec ce contenu :
   ```
   # Utilisez une image Python avec Selenium (pour Firefox ou Chrome)
   FROM python:3.12-slim

   # Installez les dépendances système (pour Firefox, adaptez pour Chrome si needed)
   RUN apt-get update && apt-get install -y firefox-esr wget unzip && \
       wget https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-linux64.tar.gz && \
       tar -xvzf geckodriver-v0.35.0-linux64.tar.gz && \
       mv geckodriver /usr/local/bin/ && \
       chmod +x /usr/local/bin/geckodriver && \
       rm geckodriver-v0.35.0-linux64.tar.gz && \
       apt-get clean

   # Copiez le script et les fichiers
   WORKDIR /app
   COPY votre_script.py .
   COPY cookies.json .  # Si présent
   COPY local.json .    # Si présent
   COPY api_ia.py .     # Si api_ia est un module local

   # Installez les dépendances Python
   RUN pip install --no-cache-dir selenium psutil

   # Lancez le script
   CMD ["python", "votre_script.py"]
   ```
   - Pour Chrome : Remplacez `firefox-esr` par `google-chrome-stable`, et adaptez le téléchargement pour chromedriver. Modifiez le script dans le conteneur comme dans la section Chrome.
3. **Build l'image** :
   ```
   docker build -t selenium-automation .
   ```
4. **Adaptez le script pour Docker** (optionnel) :
   - Dans Docker, les paths comme `/tmp` fonctionnent, mais montez des volumes pour persister les fichiers (ex. : cookies.json).
   - Pour un affichage headless (sans GUI), ajoutez des options au driver : `options = webdriver.FirefoxOptions(); options.add_argument('--headless'); driver = webdriver.Firefox(service=service, options=options)`.

### Lancement
- Lancez le conteneur :
  ```
  docker run --rm -v $(pwd):/app selenium-automation
  ```
   - `--rm` : Supprime le conteneur après exécution.
   - `-v $(pwd):/app` : Monte le répertoire courant pour accéder aux fichiers (cookies, localStorage).
- Pour un mode interactif ou avec logs : Ajoutez `-it` pour un terminal interactif.

**Dépannage** :
- Si besoin d'un Selenium Grid : Utilisez des images comme `selenium/standalone-firefox` et connectez-vous via RemoteWebDriver : `driver = webdriver.Remote(command_executor='http://localhost:4444/wd/hub', options=webdriver.FirefoxOptions())`.
- Erreurs de driver : Vérifiez les versions dans le Dockerfile.
- Pour Chrome dans Docker : Remplacez le téléchargement par chromedriver et utilisez `webdriver.Chrome`.

## Usage Général

- **Exécution** : Lancez avec `python votre_script.py`. Le script tourne en boucle infinie jusqu'à Ctrl+C.
- **Personnalisation** :
   - Changez `BASE_URL` si needed.
   - Ajustez `OUTPUT_DIR` pour les logs.
   - Pour plus de robustesse, ajoutez des timeouts ou des retries supplémentaires.
- **Tests** : Exécutez dans un environnement de test pour éviter des impacts sur des sessions réelles.
- **Limitations** : Le script dépend de la structure CSS du site (ex. : `div[dir='auto'].r-lrvibr` pour les questions). Si le site change, mettez à jour les sélecteurs.

Si vous avez des questions spécifiques ou besoin d'ajustements, fournissez plus de détails !

## Récupérer les Cookies et le LocalStorage pour se Connecter sur Squiz.gg

**Prérequis :**
- Un navigateur web moderne (Chrome, Firefox, Edge... recommandé : Firefox pour compatibilité avec GeckoDriver).
- Être connecté à votre compte sur squiz.gg.
- Aucune extension ou outil supplémentaire n'est requis, mais les Outils de Développement (DevTools) du navigateur suffisent.

**Attention :**
- Les cookies et le localStorage contiennent des données sensibles (comme des tokens d'authentification). Ne les partagez pas et stockez-les en sécurité.
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