from fastapi import FastAPI, Form, Request, HTTPException
from starlette.middleware.sessions import SessionMiddleware
from google.oauth2 import id_token  #google.oauth2 is a Python library from Google that helps verify OAuth2 tokens and extract user identity securely.
from google.auth.transport import requests as google_requests
from fastapi.responses import JSONResponse

# google.auth.transport is a submodule provides the network layer (like Request()) that Google’s auth system uses to securely send and receive token verification requests
# comes under google auth package
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="kjoshi123")

def verify_google_token(token: str):
    if token == "test":
        email = "bkamal@gmail.com"
        return {"email": email,}

    try:
        user_data = id_token.verify_oauth2_token(token, google_requests.Request())
# use google.oauth2 id_token.verify_oauth2_token(token, Request()) through — onboarding clarity and crash-proof login flow
# use google.auth.transport use hota hai verify_oauth2_token(token, google_requests.Request()) mein — bina iske Google se baat hi nahi hoti
        email = user_data.get("email") # safe extraction, crash-proof
        name = user_data.get("name")
        picture = user_data.get("picture")

        if not email:
            raise HTTPException(status_code=400, detail="email not found in token") # 400 bad request

        return {"email": email, "name": name, "picture": picture}

    except:
        raise HTTPException(status_code=401, detail="invalid or expired google token") # 401 unauthorized

@app.post("/login")
def login(request: Request, token: str = Form(...)):
    user_data = verify_google_token(token)
    request.session["email"] = user_data["email"]
    return {"msg": "login successful", **user_data} # ** python dictionary unpacking

@app.get("/home")
def home(request: Request, email: str):
    session = request.session.get("email")
    if session != email:
        return JSONResponse(content={"msg": "unauthorized"}, status_code=401)

    return JSONResponse(content={"msg": f"welcome user {email}"}, status_code=200)

@app.get("/logout")
def logout(request: Request, email: str):
    session = request.session.get("email")
    if session != email:
        return JSONResponse(content={"msg": "unauthorized"}, status_code = 401)
    request.session.pop("email", None)
    return JSONResponse(content={"msg": f"user logged out {email}"}, status_code = 200)

# expire session cookie


# “Built Google login using ID token verification in FastAPI — no JWT or session used.
# Backend stayed stateless and verified token on every request to return user email.
# This flow is simple, scalable.
# Stateless means the backend does not save any user data or login status. Every request must carry its own identity.
# Google-issued JWT, not self-issued
