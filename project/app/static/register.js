const MIN_PW_LENGTH = 8;
const MIN_USERNAME_LENGTH = 5;
const MAX_STRING_LENGTH = 100;

function username_check(username) {
  if (username.length < MIN_USERNAME_LENGTH || username.length > MAX_STRING_LENGTH) {
    return false;
  }
  return true
}

function password_check(password) {
  if (password.length < MIN_PW_LENGTH || password.length > MAX_STRING_LENGTH) {
    return false;
  }
  return true;

}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("register-form");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);

    const password = formData.get("password");

    if (!(username_check(formData.get("username")) || password_check(password))) {
      alert("Login failed: Username and Password requirements are not met. Username must be longer than 5 characters and password must be longer than 8 characters. Neither can exceed 100 characters.")
      return;
    }

    const repeatPassword = formData.get("repeat_password");

    // console.log(password)
    // console.log(repeatPassword)

    if (password !== repeatPassword) {
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
      window.location.href = "/"; // Optional redirect
    } catch (error) {
      alert("Error: " + error.message);
    }
  });
});
