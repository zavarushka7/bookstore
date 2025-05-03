document.addEventListener('DOMContentLoaded', function() {
    const emailInput = document.querySelector('input[name="email"]');
    const passwordInput = document.querySelector('input[name="password1"]');
    const emailError = document.getElementById('email-error');
    const passwordError = document.getElementById('password-error');
    const form = document.getElementById('register-form');

    // Проверка формата email
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    // Проверка email через AJAX
    function checkEmailUniqueness(email) {
        fetch(`/check-email/?email=${encodeURIComponent(email)}`)
            .then(response => response.json())
            .then(data => {
                if (data.is_taken) {
                    emailError.textContent = data.error_message;
                } else {
                    emailError.textContent = '';
                }
            })
            .catch(() => {
                emailError.textContent = 'Ошибка проверки email.';
            });
    }

    // Валидация email
    emailInput.addEventListener('input', function() {
        const email = this.value.trim();
        if (!email) {
            emailError.textContent = 'Email обязателен.';
        } else if (!validateEmail(email)) {
            emailError.textContent = 'Введите корректный email.';
        } else {
            emailError.textContent = '';
            checkEmailUniqueness(email);
        }
    });

    // Валидация пароля
    passwordInput.addEventListener('input', function() {
        const password = this.value;
        if (password.length < 6) {
            passwordError.textContent = 'Пароль должен содержать не менее 6 символов.';
        } else {
            passwordError.textContent = '';
        }
    });

    // Блокировка отправки формы при ошибках
    form.addEventListener('submit', function(event) {
        const email = emailInput.value.trim();
        const password = passwordInput.value;

        if (!validateEmail(email) || password.length < 6 || emailError.textContent) {
            event.preventDefault();
            if (!validateEmail(email)) {
                emailError.textContent = 'Введите корректный email.';
            }
            if (password.length < 6) {
                passwordError.textContent = 'Пароль должен содержать не менее 6 символов.';
            }
        }
    });
});