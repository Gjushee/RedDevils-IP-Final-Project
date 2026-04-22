/* TRANSFERS PAGE JS */

document.addEventListener('DOMContentLoaded', function () {

    // --- Set likelihood bar widths from data-pct attribute ---
    document.querySelectorAll('.likelihood-bar[data-pct]').forEach(function (bar) {
        bar.style.width = bar.dataset.pct + '%';
    });

    // --- Likelihood slider live label ---
    const slider = document.getElementById('likelihoodSlider');
    const valueLabel = document.getElementById('likelihoodValue');

    if (slider && valueLabel) {
        // Set initial display
        valueLabel.textContent = slider.value;

        slider.addEventListener('input', function () {
            valueLabel.textContent = this.value;

            // Update label colour based on score
            const score = parseInt(this.value, 10);
            if (score <= 3) {
                valueLabel.style.color = '#ffc107';
            } else if (score <= 5) {
                valueLabel.style.color = '#fd7e14';
            } else if (score <= 7) {
                valueLabel.style.color = '#dc3545';
            } else {
                valueLabel.style.color = '#198754';
            }
        });
    }

    // --- Auto-dismiss alerts after 4 seconds 
    document.querySelectorAll('.alert').forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 4000);
    });

});
