import { auth, db } from './firebase-config.js';
import { 
    createUserWithEmailAndPassword, 
    updateProfile,
    GoogleAuthProvider, 
    GithubAuthProvider, 
    signInWithPopup 
} from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';
import { doc, setDoc } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js';

const googleProvider = new GoogleAuthProvider();
const githubProvider = new GithubAuthProvider();

const signupForm = document.getElementById('signupForm');
const errorMessage = document.getElementById('errorMessage');

signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    console.log('Signup attempt:', { email, username }); // Debug log
    
    // Validation
    if (password !== confirmPassword) {
        showError('Passwords do not match.');
        return;
    }
    
    if (password.length < 6) {
        showError('Password must be at least 6 characters long.');
        return;
    }
    
    try {
        showLoading(true);
        console.log('Creating user with Firebase...'); // Debug log
        
        // Create user account
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
        
        console.log('User created successfully:', user.uid); // Debug log
        
        // Update profile with username
        await updateProfile(user, {
            displayName: username
        });
        
        console.log('Profile updated, saving to Firestore...'); // Debug log
        
        // Try to save to Firestore, but don't fail if it doesn't work
        try {
            await setDoc(doc(db, 'users', user.uid), {
                uid: user.uid,
                username: username,
                email: email,
                displayName: username,
                photoURL: '',
                createdAt: new Date().toISOString(),
                lastLogin: new Date().toISOString(),
                provider: 'email'
            });
            console.log('User data saved to Firestore'); // Debug log
        } catch (firestoreError) {
            console.warn('Firestore save failed (this is OK for now):', firestoreError);
            // Continue even if Firestore fails - user is still authenticated
        }
        
        // Store session
        localStorage.setItem('userToken', await user.getIdToken());
        localStorage.setItem('userId', user.uid);
        
        // Redirect to main app
        window.location.href = '/';
        
    } catch (error) {
        console.error('Signup error:', error); // Detailed error log
        console.error('Error code:', error.code); // Error code
        console.error('Error message:', error.message); // Error message
        showError(getErrorMessage(error.code));
    } finally {
        showLoading(false);
    }
});

// Google and GitHub sign-in functions (same as login.js)
window.signInWithGoogle = async () => {
    try {
        console.log('Attempting Google sign-in...'); // Debug log
        showLoading(true);
        const result = await signInWithPopup(auth, googleProvider);
        const user = result.user;
        
        console.log('Google sign-in successful:', user.email); // Debug log
        
        await saveUserToFirestore(user);
        
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

async function saveUserToFirestore(user) {
    try {
        await setDoc(doc(db, 'users', user.uid), {
            uid: user.uid,
            username: user.displayName || user.email.split('@')[0],
            email: user.email,
            displayName: user.displayName || '',
            photoURL: user.photoURL || '',
            createdAt: new Date().toISOString(),
            lastLogin: new Date().toISOString(),
            provider: user.providerData[0]?.providerId || 'email'
        });
        console.log('User data saved to Firestore'); // Debug log
    } catch (firestoreError) {
        console.warn('Firestore save failed (this is OK for now):', firestoreError);
        // Continue even if Firestore fails - user is still authenticated
    }
}

window.togglePassword = (fieldId) => {
    const field = document.getElementById(fieldId);
    if (!field) {
        console.error('Password field not found:', fieldId);
        return;
    }
    
    // Find the toggle button for this field
    const toggleButton = field.parentElement.querySelector('.toggle-password');
    if (!toggleButton) {
        console.error('Toggle button not found for field:', fieldId);
        return;
    }
    
    const icon = toggleButton.querySelector('i');
    if (!icon) {
        console.error('Toggle icon not found for field:', fieldId);
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

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('show');
    setTimeout(() => {
        errorMessage.classList.remove('show');
    }, 5000);
}

function showLoading(loading) {
    const signupBtn = document.querySelector('.login-btn');
    if (loading) {
        signupBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Creating account...</span>';
        signupBtn.disabled = true;
    } else {
        signupBtn.innerHTML = '<span>Create Account</span> <i class="fas fa-arrow-right"></i>';
        signupBtn.disabled = false;
    }
}

function getErrorMessage(errorCode) {
    const errorMessages = {
        'auth/email-already-in-use': 'An account with this email already exists.',
        'auth/invalid-email': 'Please enter a valid email address.',
        'auth/operation-not-allowed': 'Account creation is currently disabled.',
        'auth/weak-password': 'Password is too weak. Please choose a stronger password.',
        'auth/network-request-failed': 'Network error. Please check your connection.',
        'auth/popup-closed-by-user': 'Sign-in popup was closed. Please try again.',
        'auth/popup-blocked': 'Popup was blocked by your browser. Please allow popups for this site.',
        'auth/cancelled-popup-request': 'Only one popup request is allowed at a time.',
        'auth/unauthorized-domain': 'This domain is not authorized for Firebase Auth. Please add localhost:5000 to authorized domains in Firebase Console.',
        'auth/invalid-api-key': 'Invalid Firebase API key. Please check your Firebase configuration.',
        'auth/app-not-authorized': 'This app is not authorized to use Firebase Authentication.',
        'auth/quota-exceeded': 'Quota exceeded. Please try again later.',
        'default': 'An error occurred during account creation. Please try again.'
    };
    
    return errorMessages[errorCode] || errorMessages['default'];
}

/* Password field HTML (for reference)
<input type="password" id="password" name="password" required>
<label for="password">Password</label>
<i class="fas fa-lock input-icon"></i>
<button type="button" class="toggle-password" onclick="togglePassword('password')">
    <i class="fas fa-eye"></i>
</button>
*/