# PALLADIUM

A geospatial news aggregation platform with interactive 3D globe visualization that collects, categorizes, and displays international news articles from major global sources.

<img src="PALLADIUM_DEMO.gif" width="650">


## 🌍 Overview

PALLADIUM is a web-based news aggregation system that automatically scrapes news from five major international sources, applies semantic tagging, stores articles in a cloud database, and presents them through a geospatially-organized 3D globe interface.

### Key Features

- **Automated News Scraping**: Parallel scraping from 5 international news sources
- **Semantic Categorization**: AI-powered keyword-based article tagging
- **Interactive 3D Globe**: WebGL-powered visualization using Three.js
- **Real-time Updates**: Direct database integration with Supabase
- **Multi-region Coverage**: USA, India, Russia, China, and Australia

##  Architecture

PALLADIUM consists of five primary layers:

| Layer | Purpose | Key Components |
|-------|---------|----------------|
| **Data Acquisition** | Scrape news articles from international sources | Selenium WebDriver, country-specific scrapers |
| **Processing** | Categorize and tag article content | ArticleTagger with keyword matching |
| **Storage** | Persist articles in cloud database | Supabase PostgreSQL with country tables |
| **Backend** | Serve application and API endpoints | Django framework with routing |
| **Frontend** | Render 3D globe and user interface | Three.js/Babylon.js with HTML templates |

### Data Flow

```
News Sources → Web Scrapers → ArticleTagger → Supabase Database → Django Backend → 3D Globe Frontend
```

##  Tech Stack

### Backend
- **Framework**: Django (Python 3.x)
- **Database**: Supabase (PostgreSQL BaaS)
- **Web Scraping**: Selenium WebDriver with ChromeDriver
- **Environment**: python-dotenv for configuration

### Frontend
- **3D Rendering**: Three.js v0.160.0 (WebGL)
- **Alternative**: Babylon.js (optional)
- **Language**: JavaScript ES6+
- **Data Access**: @supabase/supabase-js client library

### Core Dependencies
- Django
- Selenium
- python-dotenv
- @supabase/supabase-js
- Three.js

##  News Sources

PALLADIUM scrapes from the following international news outlets:

| Country | Script | News Source |
|---------|--------|-------------|
| 🇺🇸 USA | `Final_with_tags_USA.py` | usatoday.com |
| 🇮🇳 India | `Final_with_tags_INDIA.py` | ndtv.com |
| 🇷🇺 Russia | `Final_with_tags_RUSSIA.py` | tass.com |
| 🇨🇳 China | `Final_with_tags_CHINA.py` | cnn.com/china |
| 🇦🇺 Australia | `Final_with_tags_AUSTRALIA.py` | abc.net.au |

Each scraper operates independently, allowing for parallel execution and independent scaling.

##  Getting Started

### Prerequisites

- Python 3.x
- Chrome browser
- ChromeDriver
- Node.js (for frontend dependencies)
- Supabase account

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/nandhra702/Palladium.git
   cd Palladium
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Core packages needed:
   ```bash
   pip install django selenium python-dotenv
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   DJANGO_SECRET_KEY=your_secret_key
   ```

4. **Configure Supabase**
   
   Create the following tables in your Supabase project:
   - `USA_news`
   - `India_news`
   - `Russia_news`
   - `China_news`
   - `Australia_news`

### Running the Application

1. **Start the Django server**
   ```bash
   python manage.py runserver
   ```

2. **Access the application**
   
   Navigate to `http://localhost:8000` in your browser

3. **Run news scrapers** (optional)
   
   Execute individual scraper scripts to populate the database: (FOR NOW, until the cron jobs are not set)
   ```bash
   python Final_with_tags_USA.py
   python Final_with_tags_INDIA.py
   python Final_with_tags_RUSSIA.py
   python Final_with_tags_CHINA.py
   python Final_with_tags_AUSTRALIA.py
   ```

##  System Components

### Web Scrapers
- Selenium-based browser automation
- Country-specific scraping logic
- Automatic article extraction and metadata collection
- Integration with ArticleTagger for categorization

### ArticleTagger
Located in `tagging.py`, this component:
- Applies keyword-based semantic analysis
- Categorizes articles into predefined topics (Politics, Technology, Sports, etc.)
- Uses configurable threshold scoring
- Enables filtering and topic-based display

### Database Schema
Supabase PostgreSQL with five country-specific tables storing:
- Article metadata
- Full content
- Tags and categories
- Timestamps
- Source information

### Django Backend
- `settings.py`: Application configuration and database settings
- `urls.py`: URL routing patterns
- `models.py`: ORM models (e.g., `IndiaNews` class)
- `manage.py`: Django management commands

### Frontend
- `main.html`: Base template structure
- `globe.js`: Three.js 3D globe rendering and interaction logic
- `style.css`: Visual styling, animations, and responsive layout

##  Features

### Interactive 3D Globe
- WebGL-based rendering
- Country-specific news markers
- Click-to-view article details
- Smooth camera controls and animations

### Article Categorization
Automatic tagging into categories:
- Politics
- Technology
- Sports
- Business
- Entertainment
- Health
- Science
- And more...

### Real-time Data Access
Frontend connects directly to Supabase using the JavaScript client library, providing real-time access to the latest news without backend proxying.

## 🔧 Development

### Project Structure
```
Palladium/
├── Final_with_tags_USA.py
├── Final_with_tags_INDIA.py
├── Final_with_tags_RUSSIA.py
├── Final_with_tags_CHINA.py
├── Final_with_tags_AUSTRALIA.py
├── tagging.py
├── settings.py
├── urls.py
├── models.py
├── manage.py
├── templates/
│   └── main.html
├── static/
    ├── globe.js
    └── style.css

```

### Best Practices
- Shared ArticleTagger and Selenium driver configurations across scrapers
- Independent scraper execution for parallel processing
- ETL (Extract-Transform-Load) pipeline per country
- Periodic batch job execution for data updates (to be done)

## Data Pipeline

The system follows an ETL pattern for each country:

1. **Extract**: Scrapers fetch articles from news sources
2. **Transform**: ArticleTagger analyzes and categorizes content
3. **Load**: Articles are inserted into Supabase using `insert()` method
4. **Display**: Frontend fetches data using `select()` method and renders on globe

## Acknowledgments

- Three.js for 3D visualization capabilities
- Supabase for cloud database infrastructure
- Django for robust backend framework
- All news sources for providing publicly accessible content











> start the virtual environment
-> pip install Django
-> pip install Supabase


-> npm install three three-globe,
-> pip install django
-> pip install dotenv
-> pip install selenium
-> pip install smthing else also i forgot, while running the command : python3 manage.py runserver, it will give error, install that package




