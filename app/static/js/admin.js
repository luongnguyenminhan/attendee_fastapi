/**
 * Attendee Admin Interface JavaScript
 * Contains utilities and functions for admin interface
 */

// Auto-dismiss alerts after 3 seconds (from Django base template)
document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss Django-style messages
    setTimeout(function () {
        var alerts = document.querySelectorAll('.django-message');
        alerts.forEach(function (alert) {
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                var bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        });
    }, 3000);

    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Initialize popovers if Bootstrap is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Popover) {
        var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
});

// Utility functions for admin interface
window.AdminUtils = {
    // Show loading spinner
    showLoading: function () {
        document.querySelector('.loading-spinner').style.display = 'block';
    },

    // Hide loading spinner  
    hideLoading: function () {
        document.querySelector('.loading-spinner').style.display = 'none';
    },

    // Show toast notification
    showToast: function (message, type = 'info') {
        const toastContainer = document.querySelector('.toast-container') || this.createToastContainer();
        const toast = this.createToast(message, type);
        toastContainer.appendChild(toast);

        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();

            // Remove toast after it's hidden
            toast.addEventListener('hidden.bs.toast', function () {
                toast.remove();
            });
        }
    },

    // Create toast container if it doesn't exist
    createToastContainer: function () {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    },

    // Create toast element
    createToast: function (message, type) {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        return toast;
    },

    // Confirm dialog with custom styling
    confirm: function (message, title = 'Xác nhận') {
        return confirm(`${title}: ${message}`);
    },

    // Format numbers with commas
    formatNumber: function (num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    },

    // Format date to Vietnamese format
    formatDate: function (date) {
        if (typeof date === 'string') {
            date = new Date(date);
        }
        return date.toLocaleDateString('vi-VN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // AJAX wrapper with loading and error handling
    ajax: function (url, options = {}) {
        this.showLoading();

        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const finalOptions = { ...defaultOptions, ...options };

        return fetch(url, finalOptions)
            .then(response => {
                this.hideLoading();

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                return response.json();
            })
            .catch(error => {
                this.hideLoading();
                this.showToast('Có lỗi xảy ra: ' + error.message, 'danger');
                throw error;
            });
    },

    // Copy text to clipboard
    copyToClipboard: function (text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                this.showToast('Đã sao chép vào clipboard', 'success');
            });
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            this.showToast('Đã sao chép vào clipboard', 'success');
        }
    }
};

// Global event handlers
document.addEventListener('click', function (e) {
    // Handle copy buttons
    if (e.target.hasAttribute('data-copy')) {
        e.preventDefault();
        const textToCopy = e.target.getAttribute('data-copy');
        AdminUtils.copyToClipboard(textToCopy);
    }

    // Handle delete buttons with confirmation
    if (e.target.hasAttribute('data-delete-confirm')) {
        const message = e.target.getAttribute('data-delete-confirm') || 'Bạn có chắc chắn muốn xóa?';
        if (!AdminUtils.confirm(message)) {
            e.preventDefault();
            return false;
        }
    }
});

// Handle forms with loading states
document.addEventListener('submit', function (e) {
    if (e.target.hasAttribute('data-loading')) {
        AdminUtils.showLoading();
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function (e) {
    // Ctrl/Cmd + / to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"], input[name="search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
});

// Initialize HTMX if available
document.addEventListener('DOMContentLoaded', function () {
    if (typeof htmx !== 'undefined') {
        // HTMX event handlers
        document.body.addEventListener('htmx:beforeRequest', function (evt) {
            AdminUtils.showLoading();
        });

        document.body.addEventListener('htmx:afterRequest', function (evt) {
            AdminUtils.hideLoading();

            if (evt.detail.xhr.status >= 400) {
                AdminUtils.showToast('Có lỗi xảy ra khi tải dữ liệu', 'danger');
            }
        });
    }
});

console.log('Attendee Admin Interface JavaScript loaded successfully'); 