const MIN_USERNAME_LENGTH = 4;
const MIN_PW_LENGTH = 8;
const MAX_STRING_LENGTH = 100;

function username_check(username) {
  return !(username.length < MIN_USERNAME_LENGTH || username.length > MAX_STRING_LENGTH);
}

function password_check(password) {
  return !(password.length < MIN_PW_LENGTH || password.length > MAX_STRING_LENGTH);
}

document.addEventListener("cr_account", function () {
    window.location.href = "/register"
})

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("login-form");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);

    if (formData.get("password").length < 1 || formData.get("username") < 1) {
      throw new Error("Those fields are empty, m'lardy")
    }

    if (!(username_check(formData.get("username")) || password_check(password))) {
      alert("Login failed: Username and Password requirements are not met. Username must be longer than 5 characters and password must be longer than 8 characters. Neither can exceed 100 characters.")
      return;
    }


    try {
      const response = await fetch("/api/token", {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        throw new Error("Login failed");
      }

      const data = await response.json();
      localStorage.setItem("token", data.access_token);

      alert("Login successful!");
      window.location.href = "/"; // redirect to main Page after login
    } catch (error) {
      alert(error.message);
    }
  });
});
