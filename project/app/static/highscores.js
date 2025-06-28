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
        highscoresList.innerHTML = "";  // clear old content

        data.forEach(score => {
            const tr = document.createElement("tr");

            const usernameTd = document.createElement("td");
            usernameTd.textContent = score.username;

            const scoreTd = document.createElement("td");
            scoreTd.textContent = score.score;

            tr.appendChild(usernameTd);
            tr.appendChild(scoreTd);

            highscoresList.appendChild(tr);
        });
    } catch (err) {
        console.error("Error loading highscores:", err);
        alert("Failed to load highscores.");
    }
});
