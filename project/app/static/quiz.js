document.addEventListener("DOMContentLoaded", async function () {
  const form = document.querySelector("form");
  const messageBox = document.getElementById("quiz-message");
  const scoreDisplay = document.getElementById("score-display");
  const scoreValue = document.getElementById("score-value");
  const submitScoreButton = document.getElementById("submit-score-button");
  const submitGuessButton = document.getElementById("submit-guess-button");
  const nextQuestionButton = document.getElementById("next-question-button");
  const guessInput = form.querySelector('input[name="guess"]');

  // Show score and submit score button always
  scoreDisplay.style.display = "block";
  submitScoreButton.style.display = "inline-block";

  // Load quiz state from backend API
  async function loadQuizState() {
    try {
      const res = await fetch('/api/quiz_state', { credentials: 'include' });
      if (res.ok) {
        const state = await res.json();
        updateUI(state);
      } else if (res.status === 400) {
        // No session -> start quiz (redirect handled by backend)
        await fetch('/api/start_quiz', { method: 'GET', credentials: 'include' });
        // Reload quiz state after session created
        await loadQuizState();
      } else {
        throw new Error("Failed to load quiz state");
      }
    } catch (err) {
      console.error("Error loading quiz state:", err);
      messageBox.textContent = "Failed to load quiz. Please try refreshing.";
      messageBox.style.color = "red";
    }
  }

  function updateUI(state) {
    // Show score from backend
    const score = state.score || 0;
    scoreValue.textContent = score;

    // Show Pokémon info somewhere in your UI (customize as needed)
    // For example, assuming you have an element with id 'pokemon-name'
    const pokemonNameElem = document.getElementById('pokemon-name');
    if (pokemonNameElem && state.name) {
      pokemonNameElem.textContent = state.name;
    }

    // Reset form and buttons if needed
    guessInput.disabled = false;
    submitGuessButton.disabled = false;
    guessInput.value = "";
    messageBox.textContent = "";
    messageBox.style.color = "black";
    nextQuestionButton.style.display = "none";
  }

  form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new FormData(form);

    try {
      const response = await fetch("/api/quiz", {
        method: "POST",
        body: formData,
        credentials: "include"
      });

      const data = await response.json();

      if (data.correct) {
        messageBox.textContent = data.message;
        messageBox.style.color = "green";

        // Update score display from backend
        if (typeof data.score === "number") {
          scoreValue.textContent = data.score;
        }

        guessInput.disabled = true;
        submitGuessButton.disabled = true;
        nextQuestionButton.style.display = "inline-block";
      } else {
        messageBox.textContent = data.message || "Incorrect guess.";
        messageBox.style.color = "red";

        if (data.hint) {
          messageBox.textContent += " Hint: " + data.hint;
        }
      }
    } catch (err) {
      messageBox.textContent = "Error submitting guess. Try again.";
      messageBox.style.color = "red";
      console.error("Error in quiz POST:", err);
    }
  });

  nextQuestionButton.addEventListener("click", async function () {
    try {
      const response = await fetch("/api/next_quiz", {
        method: "POST",
        credentials: "include"
      });

      if (response.ok) {
        // Fetch and update the quiz state dynamically instead of reloading the page
        await loadQuizState();
      } else {
        const data = await response.json();
        alert(data.error || "Failed to load next question.");
      }
    } catch (err) {
      console.error("Failed to load next question:", err);
      alert("Error loading next quiz.");
    }
  });

  submitScoreButton.addEventListener("click", async function () {
    try {
      const response = await fetch("/api/highscore", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
      });

      if (!response.ok) {
        if (response.status === 401) {
          alert("You must be logged in to submit a score.");
        } else {
          alert("Failed to submit highscore.");
        }
        return;
      }

      alert("Highscore submitted!");
      // Reset score display to 0 after submission
      scoreValue.textContent = "0";
    } catch (err) {
      console.error("Submit failed:", err);
      alert("Failed to submit highscore.");
    }
  });

  // On page load, fetch initial quiz state
  await loadQuizState();
});
