'use strict';

(function () {
    const SUMMARY_URL = '/cart/summary/';
    const UPDATE_URL  = '/cart/update/';
    const REMOVE_URL  = '/cart/remove/';

    function getCsrf() {
        if (window._cartCsrf) return window._cartCsrf;
        const match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? match[1] : '';
    }

    function renderItems(data) {
        const list   = document.getElementById('cartItemsList');
        const footer = document.getElementById('cartFooter');
        const badge  = document.getElementById('cartBadge');
        const total  = document.getElementById('cartTotal');

        if (!list || !footer) return;

        if (badge) {
            if (data.total_items > 0) {
                badge.textContent = data.total_items;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        }

        if (data.items.length === 0) {
            list.innerHTML = `<div class="text-center py-5 text-muted">
                <i class="bi bi-cart-x fs-1 mb-2 d-block"></i><span>Your cart is empty</span></div>`;
            footer.style.setProperty('display', 'none', 'important');
            return;
        }

        footer.style.removeProperty('display');
        if (total) total.textContent = '£' + parseFloat(data.total_price).toFixed(2);

        list.innerHTML = data.items.map(item => `
            <div class="cart-panel-item d-flex gap-2 align-items-center mb-3" id="panel-item-${item.id}">
                ${item.image
                    ? `<img src="${item.image}" alt="${item.name}" class="cart-panel-img rounded">`
                    : `<div class="cart-panel-img rounded bg-light d-flex align-items-center justify-content-center"><i class="bi bi-image text-muted"></i></div>`
                }
                <div class="flex-grow-1 min-w-0">
                    <div class="fw-semibold small text-truncate">${item.name}</div>
                    <div class="text-muted" style="font-size:0.75rem;">Size: ${item.size}</div>
                    <div class="text-danger fw-bold small">£${parseFloat(item.line_total).toFixed(2)}</div>
                </div>
                <div class="d-flex align-items-center gap-1">
                    <button class="btn btn-outline-secondary btn-xs cart-decrease" data-id="${item.id}"
                            style="width:26px;height:26px;padding:0;font-size:0.75rem;">−</button>
                    <span class="fw-bold small" style="min-width:20px;text-align:center;"
                          id="panel-qty-${item.id}">${item.quantity}</span>
                    <button class="btn btn-outline-secondary btn-xs cart-increase" data-id="${item.id}"
                            style="width:26px;height:26px;padding:0;font-size:0.75rem;">+</button>
                </div>
                <button class="btn btn-outline-danger btn-xs cart-remove" data-id="${item.id}"
                        style="width:26px;height:26px;padding:0;font-size:0.75rem;">
                    <i class="bi bi-trash3" style="font-size:0.7rem;"></i>
                </button>
            </div>
        `).join('');

        list.querySelectorAll('.cart-increase').forEach(btn => {
            btn.addEventListener('click', () => doUpdate(btn.dataset.id, 'increase'));
        });
        list.querySelectorAll('.cart-decrease').forEach(btn => {
            btn.addEventListener('click', () => doUpdate(btn.dataset.id, 'decrease'));
        });
        list.querySelectorAll('.cart-remove').forEach(btn => {
            btn.addEventListener('click', () => doRemove(btn.dataset.id));
        });
    }

    function loadCart() {
        fetch(SUMMARY_URL, {
            credentials: 'same-origin',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(r => {
            if (!r.ok) { console.error('Cart summary failed:', r.status, r.url); return; }
            return r.json();
        })
        .then(data => { if (data) renderItems(data); })
        .catch(err => console.error('loadCart error:', err));
    }

    function doUpdate(itemId, action) {
        fetch(`${UPDATE_URL}${itemId}/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCsrf(),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `action=${action}`
        })
        .then(r => r.json())
        .then(data => { if (data.success) loadCart(); })
        .catch(console.error);
    }

    function doRemove(itemId) {
        fetch(`${REMOVE_URL}${itemId}/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCsrf(),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: ''
        })
        .then(r => r.json())
        .then(data => { if (data.success) loadCart(); })
        .catch(console.error);
    }

    document.addEventListener('DOMContentLoaded', loadCart);

    const offcanvasEl = document.getElementById('cartOffcanvas');
    if (offcanvasEl) offcanvasEl.addEventListener('show.bs.offcanvas', loadCart);

    window.reloadCart = loadCart;
})();
