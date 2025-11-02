---
title: Authentication System Testing Guide
category: guides
tags: [authentication, testing, qa]
last_updated: 2025-11-02
---

# Authentication System Testing Guide

Deze guide beschrijft alle test scenarios voor het authentication systeem van de Digital Resupplying Tool.

## Inhoudsopgave
- [Test Credentials](#test-credentials)
- [Login Flow Tests](#login-flow-tests)
- [Logout Flow Tests](#logout-flow-tests)
- [Session Management Tests](#session-management-tests)
- [Role-Based Access Tests](#role-based-access-tests)
- [Error Handling Tests](#error-handling-tests)

---

## Test Credentials

### Development Test Users

**Admin User:**
- Username: `admin`
- Password: `Admin123!`
- Role: Administrator
- Access: Alle features (Genereren, Voorstellen, Instellingen)

**Regular User:**
- Username: `user`
- Password: `User123!`
- Role: User
- Access: Standaard features (Genereren, Voorstellen)

**Store User:**
- Username: `store`
- Password: `Store123!`
- Role: Store
- Access: Alleen Opdrachten (geen Genereren/Voorstellen)

---

## Login Flow Tests

### TC-AUTH-001: Successful Login (Remember Me OFF)
**Steps:**
1. Navigate to `http://localhost:3000/login`
2. Enter valid credentials (admin/Admin123!)
3. **Do NOT** check "Onthoud mij" checkbox
4. Click "Inloggen"

**Expected Results:**
- ✅ Success toast: "Inloggen geslaagd!"
- ✅ Redirect to dashboard
- ✅ User info visible in sidebar (avatar + name)
- ✅ Token stored in **sessionStorage** (not localStorage)
- ✅ Session expires when browser closes

**Verification:**
- Open DevTools > Application > Session Storage
- Check for `access_token` and `refresh_token`
- Close browser and reopen → should require login

---

### TC-AUTH-002: Successful Login (Remember Me ON)
**Steps:**
1. Navigate to `http://localhost:3000/login`
2. Enter valid credentials (admin/Admin123!)
3. **Check** "Onthoud mij (30 dagen)" checkbox
4. Click "Inloggen"

**Expected Results:**
- ✅ Success toast: "Inloggen geslaagd!"
- ✅ Redirect to dashboard
- ✅ User info visible in sidebar
- ✅ Token stored in **localStorage** (persists)
- ✅ Session persists after browser close

**Verification:**
- Open DevTools > Application > Local Storage
- Check for `access_token` and `refresh_token`
- Close browser and reopen → should auto-login

---

### TC-AUTH-003: Invalid Credentials
**Steps:**
1. Navigate to login page
2. Enter invalid credentials (admin/wrongpassword)
3. Click "Inloggen"

**Expected Results:**
- ✅ Error toast: "Inloggen mislukt"
- ✅ Inline error message displayed
- ✅ User stays on login page
- ✅ No tokens stored
- ✅ Form fields remain enabled

---

### TC-AUTH-004: Empty Fields Validation
**Steps:**
1. Navigate to login page
2. Leave username/password empty
3. Click "Inloggen"

**Expected Results:**
- ✅ Inline error: "Gebruikersnaam is verplicht" (if username empty)
- ✅ Inline error: "Wachtwoord is verplicht" (if password empty)
- ✅ No API call made
- ✅ User stays on login page

---

### TC-AUTH-005: Auto-Redirect When Already Logged In
**Steps:**
1. Login successfully (any user)
2. Manually navigate to `/login`

**Expected Results:**
- ✅ Immediately redirected to dashboard
- ✅ No login form visible
- ✅ User remains authenticated

---

## Logout Flow Tests

### TC-AUTH-010: Manual Logout
**Steps:**
1. Login as any user
2. Verify you're on dashboard with sidebar visible
3. Click "Uitloggen" button in sidebar footer

**Expected Results:**
- ✅ Tokens cleared from storage
- ✅ Redirect to `/login`
- ✅ Sidebar no longer visible
- ✅ Cannot navigate back to protected routes

**Verification:**
- Check DevTools > Application > Storage
- All auth tokens should be cleared
- Try navigating to `/` → should redirect to login

---

### TC-AUTH-011: Logout with Return URL
**Steps:**
1. Login successfully
2. Navigate to `/proposals`
3. Click "Uitloggen"
4. After redirect, login again

**Expected Results:**
- ✅ Logout succeeds
- ✅ Redirect to `/login`
- ✅ On re-login, redirect to dashboard (not `/proposals`)

---

## Session Management Tests

### TC-AUTH-020: Auto Token Refresh
**Steps:**
1. Login successfully
2. Open DevTools > Console
3. Wait 10+ minutes (or modify refresh interval to 1 min for testing)

**Expected Results:**
- ✅ Console log: "Refreshing token..." (every 10 min)
- ✅ New `access_token` in storage
- ✅ Session stays active
- ✅ No user interruption

**Note:** For faster testing, temporarily modify refresh interval in `auth-context.tsx`.

---

### TC-AUTH-021: Session Expiry Detection (401)
**Steps:**
1. Login successfully
2. Open DevTools > Application > Storage
3. Manually delete `access_token` and `refresh_token`
4. Try to navigate or perform any action that calls API

**Expected Results:**
- ✅ 401 error detected
- ✅ Session Expired modal appears
- ✅ 10-second countdown starts
- ✅ Auto-redirect to login after countdown
- ✅ Or click "Nu Inloggen" for immediate redirect

---

### TC-AUTH-022: Session Expired Modal
**Steps:**
1. Trigger session expiry (delete tokens or wait for expiry)
2. Observe modal behavior

**Expected Results:**
- ✅ Modal shows: "Sessie Verlopen"
- ✅ Countdown from 10 to 0
- ✅ "Nu Inloggen" button active
- ✅ Auto-redirect at 0 seconds
- ✅ Cannot interact with page behind modal

---

## Role-Based Access Tests

### TC-AUTH-030: Admin Role Navigation
**Steps:**
1. Login as admin (admin/Admin123!)
2. Check visible menu items in sidebar

**Expected Results:**
- ✅ Dashboard visible
- ✅ Genereren visible
- ✅ Herverdelingsvoorstellen visible
- ✅ Instellingen visible
- ✅ NO "Opdrachten" menu item

---

### TC-AUTH-031: Store Role Navigation
**Steps:**
1. Login as store user (store/Store123!)
2. Check visible menu items in sidebar

**Expected Results:**
- ✅ Dashboard visible
- ✅ Opdrachten visible
- ✅ Instellingen visible
- ✅ NO "Genereren" menu item
- ✅ NO "Herverdelingsvoorstellen" menu item

---

### TC-AUTH-032: Regular User Role Navigation
**Steps:**
1. Login as regular user (user/User123!)
2. Check visible menu items

**Expected Results:**
- ✅ Dashboard visible
- ✅ Genereren visible
- ✅ Herverdelingsvoorstellen visible
- ✅ Instellingen visible
- ✅ NO "Opdrachten" menu item

---

## Error Handling Tests

### TC-AUTH-040: Network Error on Login
**Steps:**
1. Stop backend server (Ctrl+C in terminal)
2. Try to login
3. Restart server

**Expected Results:**
- ✅ Error toast: "Failed to fetch" or connection error
- ✅ Inline error message
- ✅ Form remains functional
- ✅ Can retry after server restart

---

### TC-AUTH-041: CORS Error (localhost vs 127.0.0.1)
**Steps:**
1. Access app via `http://127.0.0.1:3000/login`
2. Try to login

**Expected Results:**
- ✅ Should work (both origins supported)
- ✅ Login succeeds normally
- ✅ No CORS errors in console

**Note:** Both `localhost:3000` and `127.0.0.1:3000` zijn toegestaan in CORS config.

---

### TC-AUTH-042: Multiple Login Attempts
**Steps:**
1. Try 3x login with wrong password
2. Try login with correct credentials

**Expected Results:**
- ✅ Each failed attempt shows error
- ✅ No account lockout (not implemented)
- ✅ Successful login works after failed attempts
- ✅ No rate limiting (future feature)

---

## Visual/UX Tests

### TC-AUTH-050: Loading States
**Steps:**
1. Login with valid credentials
2. Observe UI during authentication

**Expected Results:**
- ✅ Login button shows spinner + "Inloggen..."
- ✅ Form fields disabled during processing
- ✅ No double-submit possible
- ✅ Loading state clears after response

---

### TC-AUTH-051: Password Visibility Toggle
**Steps:**
1. Enter password
2. Click eye icon to toggle visibility

**Expected Results:**
- ✅ Password initially hidden (••••)
- ✅ Click eye → password visible
- ✅ Click eye-off → password hidden again
- ✅ Toggle works while typing

---

### TC-AUTH-052: Toast Notifications
**Steps:**
1. Login successfully
2. Try invalid login
3. Observe toast notifications

**Expected Results:**
- ✅ Success toast appears on successful login
- ✅ Error toast appears on failed login
- ✅ Toasts auto-dismiss after 5 seconds
- ✅ Multiple toasts stack properly

---

## Regression Tests

### TC-AUTH-060: Protected Route Access
**Steps:**
1. Logout (clear all tokens)
2. Try to access `http://localhost:3000/proposals` directly

**Expected Results:**
- ✅ Redirect to `/login?returnUrl=/proposals`
- ✅ Cannot access protected content
- ✅ After login, redirect to requested page

---

### TC-AUTH-061: Token Persistence Check
**Steps:**
1. Login with Remember Me
2. Check localStorage
3. Refresh page
4. Check if still logged in

**Expected Results:**
- ✅ Tokens persists in localStorage
- ✅ Auto-login on page refresh
- ✅ No re-authentication needed
- ✅ User data loaded from storage

---

## Test Summary Checklist

### Must-Pass Tests (Critical)
- [ ] TC-AUTH-001: Login with Remember Me OFF
- [ ] TC-AUTH-002: Login with Remember Me ON
- [ ] TC-AUTH-003: Invalid credentials handling
- [ ] TC-AUTH-010: Manual logout
- [ ] TC-AUTH-020: Auto token refresh
- [ ] TC-AUTH-021: Session expiry detection
- [ ] TC-AUTH-030: Admin role navigation
- [ ] TC-AUTH-031: Store role navigation
- [ ] TC-AUTH-060: Protected route access

### Should-Pass Tests (Important)
- [ ] TC-AUTH-004: Empty fields validation
- [ ] TC-AUTH-005: Auto-redirect when logged in
- [ ] TC-AUTH-022: Session expired modal
- [ ] TC-AUTH-040: Network error handling
- [ ] TC-AUTH-050: Loading states
- [ ] TC-AUTH-052: Toast notifications

### Nice-to-Have Tests (Polish)
- [ ] TC-AUTH-051: Password visibility toggle
- [ ] TC-AUTH-042: Multiple login attempts
- [ ] TC-AUTH-061: Token persistence

---

## Testing Best Practices

### Before Testing
1. ✅ Ensure backend is running (`.\dev.ps1`)
2. ✅ Database is seeded with test users
3. ✅ Clear browser cache and storage
4. ✅ Use incognito/private window for clean state

### During Testing
1. ✅ Open DevTools (F12) before starting
2. ✅ Monitor Console tab for errors
3. ✅ Check Network tab for API calls
4. ✅ Verify Application > Storage tabs
5. ✅ Take screenshots of failures

### Reporting Issues
When filing a bug, include:
- Test case number (e.g., TC-AUTH-003)
- Steps to reproduce
- Expected vs actual behavior
- Screenshots of error messages
- Console logs (if applicable)
- Browser version and OS

---

## Automated Testing (Future)

Currently all tests are manual. Future improvements:
- [ ] Playwright E2E tests for login flows
- [ ] Jest unit tests for auth utilities
- [ ] Cypress component tests
- [ ] API integration tests with pytest

---

## Related Documentation
- [Authentication Flow Implementation](../todo/authentication-flow-implementation.md)
- [Quick Start Guide](../getting-started/quick-start.md)
- [Troubleshooting Guide](../getting-started/troubleshooting.md)
