# AI Travel Planner 🌍✈️

**AI Travel Planner** is an intelligent and modern travel planning application that combines flight and hotel search with AI-powered assistance. Built with **Flask**, **Firebase Authentication**, and **Google's Gemini AI**, it helps users plan trips efficiently with real-time pricing and personalized recommendations.

## 🌟 Features

- **🔐 Secure Authentication**: Firebase-powered login with email/password, Google, and GitHub
- **✈️ Flight Search**: Find available flights between major cities with real-time pricing via Amadeus API
- **🏨 Hotel Search**: Discover accommodations within your budget at your destination
- **🤖 AI Travel Assistant**: Get personalized travel advice using Google's Gemini AI
- **💰 Budget Planning**: Set daily budgets and find options that fit your financial plan
- **💬 Interactive Chat**: Ask questions about destinations, activities, and travel tips
- **📊 Smart Pricing**: Minimum price tracking for flights and hotels
- **📅 Date Range Planning**: Plan trips with flexible dates
- **🌐 Multi-City Support**: Browse options across 10+ major international cities
- **📱 Responsive Design**: Works seamlessly on desktop and mobile devices

## 🚀 Live Demo

[Visit the deployed application](https://travel-planner-git-main-tarunsunils-projects.vercel.app)

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Flask 3.0.0 |
| Database | SQLite (Development) |
| Authentication | Firebase Auth |
| AI Integration | Google Gemini AI |
| API Integration | Amadeus Travel API |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Deployment | Vercel |
| Environment | python-dotenv |

## 🌍 Supported Cities

- **Asia**: Tokyo, Singapore, Mumbai, Delhi
- **Europe**: London, Paris
- **Middle East**: Dubai
- **Americas**: New York, San Francisco
- **Oceania**: Sydney

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Firebase Project (for authentication)
- Amadeus API credentials
- Google Gemini API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ai-travel-planner.git
cd ai-travel-planner
```

2. **Set up virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
```

Edit the `.env` file with your credentials:
```env
# API Keys
AMADEUS_CLIENT_ID=your_amadeus_client_id
AMADEUS_CLIENT_SECRET=your_amadeus_client_secret
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_secret_key

# Firebase Configuration
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id
```

5. **Initialize the database**
```bash
python database.py
```

6. **Run the application**
```bash
python main.py
```

7. **Open your browser**
Visit `http://localhost:5000`

## 🔧 Configuration

### Firebase Setup
1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com)
2. Enable Authentication with Email/Password, Google, and GitHub providers
3. Add `localhost`, `127.0.0.1` to authorized domains in Authentication settings
4. Get your Firebase configuration from Project Settings

### API Keys Setup
- **Amadeus API**: Get credentials from [Amadeus for Developers](https://developers.amadeus.com)
- **Gemini AI**: Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## 🎮 Usage

### Trip Planning
1. **Login** with email/password, Google, or GitHub
2. **Select** your departure and destination cities
3. **Set** your daily budget and travel dates
4. **Click** "Search" to find flights and hotels

### AI Travel Assistant
Use the chat to ask questions like:
- "What are the best attractions in Paris?"
- "Tell me about the weather in Tokyo"
- "What should I pack for Dubai?"
- "Find budget-friendly restaurants in Singapore"
- "What flights are available to London?"
- "Create a 3-day itinerary for Paris"

## 📁 Project Structure

```
ai-travel-planner/
├── main.py                 # Flask application entry point
├── database.py             # Database setup and sample data
├── amadeus_api.py          # Amadeus API integration
├── city_data.py            # City and airport data
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in repo)
├── .env.example           # Environment template
├── vercel.json            # Vercel deployment config
├── templates/
│   ├── index.html         # Main application interface
│   ├── login.html         # Login page
│   └── signup.html        # Registration page
├── static/
│   ├── styles.css         # Main styling
│   ├── app.js            # Frontend JavaScript
│   ├── css/
│   │   ├── login.css     # Authentication styling
│   │   └── style.css     # Alternative styles
│   ├── js/
│   │   ├── login.js      # Login functionality
│   │   ├── signup.js     # Registration functionality
│   │   └── firebase-config.js # Firebase configuration
│   └── images/           # Application images
├── tasks/
│   └── todo.md           # Development tasks
└── Changes.txt           # Development changelog
```

## 🚀 Deployment

### Vercel Deployment
1. Connect your GitHub repository to Vercel
2. Set environment variables in the Vercel dashboard
3. Deploy automatically on push to main branch

### Environment Variables for Production
Make sure to set all environment variables from your `.env` file in your deployment platform.

## 🔒 Security Features

- **Firebase Authentication**: Enterprise-grade security
- **Secure Token Management**: JWT tokens handled by Firebase
- **Environment Variables**: All sensitive data in environment variables
- **Input Validation**: Form validation and sanitization
- **HTTPS**: Secure connections in production

## 🐛 Known Issues & Solutions

- **Firebase Auth Domain**: Add your deployment domain to Firebase authorized domains
- **API Rate Limits**: Implement caching for frequently searched routes
- **CORS Issues**: Configure proper CORS headers for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for intelligent travel assistance
- **Amadeus API** for real-time travel data
- **Firebase** for authentication and data storage
- **Flask** community for the web framework
- **Vercel** for deployment platform

## 📞 Support

- Create an issue in the [Issues](https://github.com/yourusername/ai-travel-planner/issues) section
- Check existing issues for solutions
- Contact the maintainers for specific questions

## 🎯 Future Enhancements

- [ ] Real-time flight price alerts
- [ ] Integration with more airlines
- [ ] Advanced itinerary planning
- [ ] Expense tracking
- [ ] Social trip sharing
- [ ] Multi-language support

---

**Happy Traveling! ✈️🌍**

*Built with ❤️ for travelers worldwide*
