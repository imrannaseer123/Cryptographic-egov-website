/**
 * E-Governance Portal - Main JavaScript
 * Provides enhanced functionality and user experience improvements
 */

// Global configuration
const EGOV = {
    config: {
        sessionTimeout: 30 * 60 * 1000, // 30 minutes in milliseconds
        warningThreshold: 5 * 60 * 1000, // 5 minutes warning
        apiBaseUrl: window.location.origin,
        animationDuration: 300
    },
    session: {
        startTime: null,
        warningShown: false,
        timer: null
    }
};

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('E-Governance Portal initialized');
    initializeSessionManagement();
    initializeFormEnhancements();
    initializeAccessibility();
    initializeAnimations();
});

/**
 * Session Management
 */
function initializeSessionManagement() {
    // Get session start time from meta tag or current time
    const sessionMeta = document.querySelector('meta[name="session-start"]');
    EGOV.session.startTime = sessionMeta ? new Date(sessionMeta.content) : new Date();

    // Start session timeout monitoring
    startSessionMonitoring();
}

function startSessionMonitoring() {
    // Check session every minute
    EGOV.session.timer = setInterval(checkSessionTimeout, 60000);

    // Initial check
    setTimeout(checkSessionTimeout, 1000);
}

function checkSessionTimeout() {
    const now = new Date();
    const elapsed = now - EGOV.session.startTime;
    const remaining = EGOV.config.sessionTimeout - elapsed;

    if (remaining <= 0) {
        // Session expired
        handleSessionExpired();
    } else if (remaining <= EGOV.config.warningThreshold && !EGOV.session.warningShown) {
        // Show warning
        showSessionWarning(remaining);
    }
}

function showSessionWarning(remaining) {
    EGOV.session.warningShown = true;
    const minutes = Math.floor(remaining / 60000);
    const seconds = Math.floor((remaining % 60000) / 1000);

    // Create warning modal
    const modal = createModal(
        'Session Warning',
        `<p>Your session will expire in <strong>${minutes}:${seconds.toString().padStart(2, '0')}</strong></p>
         <p>Would you like to extend your session?</p>`,
        [
            { text: 'Extend Session', class: 'btn-primary', action: extendSession },
            { text: 'Logout', class: 'btn-secondary', action: logout }
        ]
    );

    document.body.appendChild(modal);
}

function extendSession() {
    // Reset session timer
    EGOV.session.startTime = new Date();
    EGOV.session.warningShown = false;

    // Show confirmation
    showNotification('Session extended successfully', 'success');

    // Close modal
    const modal = document.querySelector('.modal');
    if (modal) modal.remove();
}

function handleSessionExpired() {
    clearInterval(EGOV.session.timer);

    showNotification('Your session has expired. Please login again.', 'warning');

    // Redirect to login after 3 seconds
    setTimeout(() => {
        window.location.href = '/login/';
    }, 3000);
}

function logout() {
    // Perform logout action
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/logout/';

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfToken) {
        form.appendChild(csrfToken.cloneNode(true));
    }

    document.body.appendChild(form);
    form.submit();
}

/**
 * Form Enhancements
 */
function initializeFormEnhancements() {
    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        enhanceForm(form);
    });

    // Add password visibility toggles
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        addPasswordToggle(input);
    });

    // Add auto-focus to first input
    const firstInput = document.querySelector('input:not([type="hidden"]):not([disabled])');
    if (firstInput) {
        firstInput.focus();
    }
}

function enhanceForm(form) {
    form.addEventListener('submit', function(e) {
        const submitBtn = form.querySelector('[type="submit"]');
        if (submitBtn && !submitBtn.disabled) {
            // Disable button and show loading
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processing...';
            submitBtn.disabled = true;

            // Re-enable after 10 seconds (fallback)
            setTimeout(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 10000);
        }
    });

    // Add client-side validation
    const requiredInputs = form.querySelectorAll('[required]');
    requiredInputs.forEach(input => {
        input.addEventListener('blur', () => validateInput(input));
        input.addEventListener('input', () => clearValidationError(input));
    });
}

function addPasswordToggle(input) {
    const container = input.parentElement;
    if (container.style.position !== 'relative') {
        container.style.position = 'relative';
    }

    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'btn btn-outline-secondary btn-sm';
    toggle.style.cssText = 'position: absolute; right: 10px; top: 50%; transform: translateY(-50%); z-index: 10;';
    toggle.innerHTML = '<i class="fas fa-eye"></i>';
    toggle.setAttribute('aria-label', 'Toggle password visibility');

    toggle.addEventListener('click', () => {
        if (input.type === 'password') {
            input.type = 'text';
            toggle.innerHTML = '<i class="fas fa-eye-slash"></i>';
        } else {
            input.type = 'password';
            toggle.innerHTML = '<i class="fas fa-eye"></i>';
        }
    });

    container.appendChild(toggle);
}

function validateInput(input) {
    if (!input.value.trim()) {
        showValidationError(input, `${input.name.charAt(0).toUpperCase() + input.name.slice(1)} is required.`);
        return false;
    }
    return true;
}

function showValidationError(input, message) {
    input.classList.add('is-invalid');

    let feedback = input.parentElement.querySelector('.invalid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        input.parentElement.appendChild(feedback);
    }

    feedback.textContent = message;
}

function clearValidationError(input) {
    input.classList.remove('is-invalid');
    const feedback = input.parentElement.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.remove();
    }
}

/**
 * Accessibility Enhancements
 */
function initializeAccessibility() {
    // Add keyboard navigation for cards
    const cards = document.querySelectorAll('.card, .info-card');
    cards.forEach(card => {
        if (card.querySelector('a, button')) {
            card.setAttribute('tabindex', '0');
            card.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    const link = card.querySelector('a, button');
                    if (link) link.click();
                }
            });
        }
    });

    // Add ARIA live regions for notifications
    addLiveRegion();

    // Add skip links
    addSkipLinks();
}

function addLiveRegion() {
    const liveRegion = document.createElement('div');
    liveRegion.setAttribute('aria-live', 'polite');
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.className = 'sr-only';
    liveRegion.id = 'live-region';
    document.body.appendChild(liveRegion);
}

function addSkipLinks() {
    const skipLinks = document.createElement('div');
    skipLinks.className = 'skip-links';
    skipLinks.innerHTML = `
        <a href="#main-content" class="skip-link">Skip to main content</a>
        <a href="#navigation" class="skip-link">Skip to navigation</a>
    `;
    document.body.insertBefore(skipLinks, document.body.firstChild);
}

/**
 * Animations and Visual Effects
 */
function initializeAnimations() {
    // Add scroll animations
    observeElements();

    // Add hover effects to cards
    const cards = document.querySelectorAll('.info-card, .card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-5px)';
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });
    });

    // Add fade-in animation to alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach((alert, index) => {
        setTimeout(() => {
            alert.classList.add('fade-in');
        }, index * 100);
    });
}

function observeElements() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });

    const elements = document.querySelectorAll('.info-card, .card');
    elements.forEach(el => observer.observe(el));
}

/**
 * Utility Functions
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 1050; max-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 500);
    }, 5000);

    // Announce to screen readers
    const liveRegion = document.getElementById('live-region');
    if (liveRegion) {
        liveRegion.textContent = message;
    }
}

function createModal(title, content, buttons = []) {
    const modal = document.createElement('div');
    modal.className = 'modal fade show';
    modal.style.display = 'block';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');

    const buttonsHtml = buttons.map(btn =>
        `<button type="button" class="btn ${btn.class}" onclick="${btn.action.name}()">${btn.text}</button>`
    ).join('');

    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">${title}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
                <div class="modal-footer">
                    ${buttonsHtml}
                </div>
            </div>
        </div>
    `;

    // Add backdrop
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop fade show';
    modal.appendChild(backdrop);

    // Close on backdrop click
    backdrop.addEventListener('click', () => modal.remove());

    return modal;
}

function formatTime(milliseconds) {
    const minutes = Math.floor(milliseconds / 60000);
    const seconds = Math.floor((milliseconds % 60000) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// Export functions for global use
window.EGOV = EGOV;
window.showNotification = showNotification;
window.extendSession = extendSession;
window.logout = logout;

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Page is hidden, pause timers
        console.log('Page hidden - pausing session monitoring');
    } else {
        // Page is visible, resume timers
        console.log('Page visible - resuming session monitoring');
        EGOV.session.startTime = new Date(); // Reset to avoid false expiration
    }
});

// Handle online/offline status
window.addEventListener('online', function() {
    showNotification('Connection restored', 'success');
});

window.addEventListener('offline', function() {
    showNotification('Connection lost. Some features may be unavailable.', 'warning');
});

console.log('E-Governance Portal JavaScript loaded successfully');