workspace {

    model {
        user = person "User" {
            description "A player who plays the DexQuiz."
        }

        dexquiz = softwareSystem "DexQuiz" {
            description "A web-based Pokémon quiz application with authentication and highscores."

            frontend = container "Frontend (HTML + JS)" {
                technology "HTML, JavaScript"
                description "The user interface for the quiz game."
            }

            backend = container "FastAPI Backend" {
                technology "Python + FastAPI"
                description "Handles all application logic and API endpoints."

                api = component "API Routes" {
                    description "Handles HTTP routing for user actions, highscores, quiz."
                    technology "FastAPI"
                }

                auth = component "Authentication Service" {
                    description "Manages registration, login, JWT tokens, and password hashing."
                    technology "Python (bcrypt, jose)"
                }

                db = component "Database Service" {
                    description "Handles MySQL connection pooling and queries."
                    technology "mysql-connector-python"
                }

                quiz = component "Quiz Service" {
                    description "Fetches Pokémon data and builds quiz logic."
                    technology "pokebase"
                }

                api -> auth "Uses"
                api -> db "Uses"
                api -> quiz "Uses"
            }

            database = container "MySQL Database" {
                technology "MySQL"
                description "Stores users and highscores."
            }

            backend -> database "Reads and writes users and highscores"
        }

        pokebase = softwareSystem "PokéBase API" {
            description "External API used to retrieve Pokémon data."
        }

        user -> frontend "Uses via web browser"
        frontend -> backend "Sends requests to"
        quiz -> pokebase "Fetches Pokémon data from"

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
