from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import secrets

app = FastAPI(title="Studiix Backend")

# autoriser ton appli mobile Expo / web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# stockage en mémoire pour la démo
TOKENS = {}

@app.get("/")
def home():
    return {"message": "Studiix API active 🚀"}

@app.get("/auth/educonnect")
def auth_educonnect(redirect_uri: str):
    """
    Simule un login EduConnect et redirige vers Studiix://callback?token=...
    """
    fake_token = secrets.token_hex(16)
    TOKENS[fake_token] = {"name": "Jean Dupont", "email": "jean.dupont@ecole.fr"}
    redirect_url = f"{redirect_uri}?token={fake_token}"
    return RedirectResponse(url=redirect_url)

@app.get("/me")
def me(request: Request):
    auth = request.headers.get("authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth.split(" ")[1]
    user = TOKENS.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return JSONResponse(content=user)
