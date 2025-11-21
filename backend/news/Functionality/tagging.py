import re

class ArticleTagger:
    """
    Automatically tags article content based on keywords and patterns.
    """
    
    def __init__(self):
        # Define keywords for each tag category
        self.tag_keywords = {
            "Political": [
                "president", "congress", "senate", "election", "vote", "campaign",
                "democrat", "republican", "legislation", "policy", "government",
                "white house", "capitol", "politician", "governor", "mayor",
                "political", "parliament", "bill", "law", "regulation"
            ],
            "Sports": [
                "game", "team", "player", "coach", "score", "win", "loss",
                "championship", "tournament", "league", "nfl", "nba", "mlb",
                "nhl", "soccer", "football", "basketball", "baseball", "athlete",
                "stadium", "match", "playoff", "season"
            ],
            "Global/International": [
                "international", "foreign", "country", "nation", "global",
                "world", "embassy", "diplomat", "treaty", "united nations",
                "border", "immigrant", "refugee", "war", "conflict", "overseas",
                "abroad", "china", "russia", "europe", "asia", "africa"
            ],
            "Weather": [
                "weather", "storm", "hurricane", "tornado", "flood", "rain",
                "snow", "temperature", "forecast", "climate", "wind", "drought",
                "thunderstorm", "blizzard", "heatwave", "cold front", "warning",
                "meteorologist", "precipitation", "degrees"
            ],
            "Science & Tech": [
                "technology", "science", "research", "study", "scientist",
                "innovation", "discovery", "experiment", "ai", "artificial intelligence",
                "computer", "software", "app", "startup", "tech", "digital",
                "internet", "cyber", "data", "algorithm", "space", "nasa"
            ],
            "Health": [
                "health", "medical", "doctor", "hospital", "patient", "disease",
                "virus", "vaccine", "medicine", "treatment", "cdc", "fda",
                "pandemic", "epidemic", "symptom", "diagnosis", "healthcare",
                "mental health", "therapy", "drug", "prescription"
            ],
            "Business/Economy": [
                "business", "economy", "market", "stock", "company", "ceo",
                "profit", "revenue", "financial", "investment", "trade",
                "industry", "corporation", "banking", "wall street", "dollar",
                "economic", "employment", "job", "unemployment", "recession"
            ],
            "Crime": [
                "police", "arrest", "crime", "criminal", "investigation",
                "suspect", "victim", "murder", "robbery", "theft", "assault",
                "detective", "trial", "court", "lawsuit", "prison", "jail",
                "officer", "shooting", "violence", "fbi", "charged"
            ],
            "Education": [
                "school", "student", "teacher", "education", "university",
                "college", "classroom", "learning", "degree", "academic",
                "campus", "tuition", "graduation", "professor", "curriculum",
                "test", "exam", "study", "scholarship"
            ],
            "Entertainment": [
                "movie", "film", "actor", "actress", "music", "concert",
                "celebrity", "hollywood", "entertainment", "show", "series",
                "album", "song", "artist", "performance", "award", "netflix",
                "streaming", "tv", "television", "theater"
            ],
            "Environment": [
                "environment", "climate change", "pollution", "wildlife",
                "endangered", "conservation", "ecosystem", "sustainability",
                "carbon", "emissions", "renewable", "fossil fuel", "recycling",
                "deforestation", "ocean", "species", "habitat", "green energy"
            ],
            "Disaster": [
                "fire", "wildfire", "earthquake", "disaster", "emergency",
                "evacuation", "rescue", "damage", "destruction", "casualties",
                "explosion", "crash", "accident", "collapsed", "victims"
            ]
        }
    
    def tag_article(self, content, threshold=2):
        """
        Tag article content based on keyword matching.
        
        Args:
            content (str or list): Article content as string or list of paragraphs
            threshold (int): Minimum keyword matches required to assign a tag
            
        Returns:
            list: List of tags that apply to the content
        """
        # Convert content to lowercase string
        if isinstance(content, list):
            text = " ".join(content).lower()
        else:
            text = content.lower()
        
        # Count keyword matches for each tag
        tag_scores = {}
        
        for tag, keywords in self.tag_keywords.items():
            score = 0
            for keyword in keywords:
                # Count occurrences of each keyword
                score += len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))
            
            tag_scores[tag] = score
        
        # Assign tags that meet the threshold
        assigned_tags = [tag for tag, score in tag_scores.items() if score >= threshold]
        
        # If no tags assigned, return "Other"
        if not assigned_tags:
            assigned_tags = ["Other"]
        
        return assigned_tags
    
