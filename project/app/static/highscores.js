document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("token");

    if (!token) {
        console.error("No token found");
        window.location.assign("/login");
        return;
    }

    try {
        const response = await fetch("/api/highscore/10", {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });

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
    }
});
