const API_BASE_URL = window.location.origin + '/api';

// Global State
let allJobs = [];

// DOM Elements
const jobsGrid = document.getElementById('jobsGrid');
const searchForm = document.getElementById('searchForm');
const applicationModal = document.getElementById('applicationModal');
const applicationForm = document.getElementById('applicationForm');
const closeModal = document.getElementById('closeModal');
const noJobsMessage = document.getElementById('noJobsMessage');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadJobs();
    setupEventListeners();
});

function setupEventListeners() {
    searchForm?.addEventListener('submit', handleSearch);
    closeModal?.addEventListener('click', () => {
        applicationModal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === applicationModal) {
            applicationModal.style.display = 'none';
        }
    });

    applicationForm?.addEventListener('submit', handleApplicationSubmit);
}

// Load jobs from API
async function loadJobs() {
    try {
        jobsGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 3rem;"><i class="fas fa-spinner fa-spin fa-2x" style="color: var(--primary)"></i></div>';

        const response = await fetch(`${API_BASE_URL}/jobs`);
        if (!response.ok) throw new Error('Failed to fetch jobs');

        allJobs = await response.json();
        displayJobs(allJobs);
    } catch (error) {
        console.error('Error:', error);
        showToast('error', 'Unable to load jobs. Please try again.');
    }
}

function displayJobs(jobs) {
    if (jobs.length === 0) {
        jobsGrid.style.display = 'none';
        noJobsMessage.style.display = 'block';
        return;
    }

    jobsGrid.style.display = 'grid';
    noJobsMessage.style.display = 'none';

    jobsGrid.innerHTML = jobs.map(job => `
        <div class="job-card">
            <span class="job-type-badge">${job.job_type}</span>
            <h3 class="job-title">${job.title}</h3>
            <div class="job-company">
                <i class="fas fa-building"></i> ${job.company}
            </div>
            
            <div class="job-meta-list">
                <div class="job-meta-item">
                    <i class="fas fa-map-marker-alt"></i> ${job.location}
                </div>
                <div class="job-meta-item">
                    <i class="fas fa-layer-group"></i> ${job.category}
                </div>
                <div class="job-meta-item">
                    <i class="fas fa-money-bill-wave"></i> ${job.salary || 'Negotiable'}
                </div>
                <div class="job-meta-item">
                    <i class="fas fa-clock"></i> ${new Date(job.posted_date).toLocaleDateString()}
                </div>
            </div>
            
            <p style="font-size: 0.875rem; color: var(--gray); margin-bottom: 1.5rem;">
                ${job.description.substring(0, 120)}...
            </p>
            
            <div class="job-footer">
                <span class="salary-text">${job.salary === 'Negotiable' ? 'Negotiable' : job.salary}</span>
                <button class="btn btn-primary" onclick="openApplyModal(${job.id}, '${job.title}')">
                    Apply Now
                </button>
            </div>
        </div>
    `).join('');
}

function handleSearch(e) {
    e.preventDefault();

    const searchTerm = document.getElementById('search').value.toLowerCase();
    const location = document.getElementById('location').value.toLowerCase();
    const category = document.getElementById('category').value;
    const type = document.getElementById('type').value;

    const filtered = allJobs.filter(job => {
        const matchesSearch = job.title.toLowerCase().includes(searchTerm) ||
            job.company.toLowerCase().includes(searchTerm) ||
            job.description.toLowerCase().includes(searchTerm);
        const matchesLocation = !location || job.location.toLowerCase().includes(location);
        const matchesCategory = !category || job.category === category;
        const matchesType = !type || job.job_type === type;

        return matchesSearch && matchesLocation && matchesCategory && matchesType;
    });

    displayJobs(filtered);
}

function openApplyModal(id, title) {
    document.getElementById('jobId').value = id;
    document.getElementById('modalTitle').textContent = `Apply for: ${title}`;
    applicationModal.style.display = 'flex';
}

async function handleApplicationSubmit(e) {
    e.preventDefault();
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const jobId = document.getElementById('jobId').value;

    const formData = {
        name: document.getElementById('applicantName').value,
        email: document.getElementById('applicantEmail').value,
        experience: document.getElementById('experience').value,
        phone: 'N/A' // Default since we simplified form
    };

    try {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';

        const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/apply`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            showToast('success', 'Application submitted successfully!');
            applicationModal.style.display = 'none';
            applicationForm.reset();
        } else {
            throw new Error();
        }
    } catch (error) {
        showToast('error', 'Failed to submit application.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Application';
    }
}

function showToast(type, message) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast`;
    toast.style.borderLeft = `4px solid ${type === 'success' ? 'var(--success)' : 'var(--error)'}`;

    toast.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}" 
           style="color: ${type === 'success' ? 'var(--success)' : 'var(--error)'}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}