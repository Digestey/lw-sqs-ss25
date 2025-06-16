"""
Module frontend: Defines all routes that are part of this applications frontend.
"""

import os
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.pokemon_service import fetch_pokemon
from app.util.logger import get_logger

router = APIRouter()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "..", "templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)
logger = get_logger("Frontend")

# In-memory session store (basic)
sessions = {}


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home site.

    Args:
        request (Request): request body

    Returns:
        TemplateResponse: Returns the HTML Template to be displayed in the clients browser.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    """Route for the login-frontend

    Args:
        request (Request): request body

    Returns:
        TemplateResponse: HTML to be displayed in the browser
    """
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    """Register Route. Provides the frontend to give users the opportunity to sell their
       soul to this website.
    
    Args:
        request (Request): Request

    Returns:
        TemplateResponse: The HTML Template to be displayed
    """
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/highscores", response_class=HTMLResponse)
async def highscore_page(request: Request):
    """Highscores Page. Can only be accessed if the user is logged in.
       That is handled in the js code however.

    Args:
        request (Request): reqeust body

    Returns:
        HTMLResponse: Highscores Page to be displayed in the browser.
    """
    return templates.TemplateResponse("highscores.html", {
        "request": request
    })


@router.get("/quiz", response_class=HTMLResponse)
async def get_quiz(request: Request):
    """Quiz frontend route. Fetches first pokemon
    Args:
        request (Request): 

    Returns:
        HTMLResponse: Quiz page to be displayed in the browser.
    """
    session_id = request.client.host
    if session_id not in sessions:
        sessions[session_id] = fetch_pokemon(logger)

    pokemon_info = sessions[session_id]

    return templates.TemplateResponse(
        "quiz.html",
        {
            "request": request,
            "message": "",
            "reload": False,
            "pokemon": pokemon_info
        }
    )


@router.post("/quiz", response_class=JSONResponse)
async def post_quiz(request: Request, guess: str = Form(...)):
    """Fetches a new Quiz question, and validates existing ones.

    Args:
        request (Request): request (form data from the ui form)
        guess (str, optional): String. Defaults to Form(...).

    Returns:
        JSONResponse: Evaluated response if the guess was correct (and the message to be displayed)
    """
    session_id = request.client.host
    if session_id not in sessions:
        sessions[session_id] = fetch_pokemon(logger)

    pokemon_info = sessions[session_id]
    correct_answer = pokemon_info.name.lower()
    guess = guess.strip().lower()

    if guess == correct_answer:
        del sessions[session_id]
        return JSONResponse(content={
            "correct": True,
            "message": "Ding Ding Ding! We have a winner!"
        })

    return JSONResponse(content={
        "correct": False,
        "message": "That is incorrect. Another hint has been added to the entry.",
        "hint": ""  # remainder of the original plan
    })
