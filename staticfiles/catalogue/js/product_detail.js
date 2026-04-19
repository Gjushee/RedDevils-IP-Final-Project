'use strict';

// ── CSRF helper ──────────────────────────────────────────────────
function getCSRF() {
    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    if (input) return input.value;
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
}

// ── Star Rating ──────────────────────────────────────────────────
(function () {
    const widget   = document.getElementById('starWidget');
    const feedback = document.getElementById('ratingFeedback');
    if (!widget || !feedback) return;  // not authenticated or widget missing

    const stars         = widget.querySelectorAll('.star-btn');
    const RATE_URL      = widget.dataset.rateUrl;
    const userRatingInit = parseInt(widget.dataset.userRating || '0', 10);

    if (!RATE_URL) return;

    function paint(upTo) {
        stars.forEach(s => {
            s.style.color = parseInt(s.dataset.value) <= upTo ? '#ffc107' : '#dee2e6';
        });
    }

    // Paint the user's existing rating on load
    paint(userRatingInit);

    stars.forEach(star => {
        star.addEventListener('mouseenter', () => paint(parseInt(star.dataset.value)));
        star.addEventListener('mouseleave', () => paint(userRatingInit));
        star.addEventListener('click', () => {
            const val = parseInt(star.dataset.value);
            fetch(RATE_URL, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCSRF(),
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `rating=${val}`
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    paint(data.user_rating);
                    document.getElementById('ratingInfo').innerHTML =
                        `Average: <strong id="avgVal">${data.avg_rating}</strong>/5`
                        + ` &nbsp;·&nbsp; <span id="cntVal">${data.count}</span>`
                        + ` rating${data.count !== 1 ? 's' : ''}`;
                    feedback.textContent = `You rated ${data.user_rating}/5 — thanks!`;
                    feedback.style.display = 'inline';
                    setTimeout(() => { feedback.style.display = 'none'; }, 3000);
                }
            })
            .catch(console.error);
        });
    });
})();

// ── Add to Cart ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('addToCartForm');
    if (!form) return;

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const btn  = document.getElementById('addToCartBtn');
        const msg  = document.getElementById('addToCartMsg');
        const csrf = form.querySelector('[name=csrfmiddlewaretoken]').value;

        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Adding...';

        fetch(form.action, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrf,
            },
            body: new FormData(form)
        })
        .then(r => r.json())
        .then(data => {
            btn.disabled = false;
            if (data.success) {
                btn.innerHTML = '<i class="bi bi-cart-check me-2"></i>Added!';
                msg.style.display = 'block';
                msg.innerHTML = `<div class="alert alert-success py-2">${data.message}</div>`;
                if (window.reloadCart) window.reloadCart();
                const cartEl = document.getElementById('cartOffcanvas');
                if (cartEl && typeof bootstrap !== 'undefined') {
                    bootstrap.Offcanvas.getOrCreateInstance(cartEl).show();
                }
                setTimeout(() => {
                    btn.innerHTML = '<i class="bi bi-cart-plus me-2"></i>Add to Cart';
                    msg.style.display = 'none';
                }, 2500);
            } else {
                btn.innerHTML = '<i class="bi bi-cart-plus me-2"></i>Add to Cart';
                msg.style.display = 'block';
                msg.innerHTML = `<div class="alert alert-warning py-2">${data.error || 'Could not add item to cart.'}</div>`;
                setTimeout(() => { msg.style.display = 'none'; }, 3000);
            }
        })
        .catch(() => {
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-cart-plus me-2"></i>Add to Cart';
        });
    });
});
