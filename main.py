from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Lost & Found ENSAM Rabat")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def page_inscription(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="inscription.html",
        context={"active_page": "accueil"}
    )

@app.get("/accueil")
def page_accueil(request: Request):
    utilisateur = {
        "prenom": "Étudiant",
        "nom": "ENSAM",
        "email": "etudiant@ensam-rabat.ac.ma",
        "telephone": "0600000000"
    }
    return templates.TemplateResponse(
        request=request, 
        name="accueil.html", 
        context={"user": utilisateur}
    )

@app.get("/perdu")
def page_perdu(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="perdu.html"
    )

@app.get("/trouve")
def page_trouve(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="trouve.html"
    )