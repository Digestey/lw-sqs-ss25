workspace {

    model {
        user = person "User" {
            description "A player who plays the DexQuiz."
        }

        dexquiz = softwareSystem "DexQuiz" {
            description "A web-based Pokémon quiz application with authentication, session management, and highscores."

            frontend = container "Frontend (HTML + JS)" {
                technology "HTML, JavaScript"
                description "The user interface for the quiz game."
                
                ui = component "UI Layer" {
                    technology "HTML, CSS, JavaScript"
                    description "Renders the quiz interface and handles user interaction."
                }

                state_management = component "State Management" {
                    technology "JavaScript (e.g., localStorage, Redux)"
                    description "Manages application state, including quiz progress and session data."
                }

                session_manager = component "Session & Cookie Manager" {
                    technology "JavaScript"
                    description "Manages JWT tokens and cookies to keep users authenticated."
                }

                api_client = component "API Client" {
                    technology "JavaScript (fetch, axios)"
                    description "Handles HTTP requests to the backend API."
                }

                ui -> state_management "Reads and updates"
                ui -> session_manager "Uses for auth state"
                ui -> api_client "Sends requests through"
                api_client -> session_manager "Uses tokens for authorization"
            }

            backend = container "FastAPI Backend" {
                technology "Python + FastAPI"
                description "Handles all application logic and API endpoints."

                api = component "API Routes" {
                    description "Handles HTTP routing for user actions, highscores, quiz, and session management."
                    technology "FastAPI"
                }

                auth = component "Authentication Service" {
                    description "Manages registration, login, JWT tokens, password hashing, and cookie-based session handling."
                    technology "Python (bcrypt, jose)"
                }

                db = component "Database Service" {
                    description "Handles MySQL connection pooling and queries."
                    technology "mysql-connector-python"
                }

                quiz = component "Pokemon Service" {
                    description "Fetches Pokémon data, builds quiz logic, and manages temporary quiz state and scores."
                    technology "pokebase, Redis"
                }

                redis = component "Redis Service" {
                    description "Manages temporary storage of quiz state and user scores during quiz participation."
                    technology "Redis"
                }

                api -> auth "Uses for authentication, JWT & sessions"
                api -> db "Uses for persistent data (users, highscores)"
                api -> quiz "Uses for quiz logic & Pokémon data"
                quiz -> redis "Uses for temporary quiz state & scoring"
                auth -> redis "Uses for session storage (if applicable)"
            }

            database = container "MySQL Database" {
                technology "MySQL"
                description "Stores persistent user data and highscores."
            }

            redis_db = container "Redis Cache" {
                technology "Redis"
                description "Temporary storage for quiz states and user session scores."
            }

            backend -> database "Reads and writes persistent user and highscore data"
            backend -> redis_db "Reads and writes temporary quiz states and scores"

        }

        pokebase = softwareSystem "PokéBase API" {
            description "External API used to retrieve Pokémon data."
        }

        user -> frontend "Uses via web browser"
        frontend -> backend "Sends requests to"
        quiz -> pokebase "Fetches Pokémon data from"
        backend -> redis_db "Uses for quiz state & session score storage"
    }

    views {
        systemContext dexquiz {
            include *
            autolayout lr
            title "System Context - DexQuiz"
        }

        container dexquiz {
            include *
            autolayout lr
            title "Container View - DexQuiz"
        }

        component backend {
            include *
            autolayout lr
            title "Component View - FastAPI Backend"
        }

        theme default
    }
}
