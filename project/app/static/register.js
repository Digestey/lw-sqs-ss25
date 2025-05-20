document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("register-form");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const password = formData.get("password");
    const repeatPassword = formData.get("repeat_password");

    console.log(password)
    console.log(repeatPassword)

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