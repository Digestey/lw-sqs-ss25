const MIN_PW_LENGTH = 8;
const MIN_USERNAME_LENGTH = 5;
const MAX_STRING_LENGTH = 100;

function username_check(username) {
  return !(username.length < MIN_USERNAME_LENGTH || username.length > MAX_STRING_LENGTH);
}

function password_check(password) {
  return !(password.length < MIN_PW_LENGTH || password.length > MAX_STRING_LENGTH);
}

function constantTimeEquals(a, b) {
  if (a.length !== b.length) return false;
  let result = 0;
  for (let i = 0; i < a.length; i++) {
    result |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return result === 0;
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("register-form");

  console.log("Register.js loaded")

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);

    const username = formData.get("username");
    const password = formData.get("password");

    if (formData.get("password").length < 1 || formData.get("username") < 1) {
      throw new Error("Those fields are empty, m'lardy")
    }

    if (!(username_check(username) || password_check(password))) {
      alert("Login failed: Username and Password requirements are not met. Username must be longer than 5 characters and password must be longer than 8 characters. Neither can exceed 100 characters.")
      return;
    }

    const repeatPassword = formData.get("repeat_password");

    if (!constantTimeEquals(password, repeatPassword)) {
      alert("Passwords do not match.");
      return;
    }

    const payload = {
      username: formData.get("username"),
      password: password,
    };

    try {
      const response = await fetch("/api/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Registration failed");
      }

      await response.json();

      alert("Registration successful!");
      window.location.assign("/login");
    } catch (error) {
      alert("Error: " + error.message);
    }
  });
});
