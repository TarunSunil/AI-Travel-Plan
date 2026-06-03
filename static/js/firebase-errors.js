export function getErrorMessage(errorCode) {
  const errorMessages = {
    // Login / generic
    "auth/user-not-found": "No account found with this email address.",
    "auth/wrong-password": "Incorrect password. Please try again.",
    "auth/invalid-email": "Please enter a valid email address.",
    "auth/user-disabled": "This account has been disabled.",
    "auth/too-many-requests": "Too many failed attempts. Please try again later.",
    "auth/network-request-failed": "Network error. Please check your connection.",
    "auth/popup-closed-by-user": "Sign-in was cancelled.",
    "auth/cancelled-popup-request": "Only one popup request is allowed at a time.",
    "auth/popup-blocked": "Popup was blocked by the browser.",

    // Signup-specific
    "auth/email-already-in-use": "An account with this email already exists.",
    "auth/operation-not-allowed": "Account creation is currently disabled.",
    "auth/weak-password": "Password is too weak. Please choose a stronger password.",
    "auth/unauthorized-domain": "This domain is not authorized for Firebase Auth. Please add localhost:5000 to authorized domains in Firebase Console.",
    "auth/invalid-api-key": "Invalid Firebase API key. Please check your Firebase configuration.",
    "auth/app-not-authorized": "This app is not authorized to use Firebase Authentication.",
    "auth/quota-exceeded": "Quota exceeded. Please try again later.",

    default: "An error occurred. Please try again.",
  };

  return errorMessages[errorCode] || errorMessages.default;
}

