const MIN_USERNAME_LENGTH = 5;
const MIN_PW_LENGTH = 8;
const MAX_STRING_LENGTH = 100;

function validateCredentials(username, password) {
  if (!username || !password) {
    throw new Error("Those fields are empty, m'lardy");
  }

  const tooShort = username.length < MIN_USERNAME_LENGTH || password.length < MIN_PW_LENGTH;
  const tooLong = username.length > MAX_STRING_LENGTH || password.length > MAX_STRING_LENGTH;

  if (tooShort || tooLong) {
    alert(
      "Login failed: Username must be at least 5 characters and password at least 8. Neither can exceed 100 characters."
    );
    return false;
  }
  return true;
}

document.addEventListener("cr_account", function () {
  window.location.assign("/register");
})

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("login-form");

  async function handleLogin(formData) {
    const response = await fetch("/api/token", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => null);
      throw new Error(errorBody?.detail || "Login failed");
    }

    alert("Login successful!");
    window.location.assign("/");
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const username = formData.get("username") || "";
    const password = formData.get("password") || "";

    if (!validateCredentials(username, password)) return;

    try {
      await handleLogin(formData);
    } catch (error) {
      alert(error.message);
    }
  });
});
