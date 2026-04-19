(function () {
    'use strict';

    const CSRF = document.querySelector('[name=csrfmiddlewaretoken]')
               ? document.querySelector('[name=csrfmiddlewaretoken]').value : '';

    document.querySelectorAll('.poll-vote-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const voteUrl = this.dataset.voteUrl;
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';

            fetch(voteUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF },
            })
            .then(r => r.json())
            .then(data => {
                if (data.ok) {
                    updatePollUI(data);
                } else {
                    alert(data.error || 'Could not register vote.');
                    btn.disabled = false;
                    btn.innerHTML = 'Vote';
                }
            })
            .catch(() => {
                alert('Network error. Please try again.');
                btn.disabled = false;
                btn.innerHTML = 'Vote';
            });
        });
    });

    function updatePollUI(data) {
        data.options.forEach(function (opt) {
            const card = document.querySelector('[data-option-card="' + opt.id + '"]');
            if (!card) return;

            if (opt.id === data.voted_id) card.classList.add('voted');

            const bar = card.querySelector('.vote-bar');
            if (bar) bar.style.width = opt.percentage + '%';

            const count = card.querySelector('.vote-count');
            if (count) count.textContent = opt.votes + ' vote' + (opt.votes !== 1 ? 's' : '') + ' (' + opt.percentage + '%)';

            const voteBtn = card.querySelector('.poll-vote-btn');
            if (voteBtn) {
                if (opt.id === data.voted_id) voteBtn.outerHTML = '<span class="badge bg-danger px-3 py-2">Your Vote</span>';
                else voteBtn.remove();
            }
        });

        let maxVotes = 0;
        data.options.forEach(o => { if (o.votes > maxVotes) maxVotes = o.votes; });
        if (maxVotes > 0) {
            data.options.forEach(o => {
                if (o.votes === maxVotes) {
                    const card = document.querySelector('[data-option-card="' + o.id + '"]');
                    if (card) card.classList.add('winner');
                }
            });
        }

        const totalEl = document.getElementById('pollTotalVotes');
        if (totalEl) totalEl.textContent = data.total + ' vote' + (data.total !== 1 ? 's' : '') + ' cast';
    }
})();
