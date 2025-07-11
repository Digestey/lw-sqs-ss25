document.addEventListener("DOMContentLoaded", function () {
    if (!window.location.pathname.startsWith("/quiz")) {
        localStorage.removeItem("score");
    }
    const form = document.querySelector("form");
    const messageBox = document.getElementById("quiz-message");
    const scoreDisplay = document.getElementById("score-display");
    const scoreValue = document.getElementById("score-value");
    const submitScoreButton = document.getElementById("submit-score-button");
    const submitGuessButton = document.getElementById("submit-guess-button");
    const nextQuestionButton = document.getElementById("next-question-button");
    const guessInput = form.querySelector('input[name="guess"]');
    let score = parseInt(localStorage.getItem("score")) || 0;


    document.getElementById("reset-score-button").addEventListener("click", async () => {
        try {
            if (score == 0) {
                return;
            }
            const res = await fetch("/api/quiz/reset", {
                method: "POST",
            });
            const data = await res.json();
            if (res.ok) {
                score = data.score;  // Update local JS variable
                localStorage.setItem("score", score);
                scoreValue.textContent = data.score;
                messageBox.textContent = data.message;
                scoreDisplay.style.display = "block";
            } else {
                messageBox.textContent = data.error || "Failed to reset score.";
            }
        } catch (err) {
            console.error("Error resetting score:", err);
            messageBox.textContent = "Unexpected error occurred.";
        }
    });

    // Show score and submit score button always
    scoreDisplay.style.display = "block";
    submitScoreButton.style.display = "inline-block";

    let serverScore = parseInt(scoreValue.textContent);
    if (!isNaN(serverScore)) {
        localStorage.setItem("score", serverScore);
    }

    // Load score from localStorage if you want, else rely on backend state

    scoreValue.textContent = score;

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const formData = new FormData(form);

        try {
            const response = await fetch("/api/quiz", {
                method: "POST",
                body: formData,
                credentials: "include"  // <-- important to send cookies!
            });

            const data = await response.json();

            if (data.correct) {
                messageBox.textContent = data.message;
                messageBox.style.color = "green";

                if (typeof data.score === "number") {
                    score = data.score;
                    scoreValue.textContent = score;
                    localStorage.setItem("score", score); // Optional: keep local copy
                }

                guessInput.disabled = true;
                submitGuessButton.disabled = true;
                nextQuestionButton.style.display = "inline-block";
            } else {
                messageBox.textContent = data.message || "Incorrect guess.";
                messageBox.style.color = "red";

                if (data.hint) {
                    messageBox.textContent += " Hint: " + data.hint;
                }
            }
        } catch (err) {
            messageBox.textContent = "Error submitting guess. Try again.";
            messageBox.style.color = "red";
            console.error("Error in quiz POST:", err);
        }
    });

    nextQuestionButton.addEventListener("click", async function () {
        try {
            const response = await fetch("/api/next_quiz", {
                method: "POST",
                credentials: "include"  // Send session cookie
            });

            if (response.ok) {
                // Reset form state
                guessInput.disabled = false;
                submitGuessButton.disabled = false;
                guessInput.value = "";
                messageBox.textContent = "";
                nextQuestionButton.style.display = "none";

                window.location.assign("/quiz");
            } else {
                const data = await response.json();
                alert(data.error || "Failed to load next question.");
            }
        } catch (err) {
            console.error("Failed to load next question:", err);
            alert("Error loading next quiz.");
        }
    });

    submitScoreButton.addEventListener("click", async function () {
        try {
            const response = await fetch("/api/highscore", {
                method: "POST",
                credentials: "include",  // <-- send cookies here too
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({})
            });

            if (!response.ok) {
                if (response.status === 401) {
                    alert("You must be logged in to submit a score.");
                } else {
                    alert("Failed to submit highscore.");
                }
                return;
            }

            alert("Highscore submitted!");
            score = 0;
            scoreValue.textContent = score;
            localStorage.setItem("score", score); // Reset local copy
        } catch (err) {
            console.error("Submit failed:", err);
            alert("Failed to submit highscore.");
        }
    });
});