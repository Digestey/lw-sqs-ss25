document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("login-form");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);

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
      window.location.href = "/"; // Optional redirect after login
    } catch (error) {
      alert(error.message);
    }
  });
});