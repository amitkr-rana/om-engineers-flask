// Mobile-First JavaScript for Om Engineers App

document.addEventListener('DOMContentLoaded', function() {

    // ========================================
    // MOBILE NAVIGATION - RIGHT SLIDING SIDEBAR
    // ========================================
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    const navMenuOverlay = document.querySelector('.nav-menu-overlay');
    const navMenuClose = document.querySelector('.nav-menu-close');

    function openNavMenu() {
        navMenu.classList.add('active');
        navMenuOverlay.classList.add('active');
        navToggle.setAttribute('aria-expanded', 'true');
        document.body.style.overflow = 'hidden'; // Prevent background scroll

        // Animate toggle bars to X
        const bars = navToggle.querySelectorAll('.nav-toggle-bar');
        bars[0].style.transform = 'rotate(45deg) translateY(6px)';
        bars[1].style.opacity = '0';
        bars[2].style.transform = 'rotate(-45deg) translateY(-6px)';
    }

    function closeNavMenu() {
        navMenu.classList.remove('active');
        navMenuOverlay.classList.remove('active');
        navToggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = ''; // Restore background scroll

        // Reset toggle bars
        const bars = navToggle.querySelectorAll('.nav-toggle-bar');
        bars[0].style.transform = 'rotate(0) translateY(0)';
        bars[1].style.opacity = '1';
        bars[2].style.transform = 'rotate(0) translateY(0)';
    }

    if (navToggle && navMenu) {
        // Toggle menu on hamburger click
        navToggle.addEventListener('click', function() {
            const isActive = navMenu.classList.contains('active');
            if (isActive) {
                closeNavMenu();
            } else {
                openNavMenu();
            }
        });

        // Close menu on close button click
        if (navMenuClose) {
            navMenuClose.addEventListener('click', closeNavMenu);
        }

        // Close menu on overlay click
        if (navMenuOverlay) {
            navMenuOverlay.addEventListener('click', closeNavMenu);
        }

        // Close mobile menu when clicking on a nav link
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                closeNavMenu();
            });
        });

        // Close menu on scroll
        let scrollTimeout;
        window.addEventListener('scroll', function() {
            if (navMenu.classList.contains('active')) {
                clearTimeout(scrollTimeout);
                scrollTimeout = setTimeout(closeNavMenu, 100);
            }
        });

        // Close menu on escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape' && navMenu.classList.contains('active')) {
                closeNavMenu();
            }
        });
    }

    // ========================================
    // FLASH MESSAGES
    // ========================================
    const flashMessages = document.querySelectorAll('.flash-message');

    flashMessages.forEach(message => {
        const closeButton = message.querySelector('.flash-message-close');

        if (closeButton) {
            closeButton.addEventListener('click', function() {
                message.style.transform = 'translateX(100%)';
                message.style.opacity = '0';

                setTimeout(() => {
                    message.remove();
                }, 300);
            });
        }

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (message.parentNode) {
                message.style.transform = 'translateX(100%)';
                message.style.opacity = '0';

                setTimeout(() => {
                    message.remove();
                }, 300);
            }
        }, 5000);
    });

    // ========================================
    // FORM ENHANCEMENTS
    // ========================================

    // Add floating label effect
    const formInputs = document.querySelectorAll('.form-input');

    formInputs.forEach(input => {
        // Add focus/blur handlers for better UX
        input.addEventListener('focus', function() {
            this.parentNode.classList.add('form-group-focused');
        });

        input.addEventListener('blur', function() {
            this.parentNode.classList.remove('form-group-focused');

            // Add validation styling
            if (this.validity.valid) {
                this.classList.remove('form-input-error');
                this.classList.add('form-input-success');
            } else if (this.value) {
                this.classList.remove('form-input-success');
                this.classList.add('form-input-error');
            }
        });
    });

    // ========================================
    // FORM VALIDATION
    // ========================================
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const inputs = form.querySelectorAll('.form-input[required]');

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('form-input-error');

                    // Show error message
                    let errorMsg = input.parentNode.querySelector('.form-error');
                    if (!errorMsg) {
                        errorMsg = document.createElement('div');
                        errorMsg.className = 'form-error';
                        errorMsg.style.color = 'var(--error-color)';
                        errorMsg.style.fontSize = 'var(--font-size-sm)';
                        errorMsg.style.marginTop = 'var(--space-1)';
                        input.parentNode.appendChild(errorMsg);
                    }
                    errorMsg.textContent = 'This field is required';
                } else {
                    input.classList.remove('form-input-error');
                    const errorMsg = input.parentNode.querySelector('.form-error');
                    if (errorMsg) {
                        errorMsg.remove();
                    }
                }
            });

            // Validate email fields
            const emailInputs = form.querySelectorAll('input[type="email"]');
            emailInputs.forEach(input => {
                if (input.value && !input.validity.valid) {
                    isValid = false;
                    input.classList.add('form-input-error');

                    let errorMsg = input.parentNode.querySelector('.form-error');
                    if (!errorMsg) {
                        errorMsg = document.createElement('div');
                        errorMsg.className = 'form-error';
                        errorMsg.style.color = 'var(--error-color)';
                        errorMsg.style.fontSize = 'var(--font-size-sm)';
                        errorMsg.style.marginTop = 'var(--space-1)';
                        input.parentNode.appendChild(errorMsg);
                    }
                    errorMsg.textContent = 'Please enter a valid email address';
                }
            });

            // Validate phone fields
            const phoneInputs = form.querySelectorAll('input[type="tel"]');
            phoneInputs.forEach(input => {
                if (input.value && input.value.length < 10) {
                    isValid = false;
                    input.classList.add('form-input-error');

                    let errorMsg = input.parentNode.querySelector('.form-error');
                    if (!errorMsg) {
                        errorMsg = document.createElement('div');
                        errorMsg.className = 'form-error';
                        errorMsg.style.color = 'var(--error-color)';
                        errorMsg.style.fontSize = 'var(--font-size-sm)';
                        errorMsg.style.marginTop = 'var(--space-1)';
                        input.parentNode.appendChild(errorMsg);
                    }
                    errorMsg.textContent = 'Please enter a valid phone number';
                }
            });

            if (!isValid) {
                e.preventDefault();

                // Scroll to first error
                const firstError = form.querySelector('.form-input-error');
                if (firstError) {
                    firstError.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                    firstError.focus();
                }
            }
        });
    });

    // ========================================
    // SMOOTH SCROLLING FOR ANCHOR LINKS
    // ========================================
    const anchorLinks = document.querySelectorAll('a[href^="#"]');

    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // ========================================
    // PERFORMANCE: LAZY LOADING IMAGES
    // ========================================
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => imageObserver.observe(img));
    }

    // ========================================
    // TOUCH ENHANCEMENT FOR MOBILE
    // ========================================

    // Add touch feedback for buttons
    const touchElements = document.querySelectorAll('.btn, .card, .nav-link');

    touchElements.forEach(element => {
        element.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.98)';
            this.style.opacity = '0.8';
        });

        element.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
            this.style.opacity = '1';
        });

        element.addEventListener('touchcancel', function() {
            this.style.transform = 'scale(1)';
            this.style.opacity = '1';
        });
    });

    // ========================================
    // ACCESSIBILITY ENHANCEMENTS
    // ========================================

    // Add keyboard navigation for custom elements
    const customButtons = document.querySelectorAll('[role="button"]');

    customButtons.forEach(button => {
        button.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });

    // Announce page changes for screen readers
    const announcePageChange = (message) => {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = message;

        document.body.appendChild(announcement);

        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    };

    // Add to global scope for use in other parts of the app
    window.omEngineers = {
        announcePageChange: announcePageChange
    };

});

// ========================================
// UTILITY FUNCTIONS
// ========================================

// Format phone number for display
function formatPhoneNumber(phone) {
    const cleaned = phone.replace(/\D/g, '');
    const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
    if (match) {
        return `(${match[1]}) ${match[2]}-${match[3]}`;
    }
    return phone;
}

// Debounce function for performance
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction() {
        const context = this;
        const args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Check if element is in viewport
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}