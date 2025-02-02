// main.js

document.addEventListener("DOMContentLoaded", function() {
    console.log("JavaScript loaded!");

    // Example: Adding an event listener to a button if available
    const analyzeButton = document.querySelector("button[type='submit']");
    if (analyzeButton) {
        analyzeButton.addEventListener("click", function(event) {
            alert("Analysis is starting... Please wait.");
        });
    }
});
document.addEventListener("DOMContentLoaded", function() {
    console.log("JavaScript loaded!");

    const coin = document.getElementById("coin");

    // Example: Toggle spin animation when the coin is clicked.
    coin.addEventListener("click", function() {
        // If the coin has the animation, remove it; otherwise, add it.
        if (coin.style.animationPlayState === "paused") {
            coin.style.animationPlayState = "running";
        } else {
            coin.style.animationPlayState = "paused";
        }
    });
});