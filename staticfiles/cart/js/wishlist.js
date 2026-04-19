(function () {
    'use strict';
 
    function getCSRF() {
        const el = document.querySelector('[name=csrfmiddlewaretoken]');
        if (el) return el.value;
        const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }
 
    // ── Toggle wishlist from catalogue / product detail ──────────
    document.querySelectorAll('.wishlist-toggle-btn').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            const url       = this.dataset.toggleUrl;
            const icon      = this.querySelector('i');
            const self      = this;
 
            fetch(url, {
                method:  'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken':      getCSRF(),
                },
            })
            .then(r => r.json())
            .then(data => {
                if (data.in_wishlist) {
                    icon.className = 'bi bi-heart-fill';
                    self.classList.add('active');
                    self.title = 'Remove from wishlist';
                } else {
                    icon.className = 'bi bi-heart';
                    self.classList.remove('active');
                    self.title = 'Add to wishlist';
                }
            })
            .catch(() => {});
        });
    });
 
    // ── Remove from wishlist page ─────────────────────────────────
    document.querySelectorAll('.wishlist-remove-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const productId = this.dataset.productId;
            const url       = this.dataset.toggleUrl;
            const card      = document.getElementById('wishlist-item-' + productId);
            const self      = this;
 
            self.disabled = true;
 
            fetch(url, {
                method:  'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken':      getCSRF(),
                },
            })
            .then(r => r.json())
            .then(data => {
                if (!data.in_wishlist && card) {
                    card.style.transition = 'opacity 0.3s ease';
                    card.style.opacity    = '0';
                    setTimeout(() => {
                        card.remove();
                        // Show empty message if no items left
                        const remaining = document.querySelectorAll('[id^="wishlist-item-"]');
                        if (remaining.length === 0) {
                            location.reload();
                        }
                    }, 300);
                }
            })
            .catch(() => { self.disabled = false; });
        });
    });
 
})();