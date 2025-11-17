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
    
    # def tag_article_detailed(self, content, threshold=2):
    #     """
    #     Tag article with detailed scoring information.
        
    #     Args:
    #         content (str or list): Article content
    #         threshold (int): Minimum keyword matches required
            
    #     Returns:
    #         dict: Dictionary with tags and their scores
    #     """
    #     # Convert content to lowercase string
    #     if isinstance(content, list):
    #         text = " ".join(content).lower()
    #     else:
    #         text = content.lower()
        
    #     # Count keyword matches for each tag
    #     tag_scores = {}
        
    #     for tag, keywords in self.tag_keywords.items():
    #         score = 0
    #         matched_keywords = []
    #         for keyword in keywords:
    #             count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))
    #             if count > 0:
    #                 score += count
    #                 matched_keywords.append((keyword, count))
            
    #         tag_scores[tag] = {
    #             "score": score,
    #             "matched_keywords": matched_keywords,
    #             "assigned": score >= threshold
    #         }
        
    #     return tag_scores


# # ---------- USAGE EXAMPLE ----------
# if __name__ == "__main__":
#     # Create tagger instance
#     tagger = ArticleTagger()
    
#     # Example 1: Single string content
#     article_text = """
#     The president announced new legislation today in Congress. 
#     Senate Democrats and Republicans are debating the bill. 
#     The White House released a statement about the policy changes.
#     """
    
#     tags = tagger.tag_article(article_text)
#     print("Example 1 - Detected tags:", tags)
    
#     # Example 2: List of paragraphs (from web scraper)
#     scraped_content = [
#         "A massive wildfire is threatening communities in California.",
#         "Firefighters are working to contain the blaze as strong winds continue.",
#         "Thousands have been evacuated from their homes.",
#         "Climate scientists say extreme weather events are becoming more frequent."
#     ]
    
#     tags = tagger.tag_article(scraped_content)
#     print("\nExample 2 - Detected tags:", tags)
    
#     # Example 3: Detailed tagging with scores
#     detailed = tagger.tag_article_detailed(scraped_content)
#     print("\nExample 3 - Detailed analysis:")
#     for tag, info in detailed.items():
#         if info["assigned"]:
#             print(f"\n{tag}: Score {info['score']}")
#             print(f"  Matched keywords: {info['matched_keywords']}")
    
#     # Example 4: Integration with web scraper output
#     print("\n" + "="*50)
#     print("INTEGRATION EXAMPLE:")
#     print("="*50)
    
#     # Simulated scraper output
#     scraper_output = """
#     The NBA finals concluded last night with a dramatic victory.
#     The team's star player scored 35 points in the championship game.
#     Fans celebrated in the streets after the final buzzer.
#     The coach praised his team's performance throughout the season.
#     """
    
#     tags = tagger.tag_article(scraper_output, threshold=3)
#     print(f"\nArticle content tagged as: {', '.join(tags)}")