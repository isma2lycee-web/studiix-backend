from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
import requests, os, secrets

app = FastAPI()

# --- CONFIG ---
CLIENT_ID = os.getenv("EDUCONNECT_CLIENT_ID")
CLIENT_SECRET = os.getenv("EDUCONNECT_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "https://ton-backend.onrender.com/callback")

# URL du vrai portail EduConnect
AUTH_URL = "https://educonnect.education.gouv.fr/idp/profile/SAML2/Redirect/SSO"
TOKEN_URL = "https://educonnect.education.gouv.fr/oauth/token"
USER_URL = "https://educonnect.education.gouv.fr/api/userinfo"

# --- BASE DE DONNÉES SIMPLIFIÉE ---
USERS = {}

@app.get("/")
def home():
    return {"message": "Bienvenue sur l’API Studiix"}

# --- ETAPE 1 : Redirection vers EduConnect ---
@app.get("/auth/educonnect")
def auth_educonnect():
    # Redirige l'utilisateur vers EduConnect
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid profile",
    }
    url = f"{AUTH_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=openid%20profile"
    return RedirectResponse(url)

# --- ETAPE 2 : Callback d’EduConnect ---
@app.get("/callback")
def callback(code: str):
    # Échange le code contre un access_token
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    token_resp = requests.post(TOKEN_URL, data=data)
    token_data = token_resp.json()

    if "access_token" not in token_data:
        return JSONResponse({"error": "Erreur de connexion à EduConnect", "details": token_data}, status_code=400)

    access_token = token_data["access_token"]

    # Récupération des infos utilisateur
    headers = {"Authorization": f"Bearer {access_token}"}
    user_resp = requests.get(USER_URL, headers=headers)
    user_data = user_resp.json()

    # Crée un token interne pour Studiix
    studiix_token = secrets.token_hex(16)
    USERS[studiix_token] = user_data

    # Redirige vers ton app mobile Expo
    redirect = f"studiix://callback?token={studiix_token}"
    return RedirectResponse(redirect)

# --- ETAPE 3 : Récupérer les infos de l’utilisateur ---
@app.get("/me")
def me(token: str):
    if token not in USERS:
        return JSONResponse({"error": "Token invalide"}, status_code=401)
    return USERS[token]
