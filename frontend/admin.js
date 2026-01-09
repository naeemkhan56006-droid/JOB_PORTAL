const API_BASE_URL = window.location.origin + '/api';
let adminKey = localStorage.getItem('njp_admin_key');

// DOM Elements
const loginScreen = document.getElementById('loginScreen');
const dashboardScreen = document.getElementById('dashboardScreen');
const loginForm = document.getElementById('loginForm');
const logoutBtn = document.getElementById('logoutBtn');
const userInfo = document.getElementById('userInfo');

// Init
document.addEventListener('DOMContentLoaded', () => {
    if (adminKey) {
        showDashboard();
    }
    setupEventListeners();
});

function setupEventListeners() {
    loginForm.addEventListener('submit', handleLogin);
    logoutBtn.addEventListener('click', handleLogout);

    document.querySelectorAll('.admin-nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const tab = e.currentTarget.dataset.tab;
            showTab(tab);
        });
    });

    document.getElementById('postJobForm').addEventListener('submit', handlePostJob);
}

function handleLogin(e) {
    e.preventDefault();
    const key = document.getElementById('adminPassword').value;
    if (key === 'njp123') {
        adminKey = key;
        localStorage.setItem('njp_admin_key', key);
        showDashboard();
        showToast('success', 'Access Granted');
    } else {
        showToast('error', 'Invalid Access Key');
    }
}

function handleLogout() {
    localStorage.removeItem('njp_admin_key');
    location.reload();
}

function showDashboard() {
    loginScreen.style.display = 'none';
    dashboardScreen.style.display = 'block';
    userInfo.style.display = 'flex';
    loadStats();
    loadJobsTable();
    loadApplications();
}

function showTab(tabName) {
    document.querySelectorAll('[id$="Tab"]').forEach(t => t.style.display = 'none');
    document.getElementById(`${tabName}Tab`).style.display = 'block';

    document.querySelectorAll('.admin-nav-link').forEach(l => l.classList.remove('active'));
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
}

async function loadStats() {
    try {
        const res = await fetch(`${API_BASE_URL}/stats`, { headers: { 'X-Admin-Password': adminKey } });
        const data = await res.json();
        document.getElementById('totalJobs').textContent = data.total_jobs;
        document.getElementById('activeJobs').textContent = data.active_jobs;
        document.getElementById('totalApps').textContent = data.total_applications;
    } catch (e) { console.error(e); }
}

async function loadJobsTable() {
    try {
        const res = await fetch(`${API_BASE_URL}/jobs/all`, { headers: { 'X-Admin-Password': adminKey } });
        const jobs = await res.json();
        const tbody = document.querySelector('#jobsTable tbody');
        tbody.innerHTML = jobs.map(j => `
            <tr>
                <td style="font-weight: 600;">${j.title}</td>
                <td>${j.category}</td>
                <td><span class="badge" style="background:var(--light)">${j.job_type}</span></td>
                <td>${j.application_count} Candidates</td>
                <td>
                    <button class="btn btn-outline" style="padding: 0.25rem 0.5rem;" onclick="deleteJob(${j.id})"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `).join('');
    } catch (e) { console.error(e); }
}

async function loadApplications() {
    try {
        const res = await fetch(`${API_BASE_URL}/applications`, { headers: { 'X-Admin-Password': adminKey } });
        const apps = await res.json();
        const tbody = document.querySelector('#appsTable tbody');
        tbody.innerHTML = apps.map(a => `
            <tr>
                <td style="font-weight: 600;">${a.name}</td>
                <td>${a.email}</td>
                <td>${a.experience} Years</td>
                <td>${new Date(a.applied_date).toLocaleDateString()}</td>
                <td><span class="badge badge-pending">Pending Review</span></td>
            </tr>
        `).join('');
    } catch (e) { console.error(e); }
}

async function handlePostJob(e) {
    e.preventDefault();
    const data = {
        title: document.getElementById('jobTitle').value,
        company: document.getElementById('jobCompany').value,
        location: document.getElementById('jobLocation').value,
        salary: document.getElementById('jobSalary').value,
        category: document.getElementById('jobCategory').value,
        job_type: document.getElementById('jobType').value,
        description: document.getElementById('jobDescription').value
    };

    try {
        const res = await fetch(`${API_BASE_URL}/jobs`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-Admin-Password': adminKey },
            body: JSON.stringify(data)
        });
        if (res.ok) {
            showToast('success', 'Job Listing Published');
            closeModal('postJobModal');
            loadStats();
            loadJobsTable();
        }
    } catch (e) { showToast('error', 'Failed to publish'); }
}

async function deleteJob(id) {
    if (!confirm('Permanent delete this listing?')) return;
    try {
        await fetch(`${API_BASE_URL}/jobs/${id}`, {
            method: 'DELETE',
            headers: { 'X-Admin-Password': adminKey }
        });
        loadJobsTable();
        loadStats();
        showToast('success', 'Listing Removed');
    } catch (e) { console.error(e); }
}

function showPostJobModal() { document.getElementById('postJobModal').style.display = 'flex'; }
function closeModal(id) { document.getElementById(id).style.display = 'none'; }

function showToast(type, message) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast`;
    toast.style.borderLeft = `4px solid ${type === 'success' ? 'var(--success)' : 'var(--error)'}`;
    toast.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}" style="color: ${type === 'success' ? 'var(--success)' : 'var(--error)'}"></i><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, 3000);
}
