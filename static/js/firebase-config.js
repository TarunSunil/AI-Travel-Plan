// Firebase Configuration using CDN imports
import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js';
import { getAuth, setPersistence, browserLocalPersistence } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';
import { getFirestore } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js';

// Firebase config - Must use production authDomain for OAuth (Google/GitHub)
// localhost must be added as authorized domain in Firebase Console
const firebaseConfig = window.FIREBASE_CONFIG;

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase services
export const auth = getAuth(app);
export const db = getFirestore(app);

// Set persistence
setPersistence(auth, browserLocalPersistence);
