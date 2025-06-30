document.addEventListener("DOMContentLoaded", () => {
    const userInfo = document.getElementById("user-info");
    const logoutButton = document.getElementById("logout-button");

    // Logout button listener
    logoutButton.addEventListener("click", async (e) => {
        e.preventDefault();

        try {
            // Call backend logout
            const res = await fetch("/api/logout", {
                method: "POST",
                credentials: "include",
            });

            if (!res.ok) {
                throw new Error("Logout failed");
            }

            // Reset score on backend
            await fetch("/api/quiz/reset", {
                method: "POST",
                credentials: "include",
            });

            // Clear local storage
            localStorage.removeItem("score");
            localStorage.removeItem("token");

            // Redirect to login page only after all is done
            window.location.assign("/login");
        } catch (err) {
            console.error("Logout failed or server not reachable", err);
        }

    });

    // Call the backend API to get user info using cookie authentication
    fetch("/api/username", {
        method: "GET",
        credentials: "include"  // VERY IMPORTANT: send cookies with the request
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Unauthorized or error fetching user info");
            }
            return response.json();
        })
        .then(data => {
            // data is the user object returned from /api/username
            if (userInfo) {
                userInfo.textContent = `Logged in as: ${data.username}`;
            }
            if (logoutButton) {
                logoutButton.style.display = "inline-block";
            }
        })
        .catch(err => {
            console.error("Error fetching user info:", err);
            // optionally redirect to login or show a message
        });
});
