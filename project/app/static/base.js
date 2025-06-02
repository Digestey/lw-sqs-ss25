document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");
    const userInfo = document.getElementById("user-info");
    const logoutButton = document.getElementById("logout-button");

    // Always add the logout listener, regardless of token
    if (logoutButton) {
        logoutButton.addEventListener("click", (e) => {
            e.preventDefault(); // Prevent form-like behavior if ever used that way
            localStorage.removeItem("token");
            window.location.assign("/login");
        });
    }

    // Only update UI if token is valid
    if (token && userInfo) {
        try {
            const payload = JSON.parse(atob(token.split(".")[1]));
            const username = payload.sub;

            userInfo.textContent = `Logged in as: ${username}`;
            if (logoutButton) logoutButton.style.display = "inline-block";
        } catch (err) {
            console.error("Invalid token:", err);
        }
    }
});
