// Global configuration
const API_BASE_URL = window.location.origin + '/api';

// Utility functions
function showAlert(type, message) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <div>${message}</div>
        <button class="close-alert">&times;</button>
    `;
    
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    document.body.insertBefore(alert, document.body.firstChild);
    
    setTimeout(() => {
        if (alert.parentNode) alert.remove();
    }, 5000);
    
    alert.querySelector('.close-alert').addEventListener('click', () => alert.remove());
}

function setLoading(element, isLoading, loadingText = 'Loading...') {
    if (isLoading) {
        element.dataset.originalText = element.innerHTML;
        element.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${loadingText}`;
        element.disabled = true;
    } else {
        element.innerHTML = element.dataset.originalText || '';
        element.disabled = false;
    }
}

// Common API functions
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({ error: 'Request failed' }));
            throw new Error(error.error || `HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

// Export for use in admin.html
if (typeof module === 'object' && module.exports) {
    module.exports = { showAlert, setLoading, apiRequest, API_BASE_URL };
}