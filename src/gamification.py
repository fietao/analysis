"""
Gamification System
Handles badges, points, achievements, and leaderboards
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

# ============================================================================
# Badge Definitions
# ============================================================================

BADGE_DEFINITIONS = {
    "first_login": {
        "name": "New Member",
        "description": "Logged in for the first time",
        "icon": "🎉",
        "points": 10,
        "tier": "bronze"
    },
    "login_streak_7": {
        "name": "On Fire! 🔥",
        "description": "7-day login streak",
        "icon": "🔥",
        "points": 50,
        "tier": "silver"
    },
    "login_streak_30": {
        "name": "Unstoppable",
        "description": "30-day login streak",
        "icon": "⭐",
        "points": 200,
        "tier": "gold"
    },
    "analysis_master": {
        "name": "Analysis Master",
        "description": "Completed 50 stock analyses",
        "icon": "📊",
        "points": 100,
        "tier": "silver"
    },
    "screening_expert": {
        "name": "Screening Expert",
        "description": "Completed 100 stock screenings",
        "icon": "🔍",
        "points": 150,
        "tier": "gold"
    },
    "profiler": {
        "name": "Pro Profile",
        "description": "Completed full user profile",
        "icon": "👤",
        "points": 25,
        "tier": "bronze"
    },
    "early_adopter": {
        "name": "Early Adopter",
        "description": "In first 1000 users",
        "icon": "🚀",
        "points": 500,
        "tier": "platinum"
    },
    "premium_user": {
        "name": "Premium Member",
        "description": "Upgraded to premium tier",
        "icon": "💎",
        "points": 200,
        "tier": "gold"
    },
    "top_10_leaderboard": {
        "name": "Top 10",
        "description": "Ranked in top 10",
        "icon": "🏆",
        "points": 250,
        "tier": "gold"
    },
    "top_100_leaderboard": {
        "name": "Top 100",
        "description": "Ranked in top 100",
        "icon": "🥇",
        "points": 100,
        "tier": "silver"
    },
    "referrer": {
        "name": "Brand Ambassador",
        "description": "Referred 3 friends",
        "icon": "👥",
        "points": 150,
        "tier": "gold"
    }
}

# ============================================================================
# Points System
# ============================================================================

POINTS_ACTIONS = {
    "login": 5,  # Daily login
    "first_login": 10,
    "analysis": 10,  # Each analysis run
    "analysis_saved": 15,  # Save analysis to portfolio
    "screening": 8,  # Each screening
    "screening_shared": 20,  # Share screening result
    "profile_complete": 50,
    "profile_photo_set": 10,
    "bio_added": 5,
    "ai_chat": 3,  # Each AI assistant message
    "ai_chat_follow_up": 5,
    "video_watched": 2,  # Per 10 minutes watched
    "video_completed": 25,
    "comment_posted": 3,
    "post_liked": 1,  # When others like your post
    "referral_join": 50,  # Friend joins via referral
    "portfolio_tracked": 5,  # Add to portfolio
    "alert_set": 3,  # Price alert or news alert
    "article_read": 2
}

# ============================================================================
# Gamification Service
# ============================================================================

class GamificationService:
    """Handle all gamification logic"""
    
    def __init__(self):
        self.badges = BADGE_DEFINITIONS
        self.points_config = POINTS_ACTIONS
    
    def calculate_points_for_action(self, action: str, metadata: Optional[dict] = None) -> int:
        """
        Calculate points earned for an action
        
        Args:
            action: Action type (e.g., 'login', 'analysis')
            metadata: Additional context (e.g., {'streak': 5, 'premium': True})
        
        Returns:
            Points earned
        """
        base_points = self.points_config.get(action, 0)
        
        if not metadata:
            return base_points
        
        # Bonus multipliers
        multiplier = 1.0
        
        # Premium user bonus (1.5x)
        if metadata.get("premium"):
            multiplier *= 1.5
        
        # Streak bonus (1 + streak * 0.1, capped at 2.0x)
        if "streak" in metadata:
            streak_bonus = 1.0 + (min(metadata["streak"], 10) * 0.1)
            multiplier *= min(streak_bonus, 2.0)
        
        # Consecutive action bonus
        if "consecutive_actions" in metadata:
            consecutive_bonus = 1.0 + (min(metadata["consecutive_actions"], 5) * 0.1)
            multiplier *= min(consecutive_bonus, 1.5)
        
        final_points = int(base_points * multiplier)
        return max(final_points, base_points)  # Never less than base
    
    def check_badge_eligibility(
        self,
        user_id: int,
        badge_type: str,
        user_stats: dict,
        current_badges: List[str]
    ) -> Tuple[bool, str]:
        """
        Check if user is eligible for a badge
        
        Args:
            user_id: User ID
            badge_type: Badge type to check
            user_stats: User statistics dict with counts
            current_badges: List of badges user already has
        
        Returns:
            Tuple of (is_eligible, reason)
        """
        # Already has badge
        if badge_type in current_badges:
            return False, "Already earned"
        
        badge = self.badges.get(badge_type)
        if not badge:
            return False, "Badge not found"
        
        # Check conditions for each badge type
        if badge_type == "first_login":
            return True, "First login"
        
        elif badge_type == "login_streak_7":
            if user_stats.get("login_streak", 0) >= 7:
                return True, "7-day streak achieved"
            return False, f"Need 7-day streak (current: {user_stats.get('login_streak', 0)})"
        
        elif badge_type == "login_streak_30":
            if user_stats.get("login_streak", 0) >= 30:
                return True, "30-day streak achieved"
            return False, f"Need 30-day streak (current: {user_stats.get('login_streak', 0)})"
        
        elif badge_type == "analysis_master":
            if user_stats.get("analysis_count", 0) >= 50:
                return True, "50 analyses completed"
            return False, f"Need 50 analyses (current: {user_stats.get('analysis_count', 0)})"
        
        elif badge_type == "screening_expert":
            if user_stats.get("screening_count", 0) >= 100:
                return True, "100 screenings completed"
            return False, f"Need 100 screenings (current: {user_stats.get('screening_count', 0)})"
        
        elif badge_type == "profiler":
            required_fields = ["bio", "profile_photo", "portfolio"]
            completed = user_stats.get("profile_fields", [])
            if all(field in completed for field in required_fields):
                return True, "Profile completed"
            return False, "Complete profile to earn"
        
        elif badge_type == "premium_user":
            if user_stats.get("subscription_tier") in ["pro", "enterprise"]:
                return True, "Premium subscription active"
            return False, "Upgrade to premium"
        
        elif badge_type == "top_10_leaderboard":
            if user_stats.get("leaderboard_rank", 999) <= 10:
                return True, "Top 10 ranking"
            return False, f"Need top 10 (current rank: {user_stats.get('leaderboard_rank')})"
        
        elif badge_type == "top_100_leaderboard":
            if user_stats.get("leaderboard_rank", 999) <= 100:
                return True, "Top 100 ranking"
            return False, f"Need top 100 (current rank: {user_stats.get('leaderboard_rank')})"
        
        elif badge_type == "referrer":
            if user_stats.get("referral_count", 0) >= 3:
                return True, "3 referrals"
            return False, f"Need 3 referrals (current: {user_stats.get('referral_count', 0)})"
        
        elif badge_type == "early_adopter":
            if user_stats.get("user_rank", 999) <= 1000:
                return True, "Early adopter"
            return False, "Only for first 1000 users"
        
        return False, "Badge conditions not met"
    
    def calculate_leaderboard_rank(
        self,
        user_id: int,
        user_points: int,
        all_user_points: List[Tuple[int, int]]
    ) -> int:
        """
        Calculate leaderboard rank for a user
        
        Args:
            user_id: User ID
            user_points: User's total points
            all_user_points: List of (user_id, points) tuples for all users
        
        Returns:
            Rank (1 = highest, 2 = second, etc.)
        """
        # Sort by points descending
        sorted_points = sorted(all_user_points, key=lambda x: x[1], reverse=True)
        
        rank = 1
        same_score_rank = 1
        prev_score = None
        
        for i, (uid, points) in enumerate(sorted_points):
            if prev_score is not None and points < prev_score:
                rank = i + 1
                same_score_rank = 1
            
            if uid == user_id:
                return rank
            
            prev_score = points
        
        return len(sorted_points) + 1  # Not found, rank at bottom
    
    def get_tier_for_points(self, total_points: int) -> str:
        """
        Determine user tier based on total points
        """
        if total_points >= 10000:
            return "platinum"
        elif total_points >= 5000:
            return "gold"
        elif total_points >= 2000:
            return "silver"
        elif total_points >= 500:
            return "bronze"
        else:
            return "member"
    
    def get_next_milestone(self, current_points: int) -> Dict:
        """Get next achievement milestone for user"""
        milestones = [500, 1000, 2000, 5000, 10000]
        
        for milestone in milestones:
            if current_points < milestone:
                return {
                    "milestone": milestone,
                    "points_needed": milestone - current_points,
                    "tier": self.get_tier_for_points(milestone)
                }
        
        return {
            "milestone": "You're a champion! 🏆",
            "points_needed": 0,
            "tier": "platinum"
        }
    
    def calculate_daily_bonus(self, login_streak: int, is_first_today: bool) -> int:
        """
        Calculate bonus points for daily login
        
        Args:
            login_streak: Current login streak
            is_first_today: First visit today
        
        Returns:
            Bonus points
        """
        if not is_first_today:
            return 0  # No bonus for multiple logins same day
        
        base_bonus = 5
        
        # Increasing bonus for streaks
        streak_bonus = min(login_streak, 30) // 3  # 0-10 bonus
        
        return base_bonus + streak_bonus

# ============================================================================
# Leaderboard Service
# ============================================================================

class LeaderboardService:
    """Handle leaderboard calculations and rankings"""
    
    @staticmethod
    def get_global_leaderboard(
        user_points_list: List[Tuple[int, int, str]], # (user_id, points, username)
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """
        Get global leaderboard
        
        Args:
            user_points_list: List of (user_id, points, username)
            limit: Number of entries to return
            offset: Starting position
        
        Returns:
            List of leaderboard entries with rank
        """
        sorted_leaderboard = sorted(
            user_points_list,
            key=lambda x: x[1],
            reverse=True
        )
        
        leaderboard = []
        for rank, (user_id, points, username) in enumerate(sorted_leaderboard[offset:offset+limit], 1):
            leaderboard.append({
                "rank": rank + offset,
                "user_id": user_id,
                "username": username,
                "points": points,
                "tier": GamificationService().get_tier_for_points(points)
            })
        
        return leaderboard
    
    @staticmethod
    def get_user_rank_context(
        user_id: int,
        user_points: int,
        all_user_points: List[Tuple[int, int]]
    ) -> Dict:
        """
        Get user's rank and surrounding context
        
        Args:
            user_id: User ID
            user_points: User's points
            all_user_points: List of (user_id, points)
        
        Returns:
            Dict with rank and nearby competitors
        """
        sorted_list = sorted(all_user_points, key=lambda x: x[1], reverse=True)
        
        user_rank = None
        for i, (uid, points) in enumerate(sorted_list):
            if uid == user_id:
                user_rank = i + 1
                break
        
        if user_rank is None:
            return {"rank": None, "points": user_points}
        
        # Get entries around user
        start = max(0, user_rank - 3)
        end = min(len(sorted_list), user_rank + 2)
        
        nearby = []
        for i in range(start, end):
            uid, points = sorted_list[i]
            nearby.append({
                "rank": i + 1,
                "is_user": uid == user_id,
                "points": points
            })
        
        return {
            "rank": user_rank,
            "total_users": len(sorted_list),
            "percentile": round((user_rank / len(sorted_list)) * 100, 1),
            "nearby_ranks": nearby
        }
    
    @staticmethod
    def get_weekly_leaderboard(
        weekly_points: Dict[int, int],  # user_id -> points
        limit: int = 50
    ) -> List[Dict]:
        """Get weekly leaderboard (resets every Sunday)"""
        sorted_weekly = sorted(
            weekly_points.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        leaderboard = []
        for rank, (user_id, points) in enumerate(sorted_weekly[:limit], 1):
            leaderboard.append({
                "rank": rank,
                "user_id": user_id,
                "weekly_points": points,
                "badge": "⭐" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else ""
            })
        
        return leaderboard

# ============================================================================
# Achievement Tracker
# ============================================================================

class AchievementTracker:
    """Track user achievements and log them"""
    
    def __init__(self):
        self.gamification = GamificationService()
    
    def log_achievement(
        self,
        user_id: int,
        action: str,
        points_earned: int,
        metadata: Optional[dict] = None
    ) -> Dict:
        """
        Log an achievement for a user
        
        Returns:
            Achievement result with badges earned
        """
        result = {
            "user_id": user_id,
            "action": action,
            "points_earned": points_earned,
            "timestamp": datetime.utcnow(),
            "badges_earned": [],
            "new_tier": None
        }
        
        logger.info(f"Achievement logged for user {user_id}: {action} (+{points_earned} pts)")
        
        return result
    
    def process_badge_achievements(
        self,
        user_id: int,
        action: str,
        user_stats: dict
    ) -> List[str]:
        """
        Check and award badges after an action
        
        Returns:
            List of newly earned badge types
        """
        badges_earned = []
        
        if action == "login":
            is_eligible, _ = self.gamification.check_badge_eligibility(
                user_id, "first_login", user_stats, user_stats.get("current_badges", [])
            )
            if is_eligible:
                badges_earned.append("first_login")
        
        # Check streak badges
        streak = user_stats.get("login_streak", 0)
        if streak == 7:
            badges_earned.append("login_streak_7")
        elif streak == 30:
            badges_earned.append("login_streak_30")
        
        # Check activity badges
        if action == "analysis":
            if user_stats.get("analysis_count", 0) == 50:
                badges_earned.append("analysis_master")
        
        if action == "screening":
            if user_stats.get("screening_count", 0) == 100:
                badges_earned.append("screening_expert")
        
        # Check leaderboard badges
        rank = user_stats.get("leaderboard_rank")
        if rank == 10:
            badges_earned.append("top_10_leaderboard")
        elif rank == 100:
            badges_earned.append("top_100_leaderboard")
        
        return badges_earned
