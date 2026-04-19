(function () {
    const MAX_WORDS = 200;
    const form      = document.getElementById('contactForm');
    if (!form) return;

    const msgField  = document.getElementById('message');
    const counter   = document.getElementById('wordCount');
    const URL       = form.dataset.url;
    const CSRF      = form.querySelector('[name=csrfmiddlewaretoken]').value;

    // Live word counter
    msgField.addEventListener('input', function () {
        const words = this.value.trim().split(/\s+/).filter(w => w.length > 0);
        counter.textContent = words.length;
        counter.style.color = words.length > MAX_WORDS ? 'red' : '';
    });

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const name    = document.getElementById('fullName');
        const email   = document.getElementById('email');
        const subject = document.getElementById('subject');

        [name, email, subject, msgField].forEach(el => el.classList.remove('is-invalid'));

        let valid = true;

        if (name.value.trim().length < 3)
            { name.classList.add('is-invalid'); valid = false; }
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim()))
            { email.classList.add('is-invalid'); valid = false; }
        if (subject.value.trim().length < 3)
            { subject.classList.add('is-invalid'); valid = false; }

        const msgText = msgField.value.trim();
        const words   = msgText.split(/\s+/).filter(w => w.length > 0);
        if (msgText.length < 10 || words.length > MAX_WORDS)
            { msgField.classList.add('is-invalid'); valid = false; }

        if (!valid) return;

        fetch(URL, {
            method:  'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': CSRF },
            body:    new FormData(form),
        })
        .then(r => r.json())
        .then(res => {
            if (res.success) {
                document.getElementById('cName').textContent    = name.value.trim();
                document.getElementById('cEmail').textContent   = email.value.trim();
                document.getElementById('cSubject').textContent = subject.value.trim();
                document.getElementById('cMessage').textContent = msgText;

                new bootstrap.Modal(document.getElementById('confirmModal')).show();
                form.reset();
                counter.textContent = '0';
            } else {
                if (res.errors.name)    name.classList.add('is-invalid');
                if (res.errors.email)   email.classList.add('is-invalid');
                if (res.errors.subject) subject.classList.add('is-invalid');
                if (res.errors.message) msgField.classList.add('is-invalid');
            }
        })
        .catch(() => {});
    });
})();
