document.addEventListener('DOMContentLoaded', function() {
    const signupForm = document.getElementById('signup-form');
    const verifyForm = document.getElementById('verify-form');
    const loginForm = document.getElementById('login-form');
    
    const signupSection = document.getElementById('signup-section');
    const verifySection = document.getElementById('verify-section');
    const totpSection = document.getElementById('totp-section');
    
    const emailLink = document.getElementById('email-link');
    const verifyEmailInput = document.getElementById('verify-email');
    const totpSecretDisplay = document.getElementById('totp-secret');
    
    let currentEmail = '';
    let totpSecret = '';

    if (signupForm) {
        signupForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            if (response.ok) {
                currentEmail = email;
                verifyEmailInput.value = email;
                emailLink.href = data.email_viewer;
                emailLink.textContent = `View Email at ${data.email_viewer}`;
                
                signupSection.style.display = 'none';
                verifySection.style.display = 'block';
                document.getElementById('login-link').style.display = 'none';
            } else {
                alert(data.error || 'Sign up failed');
            }
        });
    }

    if (verifyForm) {
        verifyForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const code = document.getElementById('verification-code').value;
            
            const response = await fetch('/api/auth/verify-code', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: currentEmail, code: code })
            });
            
            const data = await response.json();
            if (response.ok) {
                totpSecret = data.totp_secret;
                totpSecretDisplay.textContent = totpSecret;
                
                verifySection.style.display = 'none';
                totpSection.style.display = 'block';
            } else {
                alert(data.error || 'Verification failed');
            }
        });
    }

    // Back to signup button (only if it exists)
    const backToSignupBtn = document.getElementById('back-to-signup');
    if (backToSignupBtn) {
        backToSignupBtn.addEventListener('click', function() {
            verifySection.style.display = 'none';
            signupSection.style.display = 'block';
            document.getElementById('login-link').style.display = 'block';
        });
    }

    // Proceed to login button (only if it exists)
    const proceedToLoginBtn = document.getElementById('proceed-to-login');
    if (proceedToLoginBtn) {
        proceedToLoginBtn.addEventListener('click', function() {
            // Store TOTP secret for login page
            sessionStorage.setItem('signup_email', currentEmail);
            sessionStorage.setItem('totp_secret', totpSecret);
            window.location.href = '/login';
        });
    }

    if (loginForm) {
        // Pre-fill email if coming from signup
        const signupEmail = sessionStorage.getItem('signup_email');
        const storedTotpSecret = sessionStorage.getItem('totp_secret');
        
        if (signupEmail) {
            document.getElementById('email').value = signupEmail;
            if (storedTotpSecret) {
                alert(`Your TOTP secret: ${storedTotpSecret}\nSet this up in your authenticator app!`);
            }
            // Clear session storage
            sessionStorage.removeItem('signup_email');
            sessionStorage.removeItem('totp_secret');
        }

        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const totp_token = document.getElementById('totp_token').value;
            
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, totp_token })
            });
            
            const data = await response.json();
            if (response.ok) {
                localStorage.setItem('token', data.access_token);
                alert('Login successful! Welcome to BBA Services.');
                window.location.href = '/';
            } else {
                alert(data.error || 'Login failed');
            }
        });
    }
});