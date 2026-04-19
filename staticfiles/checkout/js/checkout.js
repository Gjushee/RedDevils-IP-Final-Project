(function () {
    'use strict';

    const cardNumberInput = document.getElementById('id_card_number');
    const previewNumber   = document.getElementById('previewNumber');
    const cardBrandLogo   = document.getElementById('cardBrandLogo');

    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function () {
            let digits = this.value.replace(/\D/g, '').slice(0, 16);
            this.value = digits.replace(/(.{4})/g, '$1 ').trim();
            if (previewNumber) {
                const padded = digits.padEnd(16, '•');
                previewNumber.textContent =
                    padded.slice(0,4) + ' ' + padded.slice(4,8) + ' ' +
                    padded.slice(8,12) + ' ' + padded.slice(12,16);
            }
            if (cardBrandLogo) {
                let icon = 'bi-credit-card';
                if (/^4/.test(digits))           icon = 'bi-credit-card-2-front';
                else if (/^5[1-5]/.test(digits)) icon = 'bi-credit-card-fill';
                else if (/^3[47]/.test(digits))  icon = 'bi-credit-card-2-back';
                cardBrandLogo.innerHTML = `<i class="bi ${icon} fs-3"></i>`;
            }
        });
    }

    const cardNameInput = document.getElementById('id_card_name');
    const previewName   = document.getElementById('previewName');
    if (cardNameInput && previewName) {
        cardNameInput.addEventListener('input', function () {
            previewName.textContent = this.value.toUpperCase() || 'YOUR NAME';
        });
    }

    const expiryInput   = document.getElementById('id_expiry');
    const previewExpiry = document.getElementById('previewExpiry');
    if (expiryInput) {
        expiryInput.addEventListener('input', function () {
            let val = this.value.replace(/\D/g, '').slice(0, 4);
            if (val.length >= 3) val = val.slice(0, 2) + '/' + val.slice(2);
            this.value = val;
            if (previewExpiry) previewExpiry.textContent = val || 'MM/YY';
        });
    }

    const cvvInput   = document.getElementById('id_cvv');
    const cvvToggle  = document.getElementById('cvvToggle');
    const cvvEyeIcon = document.getElementById('cvvEyeIcon');
    if (cvvToggle && cvvInput) {
        cvvToggle.addEventListener('click', function () {
            const isPassword = cvvInput.type === 'password';
            cvvInput.type = isPassword ? 'text' : 'password';
            cvvEyeIcon.className = isPassword ? 'bi bi-eye-slash' : 'bi bi-eye';
        });
    }

    window.switchTab = function (tab) {
        const cardPanel   = document.getElementById('cardPanel');
        const paypalPanel = document.getElementById('paypalPanel');
        const tabCard     = document.getElementById('tabCard');
        const tabPaypal   = document.getElementById('tabPaypal');
        if (tab === 'card') {
            if (cardPanel)   cardPanel.style.display   = '';
            if (paypalPanel) paypalPanel.style.display = 'none';
            if (tabCard)     tabCard.classList.add('active');
            if (tabPaypal)   tabPaypal.classList.remove('active');
        } else {
            if (cardPanel)   cardPanel.style.display   = 'none';
            if (paypalPanel) paypalPanel.style.display = '';
            if (tabCard)     tabCard.classList.remove('active');
            if (tabPaypal)   tabPaypal.classList.add('active');
        }
    };

    const checkoutForm = document.getElementById('checkoutForm');
    const payCardBtn   = document.getElementById('payCardBtn');
    if (checkoutForm && payCardBtn) {
        checkoutForm.addEventListener('submit', function () {
            payCardBtn.disabled = true;
            payCardBtn.innerHTML =
                '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processing…';
        });
    }
})();
