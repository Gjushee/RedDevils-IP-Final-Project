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
            btn.innerHTML = '<i class="bi bi-cart-check me-2"></i>Added!';
            msg.style.display = 'block';
            msg.innerHTML = `<div class="alert alert-success py-2">${data.message}</div>`;
            if (window.reloadCart) window.reloadCart();
            setTimeout(() => {
                btn.innerHTML = '<i class="bi bi-cart-plus me-2"></i>Add to Cart';
                msg.style.display = 'none';
            }, 2500);
        })
        .catch(() => {
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-cart-plus me-2"></i>Add to Cart';
        });
    });
});
