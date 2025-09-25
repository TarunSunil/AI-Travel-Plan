# AI Travel Planner

**AI Travel Planner** is an intelligent and modern travel planning application that combines flight and hotel search with AI-powered assistance. Built with **Flask**, **MySQL**, and **Google's Gemini AI**, it helps users plan trips efficiently with real-time pricing and personalized recommendations—all in a clean, responsive web app.


Try the deployed application here:  
[https://travel-planner-git-main-tarunsunils-projects.vercel.app](https://travel-planner-git-main-tarunsunils-projects.vercel.app)


- **Flight Search**: Find available flights between major cities with real-time pricing
- **Hotel Search**: Discover accommodations within your budget at your destination
- **AI Travel Assistant**: Get personalized travel advice using Google's Gemini AI
- **Budget Planning**: Set daily budgets and find options that fit your financial plan
- **Interactive Chat**: Ask questions about destinations, activities, and travel tips
- **Smart Pricing**: Minimum price tracking for flights and hotels
- **Date Range Planning**: Plan trips with flexible dates
- **Multi-City Support**: Browse options across 10+ major international cities
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-travel-planner.git
cd ai-travel-planner
```

### 2. Set Up Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy and edit the example environment configuration:

```bash
cp env.example .env
```

Edit the `.env` file with your configuration details:

```env
# Database Configuration
DB_HOST=localhost
DB_NAME=travel_planner
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_PORT=3306

# API Keys
GEMINI_API_KEY=your_gemini_api_key
```

### 5. Set Up the Database

```bash
python database.py
```

### 6. Run the Application

```bash
python main.py
```

### 7. Open the App

Visit `http://localhost:5000` in your browser.

## 🛠️ Technology Stack

| Component       | Version / Service     |
|-----------------|----------------------|
| Backend         | Flask 3.0.0          |
| Database        | MySQL 8.2.0          |
| AI Integration  | Google Gemini 2.0 Flash |
| Frontend        | HTML5, CSS3, JavaScript|
| Deployment      | Vercel-ready         |
| Config Management | python-dotenv       |

## 📊 Database Schema

The application uses three main tables:

- **Flights Table**: `id`, origin, destination, price, date, airline
- **Hotels Table**: `id`, name, location, price per night, rating
- **Min Prices Table**: origin, destination, minimum flight price, minimum hotel price

## 🌍 Supported Cities

Travel planner currently supports:

- New York 🇺🇸
- London 🇬🇧
- Paris 🇫🇷
- Tokyo 🇯🇵
- Sydney 🇦🇺
- Dubai 🇦🇪
- Singapore 🇸🇬
- San Francisco 🇺🇸
- Mumbai 🇮🇳
- Delhi 🇮🇳

## 🎮 Usage

1. **Trip Planning**
   - Select your departure and destination cities
   - Set your daily budget and travel dates
   - Click "Search" to find flights and hotels

2. **AI Travel Assistant Chat**
   - Use the chat to ask questions like:  
     - "What are the best attractions in Paris?"  
     - "Tell me about the weather in Tokyo"  
     - "What should I pack for Dubai?"  
     - "Find budget-friendly restaurants in Singapore"

3. **Sample Queries**
   - Flight info: "What flights are available to London?"
   - Hotel recommendations: "What hotels in New York?"
   - Travel advice: "What's the best time to visit Tokyo?"
   - Itinerary planning: "Create a 3-day itinerary for Paris"

## 🚀 Deployment

### Vercel Deployment

1. Connect your GitHub repository to Vercel
2. Set environment variables in the Vercel dashboard
3. Deploy automatically on push to the main branch

### Other Platforms

Can also deploy to:
- Heroku
- Railway
- DigitalOcean App Platform
- AWS Elastic Beanstalk

## 📁 Project Structure

```
ai-travel-planner/
├── main.py             # Flask application entry point
├── database.py         # Database setup and sample data
├── requirements.txt    # Python dependencies
├── env.example         # Environment variables template
├── vercel.json         # Vercel deployment configuration
├── templates/
│   └── index.html      # Main application interface
├── static/
│   ├── styles.css      # Application styling
│   ├── app.js          # Frontend JavaScript
│   └── images/         # Application images
└── README.md           # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini AI for intelligent travel assistance
- Flask community for the web framework
- MySQL for the database management
- Vercel for the deployment platform

## 📞 Support

- Check the [Issues](https://github.com/yourusername/ai-travel-planner/issues) page
- Create a new issue with a detailed description
- Contact the maintainers

**Happy Traveling! ✈️🌍**

_Built with ❤️ for travelers worldwide_