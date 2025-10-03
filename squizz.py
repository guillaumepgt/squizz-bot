import json
import time
import os
import signal
import getpass
import sys
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import api_ia

# --- CONFIG ---
GECKODRIVER_PATH = "geckodriver"  # adapte si nécessaire (chemin absolu recommandé)
OUTPUT_DIR = "/tmp"
BASE_URL = "https://squiz.gg/room/0"
COOKIES_FILE = "cookies.json"
LOCALSTORAGE_FILE = "local.json"

# --- service ---
# envoyer les logs dans /dev/null pour éviter affichage verbeux
log_path = os.devnull  # ou f"{OUTPUT_DIR}/geckodriver.log" si tu veux conserver
service = Service(
    executable_path=GECKODRIVER_PATH,
    log_path=log_path
    # ne passe pas service_args si pas nécessaire
)

driver = None

def signal_handler(sig, frame):
    """
    Gestionnaire de signal pour quitter proprement sur Ctrl+C.
    """
    print("\n[INFO] Ctrl+C détecté. Fermeture propre...")
    if driver:
        try:
            driver.quit()
        except Exception as e:
            print(f"[WARN] Erreur lors de driver.quit() dans signal_handler: {e}")
    sys.exit(0)

# Associer le handler à SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

def kill_geckodriver_for_current_user():
    """
    Tentative de tuer proprement les processus 'geckodriver' appartenant
    à l'utilisateur courant. Utilise psutil si disponible, sinon imprime une commande à lancer.
    """
    try:
        import psutil
    except Exception:
        print("[INFO] psutil non installé — pour tuer les geckodriver restants, exécute manuellement :")
        print("  pkill -u $(whoami) -f geckodriver")
        return

    me = getpass.getuser()
    killed = 0
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cmdline']):
        try:
            info = proc.info
            if info['name'] and 'geckodriver' in info['name']:
                # vérifier que le proc est mien
                if info.get('username') == me:
                    print(f"[CLEANUP] killing geckodriver pid={proc.pid} user={info.get('username')}")
                    proc.terminate()
                    try:
                        proc.wait(timeout=3)
                    except psutil.TimeoutExpired:
                        proc.kill()
                    killed += 1
        except Exception:
            pass
    print(f"[CLEANUP] processus geckodriver tués : {killed}")

try:
    driver = webdriver.Firefox(service=service)
    driver.set_window_size(1200, 900)

    # 1) charger le domaine (nécessaire pour pouvoir ajouter des cookies / localStorage)
    try:
        driver.get(BASE_URL)
        time.sleep(1)
    except Exception as e:
        print(f"[WARN] Erreur lors du chargement de la page initiale: {e}")
        # Continuer malgré l'erreur, ou relancer si critique

    # 2) cookies
    if os.path.exists(COOKIES_FILE):
        try:
            with open(COOKIES_FILE, "r", encoding="utf-8") as f:
                cookies = json.load(f)
            for cookie in cookies:
                clean = {k: v for k, v in cookie.items() if k in ("name", "value", "domain", "path", "secure", "httpOnly", "expiry")}
                driver.add_cookie(clean)
        except Exception as e:
            print(f"[WARN] Erreur lors du chargement des cookies: {e}")

    # 3) localStorage
    if os.path.exists(LOCALSTORAGE_FILE):
        try:
            with open(LOCALSTORAGE_FILE, "r", encoding="utf-8") as f:
                ls = json.load(f)
            for key, value in ls.items():
                js = f"window.localStorage.setItem({json.dumps(key)}, {json.dumps(value)});"
                driver.execute_script(js)
        except Exception as e:
            print(f"[WARN] Erreur lors du chargement du localStorage: {e}")
    else:
        print(f"[INFO] {LOCALSTORAGE_FILE} introuvable. Exporte-le via DevTools.")

    # 4) recharger
    try:
        driver.refresh()
    except Exception as e:
        print(f"[WARN] Erreur lors du refresh de la page: {e}")

    # 5) boucle principale pour attendre et récupérer les questions
    texte = ""
    while True:
        try:
            wait = WebDriverWait(driver, 60)
            texte1 = texte

            # Boucle pour attendre un texte suffisant
            while len(texte) <= 20:
                try:
                    question_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[dir='auto'].r-lrvibr")))
                    texte = str(question_element.text)
                except Exception as e:
                    print(f"[WARN] Erreur lors de la recherche de l'élément question (len <=20): {e}")
                    time.sleep(1)  # Petit délai avant réessai
                    continue

            # Boucle pour attendre un changement de texte
            while texte == texte1:
                try:
                    question_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[dir='auto'].r-lrvibr")))
                    texte = str(question_element.text)
                except Exception as e:
                    print(f"[WARN] Erreur lors de la recherche de l'élément question (texte inchangé): {e}")
                    time.sleep(1)  # Petit délai avant réessai
                    continue

            print("Texte trouvé :", texte)

            # Poser la question et traiter la réponse
            try:
                result = api_ia.poser_question(texte)
                print(result)
                result = result.translate(str.maketrans("", "", ".,()"))
            except Exception as e:
                print(f"[WARN] Erreur lors de poser_question: {e}")
                continue  # Passer à la prochaine itération

            # Envoyer la réponse
            try:
                input_box = driver.find_element(By.CLASS_NAME, "css-11aywtz")
                input_box.send_keys(result)
                input_box.send_keys(Keys.RETURN)
            except Exception as e:
                print(f"[WARN] Erreur lors de l'envoi de la réponse: {e}")
                time.sleep(1)  # Délai avant réessai

        except Exception as e:
            print(f"[ERROR] Erreur dans la boucle principale: {repr(e)}")
            time.sleep(5)  # Délai plus long en cas d'erreur générale, puis réessai

except Exception as e:
    print("Erreur critique durant l'initialisation Selenium :", repr(e))

finally:
    # fermeture robuste (mais seulement appelée si sortie du try principal, pas dans la boucle infinie)
    if driver:
        try:
            driver.quit()
        except PermissionError as pe:
            print("PermissionError lors de driver.quit():", pe)
            try:
                driver.close()
            except Exception as e:
                print("Erreur driver.close():", e)
            # tenter un nettoyage des processus geckodriver appartenant à l'utilisateur
            kill_geckodriver_for_current_user()
        except Exception as ex:
            print("Autre exception lors de driver.quit():", ex)
            kill_geckodriver_for_current_user()
    else:
        # si driver n'a pas été initialisé mais processus geckodriver traînent, proposer nettoyage
        kill_geckodriver_for_current_user()