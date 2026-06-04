# AI Travel Planner 🌍✈️

**AI Travel Planner** is an intelligent and modern travel planning application that combines flight and hotel search with AI-powered assistance. Built with **Flask**, **Firebase Authentication**, and **Google's Gemini AI**, it helps users plan trips efficiently with real-time pricing and personalized recommendations.

> 🎉 **Recently Enhanced**: Comprehensive security fixes, performance improvements, testing infrastructure, and cloud database support added!

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

### 🆕 New Security & Performance Features

- ✅ **XSS Protection**: Full sanitization of user and API data
- ✅ **Input Validation**: Server-side validation for all inputs
- ✅ **Rate Limiting**: API abuse prevention (10-30 req/min per endpoint)
- ✅ **Optimized API Calls**: 40% reduction in external API requests
- ✅ **Testing Infrastructure**: Comprehensive pytest test suite
- ✅ **Cloud Database Support**: Optional Supabase PostgreSQL migration
- ✅ **Production Ready**: Secure session management and error handling

## 🚀 Live Demo

[Visit the deployed application](ai-travel-planner-seven-flax.vercel.app)

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Flask 3.0.0 |
| Database | SQLite (default) / PostgreSQL (Supabase) |
| Authentication | Firebase Auth |
| AI Integration | Google Gemini AI |
| API Integration | Amadeus Travel API |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Testing | pytest, pytest-flask |
| Security | Flask-Limiter, Input Validation |
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
- Node.js & pnpm (for frontend dependencies)
- Firebase Project (for authentication)
- Amadeus API credentials
- Google Gemini API key
- (Optional) Supabase account for cloud database

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

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Install frontend dependencies**
```bash
pnpm install
```

5. **Configure environment variables**
```bash
cp sample.env .env
```

Edit the `.env` file with your credentials:
```env
# API Keys
AMADEUS_CLIENT_ID=your_amadeus_client_id
AMADEUS_CLIENT_SECRET=your_amadeus_client_secret
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=generate_with_python_secrets_token_hex

# Firebase Configuration
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id

# Optional: Supabase PostgreSQL (see docs/SUPABASE_MIGRATION.md)
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_KEY=your_anon_public_key
# DATABASE_URL=postgresql://postgres:password@host:5432/postgres
```

**Generate SECRET_KEY**:
```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

6. **Initialize the database**
```bash
python database.py
```

7. **Run the application**
```bash
python main.py
```

8. **Open your browser**
Visit `http://localhost:5000`

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_validation.py

# Run with coverage
pytest --cov=. --cov-report=html
```

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
travel-planner/
├── main.py                  # Flask application entry point
├── database.py              # SQLite database module
├── supabase_db.py          # Supabase PostgreSQL module (optional)
├── validation.py            # Input validation utilities
├── amadeus_api.py           # Amadeus API integration
├── city_data.py             # City and airport data
├── requirements.txt         # Python dependencies
├── package.json             # Frontend dependencies
├── pytest.ini              # Pytest configuration
├── .env                     # Environment variables (not in repo)
├── sample.env               # Environment template
├── vercel.json             # Vercel deployment config
├── IMPLEMENTATION_SUMMARY.md # Recent improvements summary
├── README.md                # This file
├── templates/
│   ├── base.html           # Base template
│   ├── index.html          # Main application interface
│   ├── login.html          # Login page
│   └── signup.html         # Registration page
├── static/
│   ├── app.js              # Main frontend JavaScript
│   ├── styles.css          # Main styling
│   ├── css/
│   │   └── login.css       # Authentication styling
│   ├── js/
│   │   ├── login.js        # Login functionality
│   │   ├── signup.js       # Registration functionality
│   │   └── firebase-config.js # Firebase configuration
│   └── images/             # Application images
├── tests/
│   ├── conftest.py         # Pytest fixtures
│   ├── test_validation.py  # Validation tests
│   └── test_routes.py      # Route integration tests
├── docs/                    # Documentation folder
│   ├── README.md           # Documentation index
│   ├── SUPABASE_MIGRATION.md # Database migration guide
│   ├── QUICK_START.md      # Quick start guide
│   ├── SOLUTIONS.md        # Troubleshooting guide
│   └── ... (15+ more docs) # API docs, setup guides
└── tasks/
    └── todo.md             # Development tasks
```

## 🚀 Deployment

### Vercel Deployment
1. Connect your GitHub repository to Vercel
2. Set environment variables in the Vercel dashboard
3. Deploy automatically on push to main branch

### Environment Variables for Production
Make sure to set all environment variables from your `.env` file in your deployment platform.

## 🔒 Security Features

- ✅ **Firebase Authentication**: Enterprise-grade security with multi-provider support
- ✅ **XSS Protection**: HTML sanitization for all user and API data
- ✅ **Input Validation**: Comprehensive server-side validation for all inputs
- ✅ **Rate Limiting**: API abuse prevention (10-30 req/min per endpoint)
- ✅ **Secure Session Management**: Proper SECRET_KEY configuration required
- ✅ **SQL Injection Prevention**: Parameterized queries throughout
- ✅ **HTTPS**: Secure connections in production
- ✅ **Environment Variables**: All sensitive data in environment variables

## 📚 Documentation

All documentation is organized in the `docs/` folder:

- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Recent improvements and enhancements
- **[docs/SUPABASE_MIGRATION.md](docs/SUPABASE_MIGRATION.md)** - Database migration to PostgreSQL
- **[docs/QUICK_START.md](docs/QUICK_START.md)** - Quick start guide
- **[docs/SOLUTIONS.md](docs/SOLUTIONS.md)** - Troubleshooting guide
- **[docs/README.md](docs/README.md)** - Full documentation index

## 🐛 Known Issues & Solutions

For detailed troubleshooting, see [docs/SOLUTIONS.md](docs/SOLUTIONS.md). Quick fixes:

- **Firebase Auth Domain**: Add your deployment domain to Firebase authorized domains
- **API Rate Limits**: Rate limiting now active (10 req/min for search endpoints)
- **Gemini API Key**: Generate new key at [Google AI Studio](https://makersuite.google.com/app/apikey)
- **SECRET_KEY Error**: Generate with `python -c 'import secrets; print(secrets.token_hex(32))'`

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
- [ ] Advanced itinerary planning with maps
- [ ] Expense tracking throughout trip
- [ ] Social trip sharing features
- [ ] Multi-language support
- [ ] CSRF protection for forms
- [ ] Redis caching layer
- [ ] Mobile app (React Native/Flutter)
- [ ] Email notifications for bookings

### ✅ Recently Completed
- ✅ XSS protection and input validation
- ✅ Rate limiting for API endpoints
- ✅ Testing infrastructure (pytest)
- ✅ Cloud database support (Supabase)
- ✅ Performance optimizations (40% fewer API calls)
- ✅ Comprehensive documentation

---

**Happy Traveling! ✈️🌍**

*Built with ❤️ for travelers worldwide*

> **Recent Update (Jan 2026)**: Major security and performance enhancements completed! See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for details.
