# 🚀 Guide de déploiement sur Railway

Ton bot tournera **24h/24 en ligne**, sans garder ton PC allumé.

---

## Étape 1 : Créer les fichiers pour Railway

Le projet est déjà prêt avec :
- `Procfile` → dit à Railway de lancer `python bot.py`
- `runtime.txt` → version Python
- `.gitignore` → ne pas envoyer les secrets (tokens) sur GitHub

## Étape 2 : Pousser le code sur GitHub

1. Crée un compte sur **github.com** si tu n'en as pas
2. Crée un **nouveau repository** (clic sur "+" en haut à droite)
   - Nom : `bot-pronostics`
   - Ne coche PAS "Add a README"
   - Clique **Create repository**
3. Tu obtiens une page avec des commandes. Dans ton dossier `bot-pronostics`, ouvre PowerShell/CMD et tape :
```
git init
git add .
git commit -m "Bot pronostics"
git branch -M main
git remote add origin https://github.com/TON_PSEUDO/bot-pronostics.git
git push -u origin main
```
   *(remplace TON_PSEUDO par ton pseudo GitHub, et mets ton vrai lien)*

## Étape 3 : Créer le projet sur Railway

1. Va sur **https://railway.app**
2. Connecte-toi avec **GitHub** (bouton "Continue with GitHub")
3. Clique **+ New Project**
4. Choisis **"Deploy from GitHub repo"**
5. Sélectionne le repo **bot-pronostics**
6. Railway déploie automatiquement 🎉

## Étape 4 : Ajouter les secrets (TOKENS)

Sur Railway, dans ton projet :

1. Va dans l'onglet **Variables** (le panneau avec l'icône clé)
2. Ajoute ces 2 variables :

| Variable | Valeur |
|----------|--------|
| `TELEGRAM_TOKEN` | `8682830253:AAE-qkR7CCKWlkiHuR3W37Ns1IZ1CkKIcF0` |
| `FOOTBALL_API_KEY` | `09b9a1b086ab468280889164d47e457a` |

3. Railway redémarre le bot automatiquement avec ces valeurs

## Étape 5 : Vérifier que ça marche

1. Dans Railway, va dans l'onglet **Deployments**
2. Tu devrais voir "Deploy Success" (vert)
3. Clique sur **View Logs**
4. Tu devrais voir `Application started` et `Bot démarré`
5. Envoie `/start` à **t.me/ToshibaPronoBot**

---

## 📱 Bonus : surveille ton bot depuis ton téléphone

Installe l'app **Railway** sur Android/iOS pour vérifier les logs et voir si le bot tourne depuis ton téléphone.

---

## ❓ À quoi ça ressemble si ça marche ?

Dans les logs Railway tu verras des lignes comme :
```
INFO - Application started
INFO - Bot démarré ! Envoie /start sur Telegram.
INFO - HTTP Request: POST .../getUpdates "HTTP/1.1 200 OK"
```

Les `getUpdates` répétés toutes les 10s = le bot écoute les messages. C'est NORMAL et c'est bon signe !

---

## ⚠️ Attention aux coûts

Railway donne **5€ de crédit gratuit** au départ (= environ 1-2 mois d'utilisation).
Ce bot consomme très peu (quelques centimes/mois après ça).
Pour ne pas dépasser : désactive l'auto-restart si tu veux, ou upgrade quand le crédit s'épuise (ça coûte ~5€/mois).

---

## ✅ Ton bot est EN LIGNE 24h/24

Une fois déployé :
- Tu peux **fermer ton PC**, le bot continue de tourner
- Tu peux **y accéder depuis ton téléphone**
- Il répond à chaque message instantanément
