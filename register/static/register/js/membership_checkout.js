'use strict';

(function () {

    // Card number formatting + preview
    const cardNumber  = document.getElementById('memCardNumber');
    const previewNum  = document.getElementById('previewNumber');
    const brandLogo   = document.getElementById('cardBrandLogo');

    if (cardNumber) {
        cardNumber.addEventListener('input', function () {
            let digits = this.value.replace(/\D/g, '').slice(0, 16);
            this.value = digits.replace(/(.{4})/g, '$1 ').trim();
            if (previewNum) {
                const padded = digits.padEnd(16, '•');
                previewNum.textContent =
                    padded.slice(0,4)  + ' ' + padded.slice(4,8)  + ' ' +
                    padded.slice(8,12) + ' ' + padded.slice(12,16);
            }
            if (brandLogo) {
                let icon = 'bi-credit-card';
                if (/^4/.test(digits))           icon = 'bi-credit-card-2-front';
                else if (/^5[1-5]/.test(digits)) icon = 'bi-credit-card-fill';
                else if (/^3[47]/.test(digits))  icon = 'bi-credit-card-2-back';
                brandLogo.innerHTML = `<i class="bi ${icon} fs-3"></i>`;
            }
        });
    }

    // Cardholder name preview
    const cardName    = document.getElementById('memCardName');
    const previewName = document.getElementById('previewName');
    if (cardName && previewName) {
        cardName.addEventListener('input', function () {
            previewName.textContent = this.value.toUpperCase() || 'YOUR NAME';
        });
    }

    // Expiry formatting + preview
    const expiry        = document.getElementById('memExpiry');
    const previewExpiry = document.getElementById('previewExpiry');
    if (expiry) {
        expiry.addEventListener('input', function () {
            let val = this.value.replace(/\D/g, '').slice(0, 4);
            if (val.length >= 3) val = val.slice(0, 2) + '/' + val.slice(2);
            this.value = val;
            if (previewExpiry) previewExpiry.textContent = val || 'MM/YY';
        });
    }

    // CVV toggle
    const cvvInput  = document.getElementById('memCvv');
    const cvvToggle = document.getElementById('cvvToggle');
    const cvvIcon   = document.getElementById('cvvEyeIcon');
    if (cvvToggle && cvvInput) {
        cvvInput.type = 'password';
        cvvToggle.addEventListener('click', function () {
            const isPwd = cvvInput.type === 'password';
            cvvInput.type = isPwd ? 'text' : 'password';
            cvvIcon.className = isPwd ? 'bi bi-eye-slash' : 'bi bi-eye';
        });
    }

    // Submit spinner
    const form       = document.getElementById('membershipForm');
    const confirmBtn = document.getElementById('confirmBtn');
    if (form && confirmBtn) {
        form.addEventListener('submit', function () {
            confirmBtn.disabled = true;
            confirmBtn.innerHTML =
                '<span class="spinner-border spinner-border-sm me-2"></span>Processing…';
        });
    }

})();
