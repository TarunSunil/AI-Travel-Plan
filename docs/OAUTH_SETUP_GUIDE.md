# OAuth Authentication Setup Guide

## Issues Fixed

1. ✅ **authDomain Configuration** - Changed from `localhost` to production `ai-tp-a98af.firebaseapp.com` (required for OAuth)
2. ✅ **Popup/Redirect Fallback** - Added automatic redirect method if popup is blocked
3. ✅ **Better Error Handling** - Suppressed "popup-closed-by-user" errors (user intentionally closed)
4. ✅ **OAuth Scopes** - Added proper scopes for Google and GitHub providers

## Firebase Console Setup Required

### 1. Add Authorized Domains
Go to Firebase Console → Authentication → Settings → Authorized domains

Add these domains:
- `localhost` (for local development)
- `127.0.0.1` (alternative localhost)
- Your production domain (e.g., `ai-tp-a98af.web.app`)

### 2. Enable OAuth Providers
Go to Firebase Console → Authentication → Sign-in method

Enable:
- ✅ **Google** (should be enabled by default)
- ✅ **GitHub** - You'll need to:
  1. Create a GitHub OAuth App at https://github.com/settings/developers
  2. Set Authorization callback URL to: `https://ai-tp-a98af.firebaseapp.com/__/auth/handler`
  3. Copy Client ID and Client Secret to Firebase

### 3. GitHub OAuth App Setup
1. Go to: https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in:
   - **Application name**: AI Travel Planner
   - **Homepage URL**: `http://localhost:5000` (or your domain)
   - **Authorization callback URL**: `https://ai-tp-a98af.firebaseapp.com/__/auth/handler`
4. Click "Register application"
5. Copy the **Client ID**
6. Generate a **Client Secret**
7. Paste both into Firebase Console → Authentication → Sign-in method → GitHub

## Common Issues & Solutions

### ERR_BLOCKED_BY_CLIENT
**Cause**: Ad blocker or browser extension blocking OAuth scripts

**Solutions**:
1. Disable ad blockers (uBlock Origin, Adblock Plus, etc.)
2. Whitelist Firebase domains:
   - `*.firebaseapp.com`
   - `*.googleapis.com`
   - `*.gstatic.com`
3. Test in incognito mode (extensions disabled)

### auth/popup-closed-by-user
**Cause**: User closed the popup before completing sign-in

**Solution**: This is now handled gracefully - no error shown to user

### auth/popup-blocked
**Cause**: Browser blocked the popup window

**Solution**: The code now automatically falls back to redirect method

### auth/unauthorized-domain
**Cause**: Current domain not in Firebase authorized domains list

**Solution**: Add your domain in Firebase Console (see step 1 above)

## Testing OAuth

1. Clear browser cache and cookies
2. Disable all ad blockers
3. Test in this order:
   - ✅ Email/Password sign-up (should work immediately)
   - ✅ Google sign-in (requires Google provider enabled)
   - ✅ GitHub sign-in (requires GitHub OAuth app setup)

## How It Works

### Popup Method (Primary)
1. Click "Google" or "GitHub" button
2. Popup window opens with provider's login page
3. User authenticates
4. Popup closes, user logged in

### Redirect Method (Fallback)
1. If popup is blocked/fails, automatically switches to redirect
2. User is redirected to provider's login page
3. After authentication, redirected back to your app
4. `getRedirectResult()` captures the result and logs user in

## Developer Notes

- Both `login.js` and `signup.js` now have identical OAuth logic
- `firebase-config.js` uses production authDomain (required for OAuth)
- Popup method tried first, redirect used as fallback
- All OAuth errors properly logged to console for debugging
