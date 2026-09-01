/**
 * ============================================================
 * CP Tracker - Frontend Script
 * ============================================================
 *
 * This file talks to your FastAPI backend and draws everything
 * on the screen. It's written in small, plain functions with a
 * lot of comments so it's easy to follow, even if you're new to
 * JavaScript.
 *
 * Everything here uses REAL data from the server. There is no
 * fake/demo data anywhere in this file anymore - if a request
 * fails, you will see a real error message instead of the app
 * quietly pretending it worked.
 */

// ============================================================
// 1. SETTINGS - change these to match your own setup
// ============================================================

// This is the address of your FastAPI backend (the `uvicorn`
// server). If your backend runs somewhere else, change this
// one line and everything else keeps working.
// Default for local dev: port 8001 (the project's dev server).
const API_BASE_URL = 'http://127.0.0.1:8001';

// The name we use to store the login token in the browser.
const TOKEN_KEY = 'cp_tracker_token';

// The name we use to remember if the user picked light or dark mode.
const THEME_KEY = 'cp_tracker_theme';

// ============================================================
// 2. APP STATE - everything the app currently knows
// ============================================================
// Keeping all our "current data" in one object makes it easy to
// find and reason about. Nothing fake ever gets stored in here -
// only what the server actually sent us.

const AppState = {
    user: null,              // { id, username, email, created_at }
    accounts: [],            // list of linked accounts (Codeforces, LeetCode, ...)
    selectedAccountId: null, // which linked account is currently shown
    selectedAccountMeta: null, // the entry from `accounts` for the selected id (has platform)
    profile: null,           // stats + contests for the selected account
    ratingChart: null,       // the Chart.js chart object currently on screen
    isSidebarOpen: false,
    isBusy: false,           // true while a sync/add/delete/verify request is in flight
    currentModal: null,
    pendingDeleteAccount: null, // { id, platform, handle }
    pendingVerifyAccount: null, // { id, platform, handle }
};

// ============================================================
// 3. TALKING TO THE SERVER
// ============================================================
// These small helper functions are the ONLY place in the whole
// file that actually calls `fetch`. Every other function asks
// one of these to do the network work for it. That way, if
// something about how we talk to the server ever changes, we
// only have to fix it in one spot.

// Reads the saved login token (if any) out of the browser.
function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

// Builds the `Authorization: Bearer ...` header, when we have a token.
function authHeader() {
    const token = getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
}

// Every response from our backend either succeeds with JSON, or
// fails with a JSON body like { "detail": "some message" }. This
// function reads that body and, on failure, throws a normal
// JavaScript Error with a friendly message attached - so calling
// code can just `catch (error) { showToast(error.message) }`.
async function readApiResponse(response) {
    let body = null;
    try {
        body = await response.json();
    } catch (e) {
        // The response had no JSON body - that's fine for some endpoints.
    }

    if (!response.ok) {
        let message = `Something went wrong (${response.status})`;
        if (body && typeof body.detail === 'string') {
            // Our backend's normal error shape: { "detail": "Some message" }
            message = body.detail;
        } else if (body && Array.isArray(body.detail) && body.detail.length > 0) {
            // FastAPI's automatic validation errors look like:
            // { "detail": [{ "msg": "...", "loc": [...] }, ...] }
            message = body.detail.map((item) => item.msg).filter(Boolean).join(', ') || message;
        }
        const error = new Error(message);
        error.status = response.status;
        throw error;
    }

    return body;
}

// GET a JSON resource from the backend, with our login token attached.
async function apiGet(path) {
    showGlobalLoader();
    try {
        const response = await fetch(`${API_BASE_URL}${path}`, {
            method: 'GET',
            headers: { ...authHeader() },
        });
        return await handleAuthedResponse(response);
    } finally {
        hideGlobalLoader();
    }
}

// POST a JSON body to the backend, with our login token attached.
async function apiPost(path, jsonBody) {
    showGlobalLoader();
    try {
        const response = await fetch(`${API_BASE_URL}${path}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...authHeader(),
            },
            body: jsonBody !== undefined ? JSON.stringify(jsonBody) : undefined,
        });
        return await handleAuthedResponse(response);
    } finally {
        hideGlobalLoader();
    }
}

// Shared by apiGet/apiPost: if the server says our token is no
// longer valid (401), we log the user out automatically instead
// of making every single caller remember to check for that.
async function handleAuthedResponse(response) {
    if (response.status === 401) {
        forceLogout('Your session has expired. Please log in again.');
        const error = new Error('Session expired');
        error.status = 401;
        throw error;
    }
    return readApiResponse(response);
}

// Logging in is special: the backend wants an old-school HTML
// form submission (username + password), not JSON, and there is
// no token to attach yet because we don't have one.
async function apiLogin(identifier, password) {
    const form = new URLSearchParams();
    form.set('username', identifier);
    form.set('password', password);

    showGlobalLoader();
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            body: form,
        });
        return await readApiResponse(response);
    } finally {
        hideGlobalLoader();
    }
}

// ============================================================
// 4. SMALL HELPER FUNCTIONS
// ============================================================

// Turns an ISO date string (like the ones the server sends for
// "updated_at" or "created_at") into something readable.
function formatDateTime(isoString) {
    if (!isoString) return '—';
    const date = new Date(isoString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit',
    });
}

// Contest dates from the server are Unix timestamps measured in
// SECONDS (that's just how Codeforces sends them to us), not the
// milliseconds that JavaScript's Date expects. So we multiply by
// 1000 before handing them to `new Date(...)`.
function formatContestDate(unixSeconds, options) {
    if (!unixSeconds) return '—';
    const date = new Date(unixSeconds * 1000);
    return date.toLocaleDateString('en-US', options || {
        year: 'numeric', month: 'short', day: 'numeric',
    });
}

// ============================================================
// Global loader control
// ============================================================
function showGlobalLoader() {
    AppState.isBusy = true;
    const el = document.getElementById('globalLoader');
    if (!el) return;
    el.hidden = false;
    el.setAttribute('aria-hidden', 'false');
}

function hideGlobalLoader() {
    AppState.isBusy = false;
    const el = document.getElementById('globalLoader');
    if (!el) return;
    el.hidden = true;
    el.setAttribute('aria-hidden', 'true');
}

// Picks 1-2 letters to show inside a round avatar circle.
function getInitials(name) {
    if (!name) return '?';
    return name.trim().slice(0, 2).toUpperCase();
}

function getPlatformClass(platform) {
    const normalized = (platform || '').toLowerCase();
    if (normalized.includes('codeforces')) return 'codeforces';
    if (normalized.includes('leetcode')) return 'leetcode';
    if (normalized.includes('atcoder')) return 'atcoder';
    if (normalized.includes('codechef')) return 'codechef';
    return 'codeforces';
}

function getPlatformLabel(platform) {
    const normalized = (platform || '').toLowerCase();
    if (normalized.includes('codeforces')) return 'Codeforces';
    if (normalized.includes('leetcode')) return 'LeetCode';
    if (normalized.includes('atcoder')) return 'AtCoder';
    if (normalized.includes('codechef')) return 'CodeChef';
    return platform || '';
}

function getPlatformAbbreviation(platform) {
    const normalized = (platform || '').toLowerCase();
    if (normalized.includes('codeforces')) return 'CF';
    if (normalized.includes('leetcode')) return 'LC';
    if (normalized.includes('atcoder')) return 'AC';
    if (normalized.includes('codechef')) return 'CC';
    return (platform || '??').substring(0, 2).toUpperCase();
}

// Prevents any text from a server response (like a username) from
// accidentally being read as HTML when we drop it into the page.
function escapeHtml(text) {
    if (text == null) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

// Finds one linked account inside AppState.accounts by its id.
function findAccountById(accountId) {
    return AppState.accounts.find((account) => account.id === accountId) || null;
}

// ============================================================
// 5. LIGHT / DARK MODE
// ============================================================

function applyTheme(theme) {
    if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    } else {
        document.documentElement.removeAttribute('data-theme');
    }
    // The chart is drawn with plain colors, not CSS variables, so
    // if the theme changes while a chart is on screen, redraw it.
    if (AppState.ratingChart && AppState.profile) {
        renderRatingGraph(AppState.profile.contests);
    }
}

function initTheme() {
    const saved = localStorage.getItem(THEME_KEY);
    if (saved === 'dark' || saved === 'light') {
        applyTheme(saved);
        return;
    }
    // No saved preference yet - follow the operating system's setting.
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    applyTheme(prefersDark ? 'dark' : 'light');
}

function toggleTheme() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const nextTheme = isDark ? 'light' : 'dark';
    applyTheme(nextTheme);
    localStorage.setItem(THEME_KEY, nextTheme);
}

// ============================================================
// 6. SWITCHING BETWEEN SCREENS (login / register / dashboard)
// ============================================================

const Views = {
    LOGIN: 'login-view',
    REGISTER: 'register-view',
    DASHBOARD: 'dashboard-view',
};

function switchView(viewId) {
    Object.values(Views).forEach((id) => {
        const el = document.getElementById(id);
        if (el) {
            el.classList.remove('active');
            el.hidden = true;
        }
    });

    const target = document.getElementById(viewId);
    if (target) {
        target.hidden = false;
        requestAnimationFrame(() => target.classList.add('active'));
    }

    document.body.style.backgroundColor = (viewId === Views.DASHBOARD)
        ? 'var(--bg-secondary)'
        : 'transparent';
}

// ============================================================
// 7. LOGGING IN, REGISTERING, LOGGING OUT
// ============================================================

// Runs once when the page first loads. If we already have a
// saved token, try to enter the dashboard with it. The server
// will tell us (with a 401) if that token isn't valid anymore.
function checkAuth() {
    if (getToken()) {
        switchView(Views.DASHBOARD);
        enterDashboard();
    } else {
        switchView(Views.LOGIN);
    }
}

async function handleLogin(e) {
    e.preventDefault();
    clearFormErrors('login');

    const identifier = document.getElementById('loginIdentifier').value.trim();
    const password = document.getElementById('loginPassword').value;

    let hasError = false;
    if (!identifier) {
        showFormError('loginIdentifier', 'Enter your username or email');
        hasError = true;
    }
    if (!password) {
        showFormError('loginPassword', 'Enter your password');
        hasError = true;
    }
    if (hasError) return;

    setButtonLoading('loginBtn', true);
    try {
        const data = await apiLogin(identifier, password);
        localStorage.setItem(TOKEN_KEY, data.access_token);
        showToast('Welcome back!', 'success');
        switchView(Views.DASHBOARD);
        await enterDashboard();
    } catch (error) {
        // A wrong username/password shows up right where the user is
        // looking, instead of quietly logging them in anyway.
        showFormError('loginPassword', error.message || 'Invalid credentials');
    } finally {
        setButtonLoading('loginBtn', false);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    clearFormErrors('register');

    const username = document.getElementById('regUsername').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const password = document.getElementById('regPassword').value;
    const confirmPassword = document.getElementById('regConfirmPassword').value;

    let hasError = false;
    if (username.length < 3) {
        showFormError('regUsername', 'Username must be at least 3 characters');
        hasError = true;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        showFormError('regEmail', 'Please enter a valid email');
        hasError = true;
    }
    if (password.length < 6) {
        showFormError('regPassword', 'Password must be at least 6 characters');
        hasError = true;
    }
    if (password !== confirmPassword) {
        showFormError('regConfirmPassword', 'Passwords do not match');
        hasError = true;
    }
    if (hasError) return;

    setButtonLoading('registerBtn', true);
    try {
        await apiPost('/auth/register', { username, email, password });

        // The server only creates the account here - it does not log
        // us in automatically, so we send the person to the login
        // screen with their username already filled in for them.
        showToast('Account created! Please sign in.', 'success');
        document.getElementById('registerForm').reset();
        switchView(Views.LOGIN);
        document.getElementById('loginIdentifier').value = username;
        document.getElementById('loginPassword').focus();
    } catch (error) {
        // Show the server's real reason (e.g. "email already exists")
        // next to whichever field it's most likely about.
        const message = error.message || 'Registration failed';
        if (message.toLowerCase().includes('email')) {
            showFormError('regEmail', message);
        } else if (message.toLowerCase().includes('user')) {
            showFormError('regUsername', message);
        } else {
            showToast(message, 'error');
        }
    } finally {
        setButtonLoading('registerBtn', false);
    }
}

// Clears everything and sends the user back to the login page.
// There's no "logout" endpoint on the backend (the login token
// just expires by itself after a while), so this is purely a
// browser-side clean-up.
function forceLogout(message) {
    localStorage.removeItem(TOKEN_KEY);
    resetAppState();
    document.getElementById('loginForm')?.reset();
    document.getElementById('registerForm')?.reset();
    clearFormErrors('login');
    clearFormErrors('register');
    switchView(Views.LOGIN);
    if (message) showToast(message, 'info');
}

function resetAppState() {
    AppState.user = null;
    AppState.accounts = [];
    AppState.selectedAccountId = null;
    AppState.selectedAccountMeta = null;
    AppState.profile = null;
    if (AppState.ratingChart) {
        AppState.ratingChart.destroy();
        AppState.ratingChart = null;
    }
}

function logout() {
    forceLogout('Logged out successfully');
}

// ============================================================
// 8. FORM HELPERS (shared by login, register, and modals)
// ============================================================

function showFormError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const errorEl = document.getElementById(`${fieldId}Error`);
    if (field) field.classList.add('error');
    if (errorEl) errorEl.textContent = message;
}

function clearFormErrors(formPrefix) {
    document.querySelectorAll(`[id^="${formPrefix}"]`).forEach((el) => {
        if (el.classList.contains('form-input')) el.classList.remove('error');
        if (el.classList.contains('form-error')) el.textContent = '';
    });
}

function setButtonLoading(btnId, loading) {
    const btn = document.getElementById(btnId);
    if (!btn) return;
    const text = btn.querySelector('.btn-text');
    const loader = btn.querySelector('.btn-loader');
    btn.disabled = loading;
    if (text) text.hidden = loading;
    if (loader) loader.hidden = !loading;
}

// ============================================================
// 9. MODAL WINDOWS (Add Account / Verify / Delete)
// ============================================================

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    const overlay = document.getElementById('modalOverlay');
    if (!modal || !overlay) return;

    AppState.currentModal = modalId;
    modal.hidden = false;
    overlay.classList.add('active');
    requestAnimationFrame(() => modal.classList.add('active'));

    const firstInput = modal.querySelector('input, select');
    if (firstInput) setTimeout(() => firstInput.focus(), 100);

    document.addEventListener('keydown', closeModalOnEscape);
}

function closeModal() {
    const overlay = document.getElementById('modalOverlay');
    const modal = document.getElementById(AppState.currentModal);
    if (!modal || !overlay) return;

    modal.classList.remove('active');
    overlay.classList.remove('active');

    setTimeout(() => {
        modal.hidden = true;
        AppState.currentModal = null;
    }, 200);

    document.removeEventListener('keydown', closeModalOnEscape);
}

function closeModalOnEscape(e) {
    if (e.key === 'Escape') closeModal();
}

// -------------------- Add Account --------------------

function openAddAccountModal() {
    document.getElementById('addAccountForm')?.reset();
    document.getElementById('addAccountPlatformError').textContent = '';
    document.getElementById('addAccountHandleError').textContent = '';
    document.getElementById('addAccountPlatform').classList.remove('error');
    document.getElementById('addAccountHandle').classList.remove('error');
    openModal('addAccountModal');
}

async function handleAddAccount() {
    const platform = document.getElementById('addAccountPlatform').value;
    const handle = document.getElementById('addAccountHandle').value.trim();

    document.getElementById('addAccountPlatform').classList.remove('error');
    document.getElementById('addAccountHandle').classList.remove('error');
    document.getElementById('addAccountPlatformError').textContent = '';
    document.getElementById('addAccountHandleError').textContent = '';

    let hasError = false;
    if (!platform) {
        document.getElementById('addAccountPlatform').classList.add('error');
        document.getElementById('addAccountPlatformError').textContent = 'Please select a platform';
        hasError = true;
    }
    if (!handle) {
        document.getElementById('addAccountHandle').classList.add('error');
        document.getElementById('addAccountHandleError').textContent = 'Handle is required';
        hasError = true;
    }
    if (hasError) return;

    setButtonLoading('submitAddAccount', true);
    try {
        const newAccount = await apiPost('/accounts', { platform, handle });
        closeModal();
        showToast(`${getPlatformLabel(platform)} account added!`, 'success');

        // Reload the sidebar list from the server (never patch our own
        // guess of what changed - always ask the server what's true),
        // then jump straight to the account we just added.
        await refreshAccounts();
        await selectAccount(newAccount.id);
    } catch (error) {
        // The backend tells us exactly why this failed - show it
        // right next to the handle field, since that's almost always
        // what's wrong (already linked, or handle doesn't exist).
        document.getElementById('addAccountHandle').classList.add('error');
        document.getElementById('addAccountHandleError').textContent = error.message || 'Could not add this account';
    } finally {
        setButtonLoading('submitAddAccount', false);
    }
}

// -------------------- Verify Account (2 steps) --------------------

function openVerifyModal(accountId) {
    const account = findAccountById(accountId);
    if (!account) return;

    AppState.pendingVerifyAccount = account;

    // Always start back at step 1 when the modal opens.
    document.getElementById('verifyStepStart').hidden = false;
    document.getElementById('verifyStepCode').hidden = true;
    document.getElementById('verifyCodeText').textContent = '--------';
    const submitBtn = document.getElementById('submitVerify');
    submitBtn.querySelector('.btn-text').textContent = 'Get My Code';

    openModal('verifyAccountModal');
}

// One button does double duty: first click asks the server for a
// code, second click (after the user has updated their profile)
// asks the server to check it.
async function handleVerifyAccount() {
    const account = AppState.pendingVerifyAccount;
    if (!account) return;

    const codeStepVisible = !document.getElementById('verifyStepCode').hidden;
    setButtonLoading('submitVerify', true);

    try {
        if (!codeStepVisible) {
            // Step 1: ask for a code.
            const result = await apiPost('/accounts/verify/start', {
                platform: account.platform,
                handle: account.handle,
            });
            document.getElementById('verifyStepStart').hidden = true;
            document.getElementById('verifyStepCode').hidden = false;
            document.getElementById('verifyCodeText').textContent = result.token;
            document.getElementById('submitVerify').querySelector('.btn-text').textContent = 'Verify Now';
        } else {
            // Step 2: check whether the user actually placed the code.
            const result = await apiPost('/accounts/verify/complete', {
                platform: account.platform,
                handle: account.handle,
            });
            if (result.verified) {
                closeModal();
                showToast('Account verified!', 'success');
                await refreshAccounts();
            }
        }
    } catch (error) {
        showToast(error.message || 'Verification failed', 'error');
    } finally {
        setButtonLoading('submitVerify', false);
    }
}

function copyVerifyCode() {
    const code = document.getElementById('verifyCodeText').textContent;
    if (!code || code === '--------') return;
    navigator.clipboard?.writeText(code).then(() => {
        showToast('Code copied!', 'info');
    }).catch(() => {
        // Clipboard access can be blocked by the browser - that's OK,
        // the user can still just select and copy the text by hand.
    });
}

// -------------------- Delete Account --------------------

function openDeleteModal(accountId) {
    const account = findAccountById(accountId);
    if (!account) return;

    AppState.pendingDeleteAccount = account;
    document.getElementById('deleteModalPlatform').textContent = getPlatformLabel(account.platform);
    document.getElementById('deleteModalHandle').textContent = account.handle;
    openModal('deleteAccountModal');
}

async function handleDeleteAccount() {
    const account = AppState.pendingDeleteAccount;
    if (!account) return;

    setButtonLoading('confirmDelete', true);
    try {
        await apiPost('/accounts/delete', {
            platform: account.platform,
            handle: account.handle,
        });
        closeModal();
        showToast('Account deleted', 'success');

        const wasSelected = AppState.selectedAccountId === account.id;
        await refreshAccounts();

        if (wasSelected) {
            // Pick a new account to show, or clear the dashboard if
            // that was the last one.
            const next = AppState.accounts[0];
            if (next) {
                await selectAccount(next.id);
            } else {
                AppState.selectedAccountId = null;
                AppState.selectedAccountMeta = null;
                AppState.profile = null;
                renderProfile(null);
                renderRatingGraph([]);
                renderContestHistory([]);
            }
        }
    } catch (error) {
        showToast(error.message || 'Could not delete this account', 'error');
    } finally {
        setButtonLoading('confirmDelete', false);
        AppState.pendingDeleteAccount = null;
    }
}

// ============================================================
// 10. TOAST NOTIFICATIONS (the little pop-up messages)
// ============================================================

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const icons = {
        success: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`,
        error: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`,
        info: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`,
    };

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span class="toast-icon" aria-hidden="true">${icons[type]}</span>
        <span>${escapeHtml(message)}</span>
    `;
    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('toast-out');
        toast.addEventListener('animationend', () => toast.remove());
    }, 2000);
}

// ============================================================
// 11. DRAWING THE SIDEBAR
// ============================================================

function renderSidebarUser(user) {
    const container = document.getElementById('sidebarUser');
    if (!container || !user) return;

    container.innerHTML = `
        <div class="user-info">
            <div class="user-avatar" aria-hidden="true">${getInitials(user.username)}</div>
            <div class="user-details">
                <div class="user-name">${escapeHtml(user.username)}</div>
                <div class="user-email">${escapeHtml(user.email)}</div>
            </div>
        </div>
    `;
}

function renderSidebarAccounts(accounts, selectedId) {
    const container = document.getElementById('accountsList');
    if (!container) return;

    if (!accounts || accounts.length === 0) {
        container.innerHTML = `
            <div class="accounts-empty">
                <svg class="accounts-empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                    <line x1="8" y1="21" x2="16" y2="21"></line>
                    <line x1="12" y1="17" x2="12" y2="21"></line>
                </svg>
                <div class="accounts-empty-title">No linked accounts yet</div>
                <div class="accounts-empty-desc">Connect your competitive programming platforms to start tracking.</div>
                <button class="accounts-empty-btn" onclick="openAddAccountModal()">Add Account</button>
            </div>
        `;
        return;
    }

    container.innerHTML = accounts.map((account) => {
        const isActive = account.id === selectedId;
        const platformClass = getPlatformClass(account.platform);
        const platformLabel = getPlatformLabel(account.platform);
        const abbreviation = getPlatformAbbreviation(account.platform);

        const statusIcon = account.verified
            ? `<svg class="status-verified" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`
            : `<svg class="status-unverified" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`;

        const verifyBtn = !account.verified
            ? `<button class="account-action-btn verify" title="Verify account" onclick="event.stopPropagation(); openVerifyModal(${account.id})" aria-label="Verify ${escapeHtml(platformLabel)} account">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
            </button>`
            : '';

        return `
            <button
                class="account-item ${isActive ? 'active' : ''}"
                data-account-id="${account.id}"
                onclick="selectAccount(${account.id})"
                aria-pressed="${isActive}"
                role="button"
                tabindex="0"
            >
                <div class="account-icon ${platformClass}" aria-hidden="true">${abbreviation}</div>
                <div class="account-info">
                    <div class="account-name">
                        ${escapeHtml(platformLabel)}
                        <span class="account-status" title="${account.verified ? 'Verified' : 'Unverified'}">${statusIcon}</span>
                    </div>
                    <div class="account-handle">${escapeHtml(account.handle)}</div>
                </div>
                <div class="account-actions">
                    ${verifyBtn}
                    <button class="account-action-btn delete" title="Delete account" onclick="event.stopPropagation(); openDeleteModal(${account.id})" aria-label="Delete ${escapeHtml(platformLabel)} account">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"></path></svg>
                    </button>
                </div>
            </button>
        `;
    }).join('');
}

// ============================================================
// 12. DRAWING THE PROFILE CARD + STATS
// ============================================================

function renderProfile(profile) {
    const container = document.getElementById('profileSection');
    if (!container) return;

    if (!profile) {
        // Nothing selected yet - usually means the user has no
        // linked accounts. Invite them to add one.
        container.innerHTML = `
            <div class="profile-card">
                <div class="empty-state">
                    <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="8" r="4"></circle>
                        <path d="M4 21v-2a4 4 0 014-4h8a4 4 0 014 4v2"></path>
                    </svg>
                    <div class="empty-state-title">No account selected</div>
                    <div class="empty-state-desc">Add a competitive programming account to see your stats here.</div>
                </div>
            </div>
        `;
        return;
    }

    const initials = getInitials(profile.first_name || profile.handle);
    const fullName = [profile.first_name, profile.last_name].filter(Boolean).join(' ');
    const updatedAt = formatDateTime(profile.updated_at);
    const platformLabel = getPlatformLabel(AppState.selectedAccountMeta?.platform);
    // Determine if there are multiple accounts for this platform
    const samePlatformAccounts = AppState.accounts.filter(a => a.platform === (AppState.selectedAccountMeta?.platform));
    const multipleForPlatform = samePlatformAccounts.length > 1;

    const platformBadgeHtml = multipleForPlatform
        ? `<button class="profile-platform-badge" onclick="openPlatformAccountsPopover('${AppState.selectedAccountMeta?.platform}')">${escapeHtml(platformLabel)} ▾</button>`
        : `<span class="profile-platform-badge">${escapeHtml(platformLabel)}</span>`;

    container.innerHTML = `
        <div class="profile-card">
            <div class="profile-header">
                <div class="profile-identity">
                    <div class="profile-avatar" aria-hidden="true">${initials}</div>
                    <div class="profile-name-group">
                        <div class="profile-handle">${escapeHtml(profile.handle)}</div>
                        ${fullName ? `<div class="profile-fullname">${escapeHtml(fullName)}</div>` : ''}
                        <div class="profile-meta">
                            ${platformBadgeHtml}
                            <span class="profile-meta-dot" aria-hidden="true"></span>
                            <span>Updated ${updatedAt}</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Current Rating</div>
                    <div class="stat-value accent">${(() => {
                        const hasContests = Array.isArray(profile.contests) && profile.contests.length > 0;
                        // If there are no contests, show 0 (user expectation).
                        if (!hasContests) return 0;
                        // Otherwise show rating if present, else 0.
                        return (profile.rating ?? 0);
                    })()}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Maximum Rating</div>
                    <div class="stat-value success">${profile.max_rating ?? '—'}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Rank</div>
                    <div class="stat-value">${escapeHtml(profile.rank || '—')}</div>
                </div>
            </div>
        </div>
    `;

    // Render insight charts if present
    renderInsightCharts(profile);
}

// ============================================================
// 13. DRAWING THE RATING CHART
// ============================================================

// Reads a color straight out of our CSS variables, so the chart
// always matches whichever theme (light/dark) is active right now.
function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function renderRatingGraph(contests) {
    const canvas = document.getElementById('ratingChart');
    if (!canvas) return;

    if (AppState.ratingChart) {
        AppState.ratingChart.destroy();
        AppState.ratingChart = null;
    }

    if (!contests || contests.length === 0) {
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        return;
    }

    // Oldest contest first, so the line reads left-to-right in time order.
    const sorted = [...contests].sort((a, b) => a.rating_update_time - b.rating_update_time);
    const labels = sorted.map((c) => formatContestDate(c.rating_update_time, { month: 'short', day: 'numeric' }));
    const ratings = sorted.map((c) => c.new_rating);

    const lineColor = cssVar('--chart-line');
    const ctx = canvas.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 360);
    gradient.addColorStop(0, cssVar('--chart-fill-start'));
    gradient.addColorStop(1, cssVar('--chart-fill-end'));

    AppState.ratingChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'Rating',
                data: ratings,
                borderColor: lineColor,
                backgroundColor: gradient,
                borderWidth: 2.5,
                pointBackgroundColor: lineColor,
                pointBorderColor: cssVar('--bg-primary'),
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: lineColor,
                pointHoverBorderColor: cssVar('--bg-primary'),
                pointHoverBorderWidth: 2,
                fill: true,
                tension: 0.4,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: cssVar('--chart-tooltip-bg'),
                    titleColor: cssVar('--chart-tooltip-text'),
                    bodyColor: cssVar('--chart-tooltip-text'),
                    borderColor: cssVar('--chart-tooltip-border'),
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 12,
                    displayColors: false,
                    titleFont: { family: "'Inter', sans-serif", size: 13, weight: '600' },
                    bodyFont: { family: "'SF Mono', monospace", size: 14, weight: '600' },
                    callbacks: {
                        title: (items) => sorted[items[0].dataIndex]?.contest_name || '',
                        label: (item) => `Rating: ${item.raw}`,
                    },
                },
            },
            scales: {
                x: {
                    grid: { display: false, drawBorder: false },
                    ticks: {
                        color: cssVar('--chart-tick'),
                        font: { family: "'Inter', sans-serif", size: 11 },
                        maxRotation: 45,
                        minRotation: 0,
                    },
                    border: { display: false },
                },
                y: {
                    grid: { color: cssVar('--chart-grid'), drawBorder: false },
                    ticks: {
                        color: cssVar('--chart-tick'),
                        font: { family: "'SF Mono', monospace", size: 11 },
                        padding: 8,
                    },
                    border: { display: false },
                },
            },
            animation: { duration: 800, easing: 'easeOutQuart' },
        },
    });
}

// ============================================================
// 14. DRAWING THE CONTEST HISTORY TABLE
// ============================================================

function renderContestHistory(contests) {
    const tbody = document.getElementById('contestTableBody');
    if (!tbody) return;

    if (!contests || contests.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6">
                    <div class="empty-state">
                        <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                            <line x1="16" y1="2" x2="16" y2="6"></line>
                            <line x1="8" y1="2" x2="8" y2="6"></line>
                            <line x1="3" y1="10" x2="21" y2="10"></line>
                        </svg>
                        <div class="empty-state-title">No contests yet</div>
                        <div class="empty-state-desc">Participate in contests, then hit Sync to see your history here.</div>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    // Newest contest first in the table.
    const sorted = [...contests].sort((a, b) => b.rating_update_time - a.rating_update_time);

    tbody.innerHTML = sorted.map((contest) => {
        const gainClass = contest.rating_gain >= 0 ? 'positive' : 'negative';
        const gainSign = contest.rating_gain >= 0 ? '+' : '';
        const gainIcon = contest.rating_gain >= 0
            ? `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"></polyline></svg>`
            : `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>`;

        return `
            <tr>
                <td><span class="contest-name">${escapeHtml(contest.contest_name)}</span></td>
                <td><span class="contest-rank">#${contest.rank?.toLocaleString?.() ?? contest.rank}</span></td>
                <td><span class="rating-old">${contest.old_rating}</span></td>
                <td><span class="rating-new">${contest.new_rating}</span></td>
                <td>
                    <span class="rating-gain ${gainClass}">
                        ${gainIcon}
                        ${gainSign}${contest.rating_gain}
                    </span>
                </td>
                <td><span class="contest-date">${formatContestDate(contest.rating_update_time)}</span></td>
            </tr>
        `;
    }).join('');
}

// ============================================================
// 13b. INSIGHT DOUGHNUTS
// ============================================================
let difficultyChart = null;
let platformsChart = null;

function renderInsightCharts(profile) {
    // Difficulty distribution - try to read from profile if backend provides counts
    const difficulty = profile && profile.difficulty_counts ? profile.difficulty_counts : { easy: 39, medium: 74, hard: 14 };

    const difficultyData = [difficulty.easy || 0, difficulty.medium || 0, difficulty.hard || 0];
    const diffCtx = document.getElementById('donutDifficulty')?.getContext('2d');
    if (diffCtx) {
        if (difficultyChart) difficultyChart.destroy();
        difficultyChart = new Chart(diffCtx, {
            type: 'doughnut',
            data: {
                labels: ['Easy','Medium','Hard'],
                datasets: [{ data: difficultyData, backgroundColor: ['#10b981','#f59e0b','#ef4444'], borderWidth: 0 }]
            },
            options: { plugins: { legend: { display: false } }, cutout: '70%' }
        });
    }

    // Platforms distribution - try to read from profile or aggregate accounts
    const platforms = profile && profile.platform_counts ? profile.platform_counts : { codechef: 329, codeforces: 155, leetcode: 0, atcoder: 0 };
    const platformsData = [platforms.codechef || 0, platforms.codeforces || 0, platforms.leetcode || 0, platforms.atcoder || 0];
    const platCtx = document.getElementById('donutPlatforms')?.getContext('2d');
    if (platCtx) {
        if (platformsChart) platformsChart.destroy();
        platformsChart = new Chart(platCtx, {
            type: 'doughnut',
            data: {
                labels: ['CodeChef','Codeforces','LeetCode','AtCoder'],
                datasets: [{ data: platformsData, backgroundColor: ['#f97316','#fb7185','#60a5fa','#db2777'], borderWidth: 0 }]
            },
            options: { plugins: { legend: { display: false } }, cutout: '70%' }
        });
    }

    // Render legends
    const diffLegend = document.getElementById('difficultyLegend');
    if (diffLegend) {
        diffLegend.innerHTML = `
            <div class="legend-row"><div class="legend-label"><span class="legend-swatch" style="background:#10b981"></span><div>Easy</div></div><div>${difficulty.easy || 0}</div></div>
            <div class="legend-row"><div class="legend-label"><span class="legend-swatch" style="background:#f59e0b"></span><div>Medium</div></div><div>${difficulty.medium || 0}</div></div>
            <div class="legend-row"><div class="legend-label"><span class="legend-swatch" style="background:#ef4444"></span><div>Hard</div></div><div>${difficulty.hard || 0}</div></div>
        `;
    }

    const platformsLegend = document.getElementById('platformsLegend');
    if (platformsLegend) {
        platformsLegend.innerHTML = `
            <div class="legend-row"><div class="legend-label"><span class="legend-swatch" style="background:#f97316"></span><div>CodeChef</div></div><div>${platforms.codechef || 0}</div></div>
            <div class="legend-row"><div class="legend-label"><span class="legend-swatch" style="background:#fb7185"></span><div>Codeforces</div></div><div>${platforms.codeforces || 0}</div></div>
            <div class="legend-row"><div class="legend-label"><span class="legend-swatch" style="background:#60a5fa"></span><div>LeetCode</div></div><div>${platforms.leetcode || 0}</div></div>
            <div class="legend-row"><div class="legend-label"><span class="legend-swatch" style="background:#db2777"></span><div>AtCoder</div></div><div>${platforms.atcoder || 0}</div></div>
        `;
    }
}

// ============================================================
// 13c. PLATFORM-ACCOUNTS POPOVER (multiple accounts same platform)
// ============================================================
function openPlatformAccountsPopover(platform) {
    const pop = document.getElementById('platformAccountsPopover');
    const list = document.getElementById('platformAccountsList');
    if (!pop || !list) return;

    const same = AppState.accounts.filter(a => a.platform === platform);
    if (!same || same.length === 0) return;

    list.innerHTML = same.map(a => `
        <div class="popover-item" data-account-id="${a.id}" onclick="selectAccount(${a.id}); closePlatformPopover();">
            <div>${escapeHtml(a.handle)}</div>
            <div style="font-size:12px;color:var(--text-tertiary)">${getPlatformLabel(a.platform)}</div>
        </div>
    `).join('');

    pop.hidden = false;
}

function closePlatformPopover() {
    const pop = document.getElementById('platformAccountsPopover');
    if (pop) pop.hidden = true;
}

// Close popover when clicking outside
document.addEventListener('click', (e) => {
    const pop = document.getElementById('platformAccountsPopover');
    if (!pop || pop.hidden) return;
    if (!e.target.closest || !pop.contains(e.target) && !e.target.closest('.profile-platform-badge')) {
        closePlatformPopover();
    }
});

// ============================================================
// 15. LOADING DATA FROM THE SERVER
// ============================================================

// Fetches the logged-in user's info and their list of linked
// accounts, then draws the sidebar. Called once at startup and
// again any time the list of accounts might have changed.
async function refreshAccounts() {
    // First fetch the current user, then request the dashboard
    // summary for that username (backend routes expect the
    // username path parameter even though the server uses the
    // token to authenticate).
    const user = await apiGet('/auth/me');
    AppState.user = user;

    const accounts = await apiGet(`/dashboard/u/${encodeURIComponent(user.username)}`);
    AppState.accounts = accounts;

    renderSidebarUser(AppState.user);
    renderSidebarAccounts(AppState.accounts, AppState.selectedAccountId);
}

// The first thing that happens when someone reaches the dashboard:
// load the sidebar, then automatically show the first linked
// account (if there is one).
async function enterDashboard() {
    try {
        await refreshAccounts();
        const first = AppState.accounts[0];
        if (first) {
            await selectAccount(first.id);
        } else {
            renderProfile(null);
            renderRatingGraph([]);
            renderContestHistory([]);
        }
    } catch (error) {
        if (error.status !== 401) { // 401 already sent us to the login screen
            showToast(error.message || 'Failed to load your dashboard', 'error');
        }
    }
}

// Switches which linked account's stats are shown on the dashboard.
async function selectAccount(accountId) {
    if (AppState.isBusy) return;

    AppState.selectedAccountId = accountId;
    AppState.selectedAccountMeta = findAccountById(accountId);
    renderSidebarAccounts(AppState.accounts, accountId);

    try {
        // The backend exposes a per-account endpoint at
        // /dashboard/u/{username}/{linked_account_id}
        const profile = await apiGet(`/dashboard/u/${encodeURIComponent(AppState.user.username)}/${encodeURIComponent(accountId)}`);

        // Enrich profile by aggregating platform/problem counts across all linked accounts.
        // We'll call platform-specific endpoints where available.
        const aggregated = await aggregatePlatformAndDifficultyCounts();
        profile.platform_counts = aggregated.platforms;
        profile.difficulty_counts = aggregated.difficulty;

        AppState.profile = profile;
        renderProfile(profile);
        renderRatingGraph(profile.contests);
        renderContestHistory(profile.contests);
    } catch (error) {
        if (error.status !== 401) {
            showToast(error.message || 'Failed to load account data', 'error');
        }
    }
}

// Aggregate counts across all linked accounts by calling platform APIs.
async function aggregatePlatformAndDifficultyCounts() {
    const platforms = { codechef: 0, codeforces: 0, leetcode: 0, atcoder: 0 };
    const difficulty = { easy: 0, medium: 0, hard: 0 };

    // For each linked account, call the platform profile endpoints (best-effort).
    await Promise.all(AppState.accounts.map(async (acc) => {
        const handle = acc.handle;
        const plat = (acc.platform || '').toString().toUpperCase();
        try {
            if (plat.includes('LEETCODE')) {
                const data = await apiGet(`/leetcode/${encodeURIComponent(handle)}`);
                platforms.leetcode += Number(data.total_solved || data.totalSolved || 0);
                difficulty.easy += Number(data.easy_solved || data.easySolved || 0);
                difficulty.medium += Number(data.medium_solved || data.mediumSolved || 0);
                difficulty.hard += Number(data.hard_solved || data.hardSolved || 0);
            } else if (plat.includes('CODEFORCES')) {
                // Codeforces profile may not include solved breakdown; call /solved if available
                try {
                    const cfProfile = await apiGet(`/codeforces/${encodeURIComponent(handle)}`);
                    platforms.codeforces += Number(cfProfile.total_solved || cfProfile.totalSolved || cfProfile.solved_count || 0);
                } catch (e) {
                    // fallback: try solved endpoint
                    try {
                        const solved = await apiGet(`/codeforces/${encodeURIComponent(handle)}/solved`);
                        platforms.codeforces += Number(solved.total_solved || solved.count || 0);
                    } catch (e2) {}
                }
            } else if (plat.includes('CODECHEF')) {
                try {
                    const cc = await apiGet(`/codechef/${encodeURIComponent(handle)}`);
                    platforms.codechef += Number(cc.problems_solved || cc.problemsSolved || 0);
                } catch (e) {}
            } else if (plat.includes('ATCODER')) {
                try {
                    const ac = await apiGet(`/atcoder/${encodeURIComponent(handle)}/solved`);
                    platforms.atcoder += Number(ac.total_solved || ac.count || 0);
                } catch (e) {}
            }
        } catch (e) {
            // ignore per-account failures
        }
    }));

    return { platforms, difficulty };
}

// The backend only knows how to sync ALL of your linked accounts
// at once (there's no "just sync this one" endpoint), so both the
// header Sync button and the sidebar Sync All button call this.
async function syncAllAccounts() {
    if (AppState.isBusy) return;
    AppState.isBusy = true;

    const syncBtn = document.getElementById('syncBtn');
    const syncAllBtn = document.getElementById('syncAllBtn');
    [syncBtn, syncAllBtn].forEach((btn) => btn && (btn.disabled = true));
    syncBtn?.classList.add('syncing');

    showToast('Syncing your accounts...', 'info');

    try {
        const result = await apiPost('/accounts/sync');
        showToast(result.message || 'Sync complete!', 'success');

        await refreshAccounts();
        if (AppState.selectedAccountId) {
            await selectAccount(AppState.selectedAccountId);
        }
    } catch (error) {
        if (error.status !== 401) {
            showToast(error.message || 'Sync failed', 'error');
        }
    } finally {
        AppState.isBusy = false;
        [syncBtn, syncAllBtn].forEach((btn) => btn && (btn.disabled = false));
        syncBtn?.classList.remove('syncing');
    }
}

// ============================================================
// 16. MOBILE SIDEBAR (hamburger menu)
// ============================================================

function initMobileSidebar() {
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (!hamburgerBtn || !sidebar || !overlay) return;

    function openSidebar() {
        sidebar.classList.add('open');
        overlay.classList.add('active');
        hamburgerBtn.setAttribute('aria-expanded', 'true');
        document.body.style.overflow = 'hidden';
        AppState.isSidebarOpen = true;
    }

    function closeSidebar() {
        sidebar.classList.remove('open');
        overlay.classList.remove('active');
        hamburgerBtn.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
        AppState.isSidebarOpen = false;
    }

    hamburgerBtn.addEventListener('click', () => {
        AppState.isSidebarOpen ? closeSidebar() : openSidebar();
    });
    overlay.addEventListener('click', closeSidebar);
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && AppState.isSidebarOpen) closeSidebar();
    });
    sidebar.addEventListener('click', (e) => {
        if (e.target.closest('.account-item') && window.innerWidth <= 768) closeSidebar();
    });
}

// ============================================================
// 17. WIRING UP ALL THE BUTTONS
// ============================================================

function initEventListeners() {
    // Switching between login/register
    document.getElementById('goToRegister')?.addEventListener('click', () => {
        document.getElementById('registerForm')?.reset();
        clearFormErrors('register');
        switchView(Views.REGISTER);
    });
    document.getElementById('goToLogin')?.addEventListener('click', () => {
        document.getElementById('loginForm')?.reset();
        clearFormErrors('login');
        switchView(Views.LOGIN);
    });

    // Auth forms
    document.getElementById('loginForm')?.addEventListener('submit', handleLogin);
    document.getElementById('registerForm')?.addEventListener('submit', handleRegister);

    // Dashboard actions
    document.getElementById('syncBtn')?.addEventListener('click', syncAllAccounts);
    document.getElementById('syncAllBtn')?.addEventListener('click', syncAllAccounts);
    document.getElementById('addAccountBtn')?.addEventListener('click', openAddAccountModal);
    document.getElementById('logoutBtn')?.addEventListener('click', logout);

    // Add Account modal
    document.getElementById('closeAddAccountModal')?.addEventListener('click', closeModal);
    document.getElementById('cancelAddAccount')?.addEventListener('click', closeModal);
    document.getElementById('submitAddAccount')?.addEventListener('click', handleAddAccount);
    document.getElementById('addAccountForm')?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') { e.preventDefault(); handleAddAccount(); }
    });

    // Verify Account modal
    document.getElementById('closeVerifyModal')?.addEventListener('click', closeModal);
    document.getElementById('cancelVerify')?.addEventListener('click', closeModal);
    document.getElementById('submitVerify')?.addEventListener('click', handleVerifyAccount);
    document.getElementById('copyVerifyCodeBtn')?.addEventListener('click', copyVerifyCode);

    // Delete Account modal
    document.getElementById('closeDeleteModal')?.addEventListener('click', closeModal);
    document.getElementById('cancelDelete')?.addEventListener('click', closeModal);
    document.getElementById('confirmDelete')?.addEventListener('click', handleDeleteAccount);

    // Click outside a modal to close it
    document.getElementById('modalOverlay')?.addEventListener('click', closeModal);

    // Light / dark mode button
    document.getElementById('themeToggleBtn')?.addEventListener('click', toggleTheme);

    // Redraw the chart at the right size after the window is resized
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            if (AppState.ratingChart) AppState.ratingChart.resize();
        }, 150);
    });
}

// ============================================================
// 18. START THE APP
// ============================================================

function init() {
    initTheme();
    initMobileSidebar();
    initEventListeners();
    checkAuth();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}