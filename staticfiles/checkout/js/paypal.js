(function () {
    'use strict';

    if (typeof paypal === 'undefined') return;

    paypal.Buttons({
        style: { layout: 'vertical', color: 'blue', shape: 'rect', label: 'paypal', height: 45 },

        createOrder: async function () {
            const billing = {
                full_name:     document.getElementById('id_full_name')?.value.trim(),
                email:         document.getElementById('id_email')?.value.trim(),
                phone:         document.getElementById('id_phone')?.value.trim(),
                address_line1: document.getElementById('id_address_line1')?.value.trim(),
                address_line2: document.getElementById('id_address_line2')?.value.trim(),
                city:          document.getElementById('id_city')?.value.trim(),
                postcode:      document.getElementById('id_postcode')?.value.trim(),
                country:       document.getElementById('id_country')?.value.trim(),
            };
            if (!billing.full_name || !billing.email || !billing.address_line1 || !billing.city || !billing.postcode) {
                alert('Please fill in your billing address before continuing with PayPal.');
                return;
            }
            await fetch(SAVE_BILLING_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF_TOKEN },
                body: JSON.stringify(billing)
            });
            const resp = await fetch(PAYPAL_CREATE_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF_TOKEN }
            });
            const data = await resp.json();
            if (data.error) { alert('Error: ' + data.error); return; }
            return data.order_id;
        },

        onApprove: async function (data) {
            const resp = await fetch(PAYPAL_CAPTURE_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF_TOKEN },
                body: JSON.stringify({ order_id: data.orderID })
            });
            const result = await resp.json();
            if (result.redirect_url) window.location.href = result.redirect_url;
            else alert('Capture failed: ' + (result.error || 'Unknown error'));
        },

        onError: function (err) { console.error('PayPal error:', err); },
        onCancel: function () { if (typeof window.switchTab === 'function') window.switchTab('card'); }

    }).render('#paypal-button-container');
})();
