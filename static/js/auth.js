// Authentication specific JavaScript functions

// Login form validation and submission
function validateLoginForm() {
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    let isValid = true;

    // Clear previous errors
    clearError('email');
    clearError('password');

    // Email validation
    if (!email) {
        showError('email', 'Email is required');
        isValid = false;
    } else if (!validateEmail(email)) {
        showError('email', 'Please enter a valid email address');
        isValid = false;
    }

    // Password validation
    if (!password) {
        showError('password', 'Password is required');
        isValid = false;
    } else if (password.length < 6) {
        showError('password', 'Password must be at least 6 characters long');
        isValid = false;
    }

    return isValid;
}

// Registration form validation and submission
function validateRegistrationForm() {
    const fullName = document.getElementById('full_name').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const skills = document.getElementById('skills').value.trim();
    let isValid = true;

    // Clear previous errors
    clearError('full_name');
    clearError('email');
    clearError('password');
    clearError('confirm_password');
    clearError('skills');

    // Full name validation
    if (!fullName) {
        showError('full_name', 'Full name is required');
        isValid = false;
    } else if (fullName.length < 2) {
        showError('full_name', 'Full name must be at least 2 characters long');
        isValid = false;
    }

    // Email validation
    if (!email) {
        showError('email', 'Email is required');
        isValid = false;
    } else if (!validateEmail(email)) {
        showError('email', 'Please enter a valid email address');
        isValid = false;
    }

    // Password validation
    if (!password) {
        showError('password', 'Password is required');
        isValid = false;
    } else if (password.length < 6) {
        showError('password', 'Password must be at least 6 characters long');
        isValid = false;
    }

    // Confirm password validation
    if (!confirmPassword) {
        showError('confirm_password', 'Please confirm your password');
        isValid = false;
    } else if (password !== confirmPassword) {
        showError('confirm_password', 'Passwords do not match');
        isValid = false;
    }

    // Skills validation
    if (!skills) {
        showError('skills', 'Please enter at least one skill');
        isValid = false;
    }

    return isValid;
}

// Handle login form submission
function handleLoginSubmit(event) {
    event.preventDefault();
    
    if (!validateLoginForm()) {
        return false;
    }

    const submitButton = document.getElementById('loginSubmitBtn');
    const originalText = submitButton.innerHTML;
    
    showLoading(submitButton);
    
    // Submit the form
    setTimeout(() => {
        document.getElementById('loginForm').submit();
    }, 500);
}

// Handle registration form submission
function handleRegistrationSubmit(event) {
    event.preventDefault();
    
    if (!validateRegistrationForm()) {
        return false;
    }

    const submitButton = document.getElementById('registerSubmitBtn');
    const originalText = submitButton.innerHTML;
    
    showLoading(submitButton);
    
    // Submit the form
    setTimeout(() => {
        document.getElementById('registrationForm').submit();
    }, 500);
}

// Toggle password visibility for confirm password field
function toggleConfirmPassword() {
    const passwordInput = document.getElementById('confirm_password');
    const toggleIcon = document.getElementById('confirmPasswordToggleIcon');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.classList.remove('fa-eye');
        toggleIcon.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        toggleIcon.classList.remove('fa-eye-slash');
        toggleIcon.classList.add('fa-eye');
    }
}

// Handle forgot password
function handleForgotPassword() {
    const email = document.getElementById('email').value.trim();
    
    if (!email) {
        showError('email', 'Please enter your email address first');
        return;
    }
    
    if (!validateEmail(email)) {
        showError('email', 'Please enter a valid email address');
        return;
    }
    
    // Show forgot password modal or handle the request
    showForgotPassword();
}

// Send forgot password email
function sendForgotPasswordEmail() {
    const email = document.getElementById('forgotPasswordEmail').value.trim();
    
    if (!email) {
        showError('forgotPasswordEmail', 'Email is required');
        return;
    }
    
    if (!validateEmail(email)) {
        showError('forgotPasswordEmail', 'Please enter a valid email address');
        return;
    }
    
    const submitButton = document.getElementById('forgotPasswordSubmitBtn');
    const originalText = submitButton.innerHTML;
    
    showLoading(submitButton);
    
    // Simulate sending email (replace with actual API call)
    setTimeout(() => {
        hideLoading(submitButton, originalText);
        showToast('Password reset email sent successfully!', 'success');
        closeForgotPassword();
    }, 2000);
}

// Real-time validation listeners
document.addEventListener('DOMContentLoaded', function() {
    // Login form event listeners
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLoginSubmit);
        
        // Real-time validation
        const emailField = document.getElementById('email');
        const passwordField = document.getElementById('password');
        
        if (emailField) {
            emailField.addEventListener('blur', function() {
                if (this.value.trim() && !validateEmail(this.value.trim())) {
                    showError('email', 'Please enter a valid email address');
                } else {
                    clearError('email');
                }
            });
        }
        
        if (passwordField) {
            passwordField.addEventListener('input', function() {
                if (this.value.length > 0 && this.value.length < 6) {
                    showError('password', 'Password must be at least 6 characters long');
                } else {
                    clearError('password');
                }
            });
        }
    }
    
    // Registration form event listeners
    const registrationForm = document.getElementById('registrationForm');
    if (registrationForm) {
        registrationForm.addEventListener('submit', handleRegistrationSubmit);
        
        // Real-time validation
        const fullNameField = document.getElementById('full_name');
        const emailField = document.getElementById('email');
        const passwordField = document.getElementById('password');
        const confirmPasswordField = document.getElementById('confirm_password');
        const skillsField = document.getElementById('skills');
        
        if (fullNameField) {
            fullNameField.addEventListener('blur', function() {
                if (this.value.trim() && this.value.trim().length < 2) {
                    showError('full_name', 'Full name must be at least 2 characters long');
                } else {
                    clearError('full_name');
                }
            });
        }
        
        if (emailField) {
            emailField.addEventListener('blur', function() {
                if (this.value.trim() && !validateEmail(this.value.trim())) {
                    showError('email', 'Please enter a valid email address');
                } else {
                    clearError('email');
                }
            });
        }
        
        if (passwordField) {
            passwordField.addEventListener('input', function() {
                if (this.value.length > 0 && this.value.length < 6) {
                    showError('password', 'Password must be at least 6 characters long');
                } else {
                    clearError('password');
                }
                
                // Check confirm password match if it has value
                const confirmPassword = document.getElementById('confirm_password');
                if (confirmPassword && confirmPassword.value) {
                    if (this.value !== confirmPassword.value) {
                        showError('confirm_password', 'Passwords do not match');
                    } else {
                        clearError('confirm_password');
                    }
                }
            });
        }
        
        if (confirmPasswordField) {
            confirmPasswordField.addEventListener('input', function() {
                const password = document.getElementById('password').value;
                if (this.value && this.value !== password) {
                    showError('confirm_password', 'Passwords do not match');
                } else {
                    clearError('confirm_password');
                }
            });
        }
        
        if (skillsField) {
            skillsField.addEventListener('blur', function() {
                if (!this.value.trim()) {
                    showError('skills', 'Please enter at least one skill');
                } else {
                    clearError('skills');
                }
            });
        }
    }
    
    // Forgot password modal event listeners
    const forgotPasswordForm = document.getElementById('forgotPasswordForm');
    if (forgotPasswordForm) {
        forgotPasswordForm.addEventListener('submit', function(e) {
            e.preventDefault();
            sendForgotPasswordEmail();
        });
    }
});

// Auto-focus first input field
document.addEventListener('DOMContentLoaded', function() {
    const firstInput = document.querySelector('input[type="text"], input[type="email"]');
    if (firstInput) {
        firstInput.focus();
    }
});
