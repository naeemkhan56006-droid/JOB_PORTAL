const API_URL = window.location.origin + '/api';

// Utility functions
function showAlert(message, type = 'info') {
    alert(message);
}

// Load jobs
async function loadJobs() {
    try {
        const response = await fetch(`${API_URL}/jobs`);
        const jobs = await response.json();
        displayJobs(jobs);
    } catch (error) {
        showAlert('Failed to load jobs', 'error');
    }
}

// Display jobs
function displayJobs(jobs) {
    const container = document.getElementById('jobsContainer');
    if (!container) return;
    
    container.innerHTML = jobs.map(job => `
        <div class="job-card">
            <h3>${job.title}</h3>
            <p><strong>Company:</strong> ${job.company}</p>
            <p><strong>Location:</strong> ${job.location}</p>
            <p><strong>Salary:</strong> ${job.salary}</p>
            <p><strong>Type:</strong> ${job.job_type}</p>
            <p>${job.description.substring(0, 150)}...</p>
            <button onclick="applyForJob(${job.id})" class="btn">Apply Now</button>
        </div>
    `).join('');
}

// Apply for job
async function applyForJob(jobId) {
    const name = prompt('Enter your name:');
    const email = prompt('Enter your email:');
    const phone = prompt('Enter your phone:');
    
    if (!name || !email || !phone) {
        showAlert('All fields are required', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/jobs/${jobId}/apply`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name, email, phone,
                resume_url: '',
                cover_letter: '',
                experience: 0,
                skills: ''
            })
        });
        
        if (response.ok) {
            showAlert('Application submitted successfully!', 'success');
        } else {
            showAlert('Failed to submit application', 'error');
        }
    } catch (error) {
        showAlert('Network error', 'error');
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
        loadJobs();
    }
});