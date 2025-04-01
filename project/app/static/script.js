document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const input = document.querySelector("input[name='guess']");
    const messageBox = document.createElement("p");  // Create message box
    form.appendChild(messageBox);

    form.addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent page reload

        const formData = new FormData(form);
        const response = await fetch("/quiz", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (data.correct) {
            messageBox.textContent = data.message;
            messageBox.style.color = "green";
            setTimeout(() => window.location.reload(), 2000); // Reload after 2s
        } else {
            messageBox.textContent = data.message;
            messageBox.style.color = "red";

            // Show the next hint
            if (data.hint && data.hint.length > 0) {
                const hintContainers = document.querySelectorAll(".pokedex-container div");
                for(container in hintContainers) {
                    console.log(container)
                }
                if (data.hint.length <= hintContainers.length) {
                    hintContainers[data.hint.length - 1].style.visibility = "visible";
                }
            }
        }
    });
});
