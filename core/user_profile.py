import os
import json
import time

class UserProfile:
    """Manages user profiles and high scores"""
    
    def __init__(self, settings):
        self.settings = settings
        self.profile_dir = "config"
        self.scores_file = os.path.join(self.profile_dir, "scores.json")
        self.current_user = settings["player"]["name"]
        self.scores = self.load_scores()
        
    def load_scores(self):
        """Load scores from the scores file"""
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("Error loading scores file, creating new one")
        
        # Create default scores structure
        return {"users": {self.current_user: {"games": {}}}}
    
    def save_scores(self):
        """Save scores to the scores file"""
        try:
            with open(self.scores_file, 'w') as f:
                json.dump(self.scores, f, indent=2)
        except Exception as e:
            print(f"Error saving scores: {e}")
    
    def add_score(self, game_id, score, level=1):
        """Add a new score for the current user"""
        # Ensure user exists
        if self.current_user not in self.scores["users"]:
            self.scores["users"][self.current_user] = {"games": {}}
            
        # Ensure game exists for user
        user_games = self.scores["users"][self.current_user]["games"]
        if game_id not in user_games:
            user_games[game_id] = {"scores": []}
            
        # Add the score with timestamp
        score_entry = {
            "score": score,
            "level": level,
            "timestamp": time.time()
        }
        
        user_games[game_id]["scores"].append(score_entry)
        
        # Sort scores (highest first)
        user_games[game_id]["scores"].sort(key=lambda x: x["score"], reverse=True)
        
        # Save scores
        self.save_scores()
        
    def get_high_score(self, game_id):
        """Get the highest score for the current user and game"""
        try:
            user_scores = self.scores["users"][self.current_user]["games"].get(game_id, {}).get("scores", [])
            if user_scores:
                return user_scores[0]["score"]
        except Exception:
            pass
            
        return 0
        
    def get_global_high_scores(self, game_id, limit=10):
        """Get global high scores for a game across all users"""
        all_scores = []
        
        for username, user_data in self.scores["users"].items():
            if game_id in user_data.get("games", {}):
                for score_entry in user_data["games"][game_id].get("scores", []):
                    all_scores.append({
                        "username": username,
                        "score": score_entry["score"],
                        "level": score_entry.get("level", 1),
                        "timestamp": score_entry.get("timestamp", 0)
                    })
        
        # Sort by score (highest first)
        all_scores.sort(key=lambda x: x["score"], reverse=True)
        
        return all_scores[:limit]
        
    def change_user(self, username):
        """Change the current user"""
        self.current_user = username
        self.settings["player"]["name"] = username
        
        # Ensure user exists in scores
        if username not in self.scores["users"]:
            self.scores["users"][username] = {"games": {}}
            self.save_scores()
        
        return True