/**
 * Authentication utility functions for token-based authentication
 */

class AuthManager {
    constructor() {
        this.TOKEN_KEY = 'om_engineers_token';
        this.CUSTOMER_KEY = 'om_engineers_customer';
        this.AUTH_KEY = 'om_engineers_auth_key';
    }

    /**
     * Store authentication data after successful login
     */
    storeAuth(authData) {
        if (authData.auth && authData.auth.token) {
            localStorage.setItem(this.TOKEN_KEY, authData.auth.token);
        }

        if (authData.customer) {
            localStorage.setItem(this.CUSTOMER_KEY, JSON.stringify(authData.customer));
            if (authData.customer.auth_key) {
                localStorage.setItem(this.AUTH_KEY, authData.customer.auth_key);
            }
        }
    }

    /**
     * Get stored authentication token
     */
    getToken() {
        return localStorage.getItem(this.TOKEN_KEY);
    }

    /**
     * Get stored auth key
     */
    getAuthKey() {
        return localStorage.getItem(this.AUTH_KEY);
    }

    /**
     * Get stored customer data
     */
    getCustomer() {
        const customerData = localStorage.getItem(this.CUSTOMER_KEY);
        return customerData ? JSON.parse(customerData) : null;
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!this.getToken();
    }

    /**
     * Clear all authentication data
     */
    clearAuth() {
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.CUSTOMER_KEY);
        localStorage.removeItem(this.AUTH_KEY);
    }

    /**
     * Get authentication headers for API requests
     */
    getAuthHeaders() {
        const headers = {};
        const token = this.getToken();

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
            headers['X-Auth-Token'] = token;
        }

        const authKey = this.getAuthKey();
        if (authKey) {
            headers['X-Auth-Key'] = authKey;
        }

        return headers;
    }

    /**
     * Make authenticated API request
     */
    async apiRequest(url, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...this.getAuthHeaders(),
            ...(options.headers || {})
        };

        const response = await fetch(url, {
            ...options,
            headers
        });

        // Handle 401 responses by redirecting to login
        if (response.status === 401) {
            this.handleAuthError();
            throw new Error('Authentication required');
        }

        return response;
    }

    /**
     * Handle authentication errors
     */
    handleAuthError() {
        this.clearAuth();
        // Redirect to login page or show login modal
        if (window.location.pathname !== '/get-started') {
            window.location.href = '/get-started';
        }
    }

    /**
     * Logout user
     */
    async logout() {
        try {
            await this.apiRequest('/api/otp/logout', { method: 'POST' });
        } catch (error) {
            console.log('Logout API call failed:', error);
        } finally {
            this.clearAuth();
            window.location.href = '/';
        }
    }

    /**
     * Refresh authentication token
     */
    async refreshToken() {
        try {
            const response = await this.apiRequest('/api/otp/refresh-token', {
                method: 'POST'
            });

            if (response.ok) {
                const authData = await response.json();
                this.storeAuth(authData);
                return true;
            }
        } catch (error) {
            console.error('Token refresh failed:', error);
            this.handleAuthError();
        }
        return false;
    }

    /**
     * Get customer dashboard URL with auth parameters
     */
    getDashboardUrl() {
        const authKey = this.getAuthKey();
        const token = this.getToken();

        let url = '/dashboard';
        const params = new URLSearchParams();

        if (authKey) params.append('auth_key', authKey);
        if (token) params.append('token', token);

        if (params.toString()) {
            url += '?' + params.toString();
        }

        return url;
    }

    /**
     * Initialize authentication check on page load
     */
    init() {
        // Check if current page requires authentication
        const protectedPaths = ['/dashboard'];
        const currentPath = window.location.pathname;

        if (protectedPaths.some(path => currentPath.startsWith(path))) {
            if (!this.isAuthenticated()) {
                this.handleAuthError();
                return;
            }
        }

        // Auto-refresh token if it expires soon
        this.scheduleTokenRefresh();
    }

    /**
     * Schedule automatic token refresh
     */
    scheduleTokenRefresh() {
        // Refresh token every 23 hours (before 24-hour expiry)
        setInterval(() => {
            if (this.isAuthenticated()) {
                this.refreshToken();
            }
        }, 23 * 60 * 60 * 1000);
    }
}

// Global auth manager instance
window.authManager = new AuthManager();

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.authManager.init();
});

/**
 * Enhanced OTP form handling with token-based authentication
 */
function handleOTPForm() {
    const otpForm = document.getElementById('otp-form');
    if (!otpForm) return;

    otpForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(otpForm);
        const data = {
            phone_number: formData.get('phone_number'),
            otp_code: formData.get('otp_code')
        };

        try {
            const response = await fetch('/api/otp/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success && result.auth) {
                // Store authentication data
                window.authManager.storeAuth(result);

                // Redirect to dashboard
                window.location.href = window.authManager.getDashboardUrl();
            } else {
                showError(result.message || 'OTP verification failed');
            }
        } catch (error) {
            showError('Network error. Please try again.');
            console.error('OTP verification error:', error);
        }
    });
}

/**
 * Handle profile update form
 */
function handleProfileUpdateForm() {
    const profileForm = document.getElementById('profile-update-form');
    if (!profileForm) return;

    profileForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(profileForm);
        const authKey = window.authManager.getAuthKey();

        if (!authKey) {
            showError('Authentication required');
            return;
        }

        const data = {
            name: formData.get('name'),
            email: formData.get('email'),
            address: formData.get('address')
        };

        try {
            const response = await window.authManager.apiRequest(
                `/profile/${authKey}/update`,
                {
                    method: 'POST',
                    body: JSON.stringify(data)
                }
            );

            const result = await response.json();

            if (result.success) {
                // Update stored customer data
                if (result.customer) {
                    localStorage.setItem(window.authManager.CUSTOMER_KEY, JSON.stringify(result.customer));
                }
                showSuccess(result.message || 'Profile updated successfully');
            } else {
                showError(result.message || 'Profile update failed');
            }
        } catch (error) {
            showError('Network error. Please try again.');
            console.error('Profile update error:', error);
        }
    });
}

/**
 * Utility functions for showing messages
 */
function showError(message) {
    // Implementation depends on your UI framework
    alert('Error: ' + message);
}

function showSuccess(message) {
    // Implementation depends on your UI framework
    alert('Success: ' + message);
}

// Initialize form handlers on page load
document.addEventListener('DOMContentLoaded', () => {
    handleOTPForm();
    handleProfileUpdateForm();
});