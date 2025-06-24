document.addEventListener("DOMContentLoaded", async () => {
    try {
        const response = await fetch("/api/highscore/10", {
            credentials: "include" 
        });

        if (response.status === 401) {
            console.error("Unauthorized: redirecting to login.");
            window.location.assign("/login");
            return;
        }

        const data = await response.json();
        console.log("Received scores:", data);

        if (!Array.isArray(data)) {
            throw new Error("Expected array, got: " + JSON.stringify(data));
        }

        const highscoresList = document.getElementById("highscores-list");
        data.forEach(score => {
            const li = document.createElement("li");
            li.textContent = `${score.username}: ${score.score}`;
            highscoresList.appendChild(li);
        });
    } catch (err) {
        console.error("Error loading highscores:", err);
        alert("Failed to load highscores.");
    }
});
