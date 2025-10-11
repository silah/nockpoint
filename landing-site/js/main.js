// Nockpoint Landing Site JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Form submission handling
    const clubSignupForm = document.getElementById('clubSignupForm');
    if (clubSignupForm) {
        clubSignupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(this);
            const formObject = {};
            
            // Convert FormData to object
            for (let [key, value] of formData.entries()) {
                formObject[key] = value;
            }
            
            // Add checkbox value
            formObject.proPlan = document.getElementById('proPlan').checked;
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Processing...';
            submitBtn.disabled = true;
            
            // Simulate form submission (replace with actual API call)
            setTimeout(() => {
                console.log('Club signup data:', formObject);
                
                // Show success message
                showSuccessMessage();
                
                // Reset form
                clubSignupForm.reset();
                
                // Reset button
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
                
            }, 1500);
        });
    }

    // Form validation enhancements
    const requiredFields = document.querySelectorAll('input[required], select[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', function() {
            validateField(this);
        });
        
        field.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                validateField(this);
            }
        });
    });

    // Pro plan checkbox interaction
    const proCheckbox = document.getElementById('proPlan');
    if (proCheckbox) {
        proCheckbox.addEventListener('change', function() {
            const label = this.closest('.form-check').querySelector('.form-check-label');
            if (this.checked) {
                label.classList.add('text-primary');
                label.style.fontWeight = '600';
                
                // Add a little animation
                label.style.transform = 'scale(1.02)';
                setTimeout(() => {
                    label.style.transform = 'scale(1)';
                }, 200);
            } else {
                label.classList.remove('text-primary');
                label.style.fontWeight = '500';
            }
        });
    }

    // Feature card hover effects
    const featureCards = document.querySelectorAll('#features .card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const icon = this.querySelector('i.bi');
            if (icon) {
                icon.style.transform = 'scale(1.1) rotateY(10deg)';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            const icon = this.querySelector('i.bi');
            if (icon) {
                icon.style.transform = 'scale(1) rotateY(0deg)';
            }
        });
    });

    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-scrolled');
            navbar.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
            navbar.style.backgroundColor = 'rgba(13, 110, 253, 0.95)';
        } else {
            navbar.classList.remove('navbar-scrolled');
            navbar.style.boxShadow = 'none';
            navbar.style.backgroundColor = '';
        }
    });

    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe feature cards for animation
    const animatedElements = document.querySelectorAll('#features .card, #pricing .card');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});

// Field validation function
function validateField(field) {
    if (field.hasAttribute('required') && !field.value.trim()) {
        field.classList.add('is-invalid');
        showFieldError(field, 'This field is required');
        return false;
    } else if (field.type === 'email' && field.value && !isValidEmail(field.value)) {
        field.classList.add('is-invalid');
        showFieldError(field, 'Please enter a valid email address');
        return false;
    } else {
        field.classList.remove('is-invalid');
        hideFieldError(field);
        return true;
    }
}

// Email validation
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Show field error
function showFieldError(field, message) {
    let errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        field.parentNode.appendChild(errorDiv);
    }
    errorDiv.textContent = message;
}

// Hide field error
function hideFieldError(field) {
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Success message function
function showSuccessMessage() {
    const signupSection = document.getElementById('signup');
    const card = signupSection.querySelector('.card');
    
    // Create success message
    const successDiv = document.createElement('div');
    successDiv.className = 'alert alert-success text-center';
    successDiv.innerHTML = `
        <i class="bi bi-check-circle-fill fs-1 text-success mb-3"></i>
        <h4>Thank You!</h4>
        <p class="mb-0">We've received your club registration request. Our team will contact you within 24 hours to get your archery club set up with Nockpoint.</p>
    `;
    
    // Replace card content temporarily
    const originalContent = card.innerHTML;
    card.innerHTML = '';
    card.appendChild(successDiv);
    
    // Restore original content after 5 seconds
    setTimeout(() => {
        card.innerHTML = originalContent;
        
        // Re-attach event listeners
        const newForm = document.getElementById('clubSignupForm');
        if (newForm) {
            // Re-run the form setup
            location.reload();
        }
    }, 5000);
}

// Console message for developers
console.log('🏹 Nockpoint Landing Site loaded successfully!');
console.log('📧 Form submissions are currently logged to console for development purposes.');