import { auth, db } from './firebase-config.js';
import { 
    signInWithEmailAndPassword, 
    GoogleAuthProvider, 
    GithubAuthProvider, 
    signInWithPopup,
    sendPasswordResetEmail 
} from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';
import { doc, setDoc, getDoc } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js';

// Initialize providers
const googleProvider = new GoogleAuthProvider();
const githubProvider = new GithubAuthProvider();

// Form elements
const loginForm = document.getElementById('loginForm');
const errorMessage = document.getElementById('errorMessage');

// Login form submission
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    console.log('Login attempt:', { email }); // Debug log
    
    try {
        showLoading(true);
        console.log('Attempting Firebase sign-in...'); // Debug log
        
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
        
        console.log('Login successful:', user.email); // Debug log
        
        // Store user session
        localStorage.setItem('userToken', await user.getIdToken());
        localStorage.setItem('userId', user.uid);
        
        // Redirect to main app
        window.location.href = '/';
        
    } catch (error) {
        console.error('Login error:', error); // Detailed error log
        console.error('Error code:', error.code);
        console.error('Error message:', error.message);
        showError(getErrorMessage(error.code));
    } finally {
        showLoading(false);
    }
});

// Google Sign In
window.signInWithGoogle = async () => {
    try {
        console.log('Attempting Google sign-in...'); // Debug log
        showLoading(true);
        const result = await signInWithPopup(auth, googleProvider);
        const user = result.user;
        
        console.log('Google sign-in successful:', user.email); // Debug log
        
        // Save user to Firestore
        await saveUserToFirestore(user);
        
        // Store session
        localStorage.setItem('userToken', await user.getIdToken());
        localStorage.setItem('userId', user.uid);
        
        window.location.href = '/';
        
    } catch (error) {
        console.error('Google sign-in error:', error); // Detailed error log
        console.error('Error code:', error.code);
        console.error('Error message:', error.message);
        showError(getErrorMessage(error.code));
    } finally {
        showLoading(false);
    }
};

// GitHub Sign In
window.signInWithGithub = async () => {
    try {
        console.log('Attempting GitHub sign-in...'); // Debug log
        showLoading(true);
        const result = await signInWithPopup(auth, githubProvider);
        const user = result.user;
        
        console.log('GitHub sign-in successful:', user.email); // Debug log
        
        await saveUserToFirestore(user);
        
        localStorage.setItem('userToken', await user.getIdToken());
        localStorage.setItem('userId', user.uid);
        
        window.location.href = '/';
        
    } catch (error) {
        console.error('GitHub sign-in error:', error); // Detailed error log
        console.error('Error code:', error.code);
        console.error('Error message:', error.message);
        showError(getErrorMessage(error.code));
    } finally {
        showLoading(false);
    }
};

// Save user to Firestore
async function saveUserToFirestore(user) {
    const userRef = doc(db, 'users', user.uid);
    const userSnap = await getDoc(userRef);
    
    try {
        if (!userSnap.exists()) {
            await setDoc(userRef, {
                uid: user.uid,
                email: user.email,
                displayName: user.displayName || '',
                photoURL: user.photoURL || '',
                createdAt: new Date().toISOString(),
                lastLogin: new Date().toISOString(),
                provider: user.providerData[0]?.providerId || 'email'
            });
        } else {
            await setDoc(userRef, {
                lastLogin: new Date().toISOString()
            }, { merge: true });
        }
        console.log('User data saved to Firestore'); // Debug log
    } catch (firestoreError) {
        console.warn('Firestore save failed (this is OK for now):', firestoreError);
        // Continue even if Firestore fails - user is still authenticated
    }
}

// Toggle password visibility
window.togglePassword = (fieldId) => {
    const field = document.getElementById(fieldId);
    if (!field) {
        console.error('Password field not found:', fieldId);
        return;
    }
    
    const icon = field.nextElementSibling?.nextElementSibling?.querySelector('i');
    if (!icon) {
        console.error('Password toggle icon not found for field:', fieldId);
        return;
    }
    
    if (field.type === 'password') {
        field.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        field.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    }
};

// Utility functions
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('show');
    setTimeout(() => {
        errorMessage.classList.remove('show');
    }, 5000);
}

function showLoading(loading) {
    const loginBtn = document.querySelector('.login-btn');
    if (loading) {
        loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Signing in...</span>';
        loginBtn.disabled = true;
    } else {
        loginBtn.innerHTML = '<span>Sign In</span> <i class="fas fa-arrow-right"></i>';
        loginBtn.disabled = false;
    }
}

function getErrorMessage(errorCode) {
    const errorMessages = {
        'auth/user-not-found': 'No account found with this email address.',
        'auth/wrong-password': 'Incorrect password. Please try again.',
        'auth/invalid-email': 'Please enter a valid email address.',
        'auth/user-disabled': 'This account has been disabled.',
        'auth/too-many-requests': 'Too many failed attempts. Please try again later.',
        'auth/network-request-failed': 'Network error. Please check your connection.',
        'auth/popup-closed-by-user': 'Sign-in was cancelled.',
        'auth/cancelled-popup-request': 'Only one popup request is allowed at a time.',
        'auth/popup-blocked': 'Popup was blocked by the browser.',
        'default': 'An error occurred during sign-in. Please try again.'
    };
    
    return errorMessages[errorCode] || errorMessages['default'];
}

// Forgot password functionality
document.addEventListener('click', async (e) => {
    if (e.target.classList.contains('forgot-password')) {
        e.preventDefault();
        const email = document.getElementById('email').value;
        
        if (!email) {
            showError('Please enter your email address first.');
            return;
        }
        
        try {
            await sendPasswordResetEmail(auth, email);
            showError('Password reset email sent! Check your inbox.');
        } catch (error) {
            showError(getErrorMessage(error.code));
        }
    }
});