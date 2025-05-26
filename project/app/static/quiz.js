

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const messageBox = document.getElementById("quiz-message");
    const scoreDisplay = document.getElementById("score-display");
    const scoreValue = document.getElementById("score-value");
    const submitButton = document.getElementById("submit-score-button");

    let score = parseInt(localStorage.getItem("currentScore")) || 0;
    updateScoreDisplay();

    function updateScoreDisplay() {
        scoreDisplay.style.display = score > 0 ? "block" : "none";
        submitButton.style.display = score > 0 ? "inline-block" : "none";
        scoreValue.textContent = score;
    }

    const logoutButton = document.getElementById("logout-button");
    if (logoutButton) {
        logoutButton.addEventListener("click", () => {
            localStorage.removeItem("token");
            localStorage.removeItem("currentScore");
            window.location.href = "/";
        });
    }

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const formData = new FormData(form);
        const response = await fetch("/quiz", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (data.correct) {
            messageBox.textContent = data.message;
            messageBox.style.color = "green";

            // Increase score
            score = score + 25;
            localStorage.setItem("currentScore", score);
            updateScoreDisplay();

            // Get a new Pokémon
            setTimeout(() => window.location.reload(), 1500);
        } else {
            messageBox.textContent = data.message;
            messageBox.style.color = "red";
        }
    });

    submitButton.addEventListener("click", async function () {
        const token = localStorage.getItem("token");
        if (!token) {
            alert("You must be logged in to submit a score.");
            return;
        }

        try {
            const response = await fetch("/api/highscore", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ score: score })
            });

            if (!response.ok) throw new Error("Failed to submit highscore");

            alert("Highscore submitted!");
            score = 0;
            localStorage.removeItem("currentScore");
            updateScoreDisplay();
        } catch (err) {
            console.error("Submit failed:", err);
            alert("Failed to submit highscore.");
        }
    });
});
