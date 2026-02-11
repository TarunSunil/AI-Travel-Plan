// Firebase Configuration using CDN imports
import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js';
import { getAuth, setPersistence, browserLocalPersistence } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';
import { getFirestore } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js';

// Firebase config - Must use production authDomain for OAuth (Google/GitHub)
// localhost must be added as authorized domain in Firebase Console
const firebaseConfig = {
    apiKey: "AIzaSyDTvRaoloxFZNxsEMAW8_RWgfam2ECeT30",
    authDomain: "ai-tp-a98af.firebaseapp.com", // Production domain required for OAuth
    projectId: "ai-tp-a98af",
    storageBucket: "ai-tp-a98af.appspot.com",
    messagingSenderId: "578943308642",
    appId: "1:578943308642:web:4eb27a2aef42a2486d923b"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase services
export const auth = getAuth(app);
export const db = getFirestore(app);

// Set persistence
setPersistence(auth, browserLocalPersistence);