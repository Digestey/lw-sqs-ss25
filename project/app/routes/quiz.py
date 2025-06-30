import uuid
from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import JSONResponse, RedirectResponse

from app.services.pokemon_service import fetch_pokemon
from app.services.redis_service import get_state, set_state

from app.util.logger import get_logger

logger = get_logger("quiz_router")
router = APIRouter()


@router.get("/api/start_quiz")
async def start_quiz(response: Response):
    """Starts a new quiz session and redirects to the quiz page.

    A unique session ID is generated and stored in an HTTP-only cookie.
    The user is redirected to the `/quiz` frontend route.

    Args:
        response (Response): The response object used to set cookies and redirect.

    Returns:
        RedirectResponse: A 302 redirect response to the quiz page with the session cookie set.
    """
    quiz_session_id = str(uuid.uuid4())
    response = RedirectResponse(url="/quiz", status_code=302)
    response.set_cookie(
        key="quiz_session_id",
        value=quiz_session_id,
        httponly=True,
        max_age=1800,  # 30 minutes expiry
        path="/"
    )
    return response


@router.post("/api/next_quiz", response_class=JSONResponse)
async def next_quiz(request: Request):
    """Prepares the next quiz question and updates session state.

    Retrieves the user's current quiz session via cookie, preserves the current score,
    fetches a new Pokémon, and stores it in the session state.

    Args:
        request (Request): The incoming request containing cookies for session tracking.

    Returns:
        JSONResponse: A success message if a session exists, or an error message if not.
    """
    session_id = request.cookies.get("quiz_session_id")
    if session_id is None:
        return JSONResponse(status_code=400, content={"error": "No quiz session found"})

    current_state = get_state(session_id)
    score = current_state.get("score", 0) if current_state else 0

    new_pokemon = fetch_pokemon(logger)
    state = new_pokemon.__dict__
    state["score"] = score
    set_state(session_id, state)

    return {"message": "New quiz loaded."}


def get_or_create_session_id(request: Request) -> str:
    return request.cookies.get("quiz_session_id") or str(uuid.uuid4())


def get_or_init_state(session_id: str) -> dict:
    state = get_state(session_id)
    if not state:
        pokemon = fetch_pokemon(logger)
        state = pokemon.__dict__
        state["score"] = 0
        set_state(session_id, state)
    return state


def create_correct_response(score: int) -> JSONResponse:
    return JSONResponse(content={
        "correct": True,
        "message": "Ding Ding Ding! We have a winner!",
        "score": score
    })


def create_incorrect_response(score: int) -> JSONResponse:
    return JSONResponse(content={
        "correct": False,
        "message": "That is incorrect. Another hint has been added to the entry.",
        "hint": "",
        "score": score
    })


def set_session_cookie(response: JSONResponse, session_id: str):
    response.set_cookie(
        key="quiz_session_id",
        value=session_id,
        max_age=1800,
        httponly=True,
        samesite="lax",
        path="/"
    )


@router.post("/api/quiz", response_class=JSONResponse)
async def post_quiz(request: Request, guess: str = Form(...)):
    """Processes the user's guess and updates the quiz session.

    Checks the submitted answer against the correct Pokémon name.
    Updates the score on a correct guess and prepares hints for incorrect guesses.
    Initializes a new session if none exists.

    Args:
        request (Request): The incoming request containing the session cookie and form data.
        guess (str): The user's guess, submitted via form input.

    Returns:
        JSONResponse: A response indicating whether the guess was correct,
        the updated score, and optional hints.
    """
    session_id = get_or_create_session_id(request)
    state = get_or_init_state(session_id)

    guess = guess.strip().lower()
    correct_answer = state["name"].lower()
    score = state.get("score", 0)

    if guess == correct_answer:
        score += 25
        state["score"] = score
        set_state(session_id, state)
        response = create_correct_response(score)
    else:
        set_state(session_id, state)
        response = create_incorrect_response(score)

    if "quiz_session_id" not in request.cookies:
        set_session_cookie(response, session_id)

    return response

@router.post("/api/quiz/reset", response_class=JSONResponse)
async def reset_quiz_score(request: Request):
    """
    Resets the current quiz score in the session.

    Args:
        request (Request): The incoming request with session cookie.

    Returns:
        JSONResponse: A message confirming the score has been reset.
    """
    session_id = request.cookies.get("quiz_session_id")
    if not session_id:
        return JSONResponse(status_code=400, content={"error": "No quiz session found"})

    state = get_state(session_id)
    if not state:
        return JSONResponse(status_code=404, content={"error": "Quiz session state not found"})

    state["score"] = 0
    set_state(session_id, state)

    return JSONResponse(content={"message": "Quiz score has been reset.", "score": 0})