
// MATCH RATINGS — JavaScript

 
// Generate rating buttons 1–10 for every player card
function createRatingButtons() {
    let html = '<div class="btn-group flex-wrap">';
    for (let i = 1; i <= 10; i++) {
        html += `<button class="btn rating-btn">${i}</button>`;
    }
    html += '</div>';
    return html;
}
 
document.querySelectorAll(".rating-buttons").forEach(container => {
    container.innerHTML = createRatingButtons();
});
 
 
// ── Click Handler (rating buttons + MOTM) ──
document.addEventListener("click", function (e) {
 
    // Rating button clicked
    if (e.target.classList.contains("rating-btn")) {
        const group = e.target.closest(".rating-buttons");
        group.querySelectorAll(".rating-btn").forEach(btn => {
            btn.classList.remove("rating-selected");
        });
        e.target.classList.add("rating-selected");
    }
 
    // MOTM button clicked
    if (e.target.closest(".motm-btn")) {
        document.querySelectorAll(".motm-btn").forEach(btn => {
            btn.classList.remove("btn-warning");
            btn.classList.add("btn-light");
            const icon = btn.querySelector("i");
            icon.classList.remove("bi-star-fill");
            icon.classList.add("bi-star");
        });
 
        const selectedBtn = e.target.closest(".motm-btn");
        selectedBtn.classList.remove("btn-light");
        selectedBtn.classList.add("btn-warning");
 
        const star = selectedBtn.querySelector("i");
        star.classList.remove("bi-star");
        star.classList.add("bi-star-fill");
    }
});
 
 
// ── Chart instance ──
let chart;
 
 
// ── Reset ──
$("#reset-ratings").click(function () {
    $(".rating-btn").removeClass("rating-selected");
    $(".motm-btn").removeClass("btn-warning").addClass("btn-light");
    $(".motm-btn i").removeClass("bi-star-fill").addClass("bi-star");
    $("#average-rating").text("0");
    $("#motm-display").text("");
    $("#no-data-message").show();
    if (chart) chart.destroy();
});
 
 
// ── Submit Ratings ──
$("#submit-ratings").click(function () {
    let ratings = [];
 
    $(".rating-buttons").each(function () {
        const selected = $(this).find(".rating-selected").text();
        if (selected) ratings.push(parseInt(selected));
    });
 
    if (ratings.length === 0) {
        $("#no-data-message").text("Please rate at least one player.").show();
        if (chart) chart.destroy();
        return;
    }
 
    $("#no-data-message").hide();
 
    // Distribution
    let distribution = new Array(10).fill(0);
    ratings.forEach(r => { distribution[r - 1]++; });
 
    // Average
    const sum = ratings.reduce((a, b) => a + b, 0);
    const average = (sum / ratings.length).toFixed(2);
    $("#average-rating").text(average);
 
    // MOTM
    let motmPlayer = "";
    $(".motm-btn").each(function () {
        if ($(this).hasClass("btn-warning")) {
            motmPlayer = $(this).closest(".card").find("h5, h6").first().text();
        }
    });
 
    $("#motm-display").text(motmPlayer
        ? "Your MOTM – " + motmPlayer
        : "No MOTM selected."
    );
 
    // Bar chart
    if (chart) chart.destroy();
 
    const isDark = document.body.classList.contains("dark-mode");
    const ctx = document.getElementById("ratingsChart").getContext("2d");
 
    chart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["1","2","3","4","5","6","7","8","9","10"],
            datasets: [{
                label: "Number of Players",
                data: distribution,
                backgroundColor: isDark ? "#22c55e" : "#dc3545"
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: isDark ? "white" : "black" } }
            },
            scales: {
                x: { ticks: { color: isDark ? "white" : "black" } },
                y: { ticks: { color: isDark ? "white" : "black" } }
            }
        }
    });
});