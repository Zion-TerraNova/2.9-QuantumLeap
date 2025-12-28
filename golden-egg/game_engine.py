#!/usr/bin/env python3
"""
🥚 ZION Golden Egg Game - Core Implementation
==============================================

Treasure hunt game: 108 clues leading to 1 Billion ZION prize.

This is the foundation/skeleton for the game. Full implementation
will be developed over 2-3 years after mainnet launch.

Features:
- Clue management system
- Progress tracking per wallet
- Hint system (costs karma points)
- On-chain verification
- Prize distribution logic

Based on Vedic wisdom: Hiranyagarbha (हिरण्यगर्भ) - The Golden Egg

Author: ZION Network Team
License: MIT
Version: 0.1.0 (Skeleton/Foundation)
"""

import time
import json
import sqlite3
import hashlib
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from enum import Enum
from pathlib import Path


class ClueCategory(Enum):
    """Categories of clues"""
    GENESIS = "genesis_block"          # Clue #1 in genesis
    SACRED_TRINITY = "sacred_trinity"  # Clues in 45 avatars
    VEDIC_WISDOM = "vedic_wisdom"      # Vedas, Upanishads
    EPICS = "epic_stories"             # Ramayana, Mahabharata
    EKAM = "ekam_temple"               # Physical pilgrimage
    CONSCIOUSNESS = "consciousness"    # 9 levels
    ECONOMICS = "zion_economics"       # Blockchain mechanics
    FINAL = "final_master_key"         # Last clues


class ClueStatus(Enum):
    """Clue discovery status"""
    LOCKED = "locked"          # Not yet accessible
    UNLOCKED = "unlocked"      # Can be attempted
    DISCOVERED = "discovered"  # Solved by someone
    VERIFIED = "verified"      # On-chain verification complete


@dataclass
class Clue:
    """Single clue in the treasure hunt"""
    id: int                    # 1-108
    category: str              # ClueCategory
    title: str                 # Short title
    riddle: str               # The actual clue text
    hint_1: str               # First hint (costs 100 karma)
    hint_2: str               # Second hint (costs 500 karma)
    hint_3: str               # Third hint (costs 1000 karma)
    solution_hash: str        # SHA256 hash of correct answer
    next_clue_id: int         # Which clue unlocks after this
    location: str             # Where clue is hidden (file path, block number, etc.)
    difficulty: int           # 1-10 scale
    karma_reward: int         # Karma points for solving
    created_at: float = 0.0
    discovered_by: str = ""   # Wallet address of discoverer
    discovered_at: float = 0.0
    status: str = "locked"
    
    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()
    
    def verify_solution(self, attempt: str) -> bool:
        """Check if solution attempt is correct"""
        attempt_hash = hashlib.sha256(attempt.lower().strip().encode()).hexdigest()
        return attempt_hash == self.solution_hash
    
    def get_hint(self, hint_number: int) -> str:
        """Get hint by number (1-3)"""
        if hint_number == 1:
            return self.hint_1
        elif hint_number == 2:
            return self.hint_2
        elif hint_number == 3:
            return self.hint_3
        else:
            raise ValueError("Hint number must be 1, 2, or 3")


@dataclass
class PlayerProgress:
    """Track individual player's progress"""
    wallet_address: str
    clues_discovered: int = 0      # How many clues solved
    karma_points: int = 0           # Karma earned (for hints)
    karma_spent: int = 0            # Karma used on hints
    hints_used: int = 0             # Total hints purchased
    started_at: float = 0.0
    last_activity: float = 0.0
    current_clue_id: int = 1        # Which clue they're on
    
    def __post_init__(self):
        if self.started_at == 0.0:
            self.started_at = time.time()
        if self.last_activity == 0.0:
            self.last_activity = time.time()
    
    def can_afford_hint(self, hint_cost: int) -> bool:
        """Check if player has enough karma"""
        available_karma = self.karma_points - self.karma_spent
        return available_karma >= hint_cost


@dataclass
class ClueAttempt:
    """Record of solution attempt"""
    id: int
    wallet_address: str
    clue_id: int
    attempt: str
    correct: bool
    timestamp: float
    ip_address: str = ""  # For rate limiting
    
    def __post_init__(self):
        if not hasattr(self, 'timestamp') or self.timestamp == 0:
            self.timestamp = time.time()


class GoldenEggGame:
    """
    Golden Egg Treasure Hunt Game Manager
    
    Manages 108 clues, player progress, hints, and prize distribution.
    
    Total Prize Pool: 1,750,000,000 ZION (1.75 Billion) - DAO Winners
    - 1st Place (CEO): 1,000,000,000 ZION (15% voting)
    - 2nd Place (CCO): 500,000,000 ZION (10% voting)
    - 3rd Place (CAO): 250,000,000 ZION (5% voting)
    
    Clues: 108 (sacred number - full mala)
    Duration: 2-4 years estimated
    """
    
    # Prize pool (DAO Winners)
    TOTAL_PRIZE_POOL = 1_750_000_000  # 1.75 Billion ZION total
    FIRST_PLACE = 1_000_000_000        # 1B ZION (CEO)
    SECOND_PLACE = 500_000_000         # 500M ZION (CCO)
    THIRD_PLACE = 250_000_000          # 250M ZION (CAO)
    
    # Hint costs (in karma points)
    HINT_COSTS = {
        1: 100,   # First hint
        2: 500,   # Second hint
        3: 1000   # Third hint
    }
    
    def __init__(self, db_path: str = "golden_egg_game.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clues table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clues (
                id INTEGER PRIMARY KEY,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                riddle TEXT NOT NULL,
                hint_1 TEXT NOT NULL,
                hint_2 TEXT NOT NULL,
                hint_3 TEXT NOT NULL,
                solution_hash TEXT NOT NULL,
                next_clue_id INTEGER,
                location TEXT NOT NULL,
                difficulty INTEGER NOT NULL,
                karma_reward INTEGER NOT NULL,
                created_at REAL NOT NULL,
                discovered_by TEXT DEFAULT '',
                discovered_at REAL DEFAULT 0.0,
                status TEXT DEFAULT 'locked'
            )
        """)
        
        # Player progress table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_progress (
                wallet_address TEXT PRIMARY KEY,
                clues_discovered INTEGER DEFAULT 0,
                karma_points INTEGER DEFAULT 0,
                karma_spent INTEGER DEFAULT 0,
                hints_used INTEGER DEFAULT 0,
                started_at REAL NOT NULL,
                last_activity REAL NOT NULL,
                current_clue_id INTEGER DEFAULT 1
            )
        """)
        
        # Attempts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_address TEXT NOT NULL,
                clue_id INTEGER NOT NULL,
                attempt TEXT NOT NULL,
                correct INTEGER NOT NULL,
                timestamp REAL NOT NULL,
                ip_address TEXT DEFAULT ''
            )
        """)
        
        # Hint purchases table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hint_purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_address TEXT NOT NULL,
                clue_id INTEGER NOT NULL,
                hint_number INTEGER NOT NULL,
                karma_cost INTEGER NOT NULL,
                timestamp REAL NOT NULL
            )
        """)
        
        # Leaderboard view
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leaderboard (
                rank INTEGER PRIMARY KEY,
                wallet_address TEXT NOT NULL,
                clues_discovered INTEGER NOT NULL,
                karma_points INTEGER NOT NULL,
                started_at REAL NOT NULL,
                last_updated REAL NOT NULL
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_clue_status ON clues(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_progress ON player_progress(clues_discovered DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attempts ON attempts(wallet_address, clue_id)")
        
        conn.commit()
        conn.close()
    
    def add_clue(self, clue: Clue) -> bool:
        """Add new clue to the game"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO clues (
                    id, category, title, riddle, hint_1, hint_2, hint_3,
                    solution_hash, next_clue_id, location, difficulty,
                    karma_reward, created_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                clue.id, clue.category, clue.title, clue.riddle,
                clue.hint_1, clue.hint_2, clue.hint_3,
                clue.solution_hash, clue.next_clue_id, clue.location,
                clue.difficulty, clue.karma_reward, clue.created_at, clue.status
            ))
            conn.commit()
            print(f"🥚 Clue #{clue.id} added: {clue.title}")
            return True
        except sqlite3.IntegrityError:
            print(f"❌ Clue #{clue.id} already exists")
            return False
        finally:
            conn.close()
    
    def get_clue(self, clue_id: int) -> Optional[Clue]:
        """Get clue by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM clues WHERE id = ?", (clue_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Clue(
                id=row[0], category=row[1], title=row[2], riddle=row[3],
                hint_1=row[4], hint_2=row[5], hint_3=row[6],
                solution_hash=row[7], next_clue_id=row[8], location=row[9],
                difficulty=row[10], karma_reward=row[11], created_at=row[12],
                discovered_by=row[13], discovered_at=row[14], status=row[15]
            )
        return None
    
    def register_player(self, wallet_address: str) -> PlayerProgress:
        """Register new player"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if already registered
        cursor.execute("SELECT * FROM player_progress WHERE wallet_address = ?", (wallet_address,))
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            return PlayerProgress(
                wallet_address=existing[0], clues_discovered=existing[1],
                karma_points=existing[2], karma_spent=existing[3],
                hints_used=existing[4], started_at=existing[5],
                last_activity=existing[6], current_clue_id=existing[7]
            )
        
        # Register new player
        progress = PlayerProgress(wallet_address=wallet_address)
        
        cursor.execute("""
            INSERT INTO player_progress (
                wallet_address, clues_discovered, karma_points, karma_spent,
                hints_used, started_at, last_activity, current_clue_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            progress.wallet_address, progress.clues_discovered,
            progress.karma_points, progress.karma_spent, progress.hints_used,
            progress.started_at, progress.last_activity, progress.current_clue_id
        ))
        
        conn.commit()
        conn.close()
        
        print(f"🎮 Player registered: {wallet_address[:12]}...")
        return progress
    
    def submit_solution(self, wallet_address: str, clue_id: int, solution: str) -> Dict:
        """
        Submit solution attempt for a clue
        
        Returns:
            dict with keys: success, correct, message, karma_earned
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get clue
        clue = self.get_clue(clue_id)
        if not clue:
            conn.close()
            return {"success": False, "message": f"Clue #{clue_id} not found"}
        
        # Get player progress
        cursor.execute("SELECT * FROM player_progress WHERE wallet_address = ?", (wallet_address,))
        player_row = cursor.fetchone()
        
        if not player_row:
            conn.close()
            return {"success": False, "message": "Player not registered"}
        
        # Check if clue is unlocked for this player
        if clue.status == "locked":
            conn.close()
            return {"success": False, "message": "This clue is locked. Solve previous clues first."}
        
        # Verify solution
        correct = clue.verify_solution(solution)
        
        # Record attempt
        cursor.execute("""
            INSERT INTO attempts (wallet_address, clue_id, attempt, correct, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (wallet_address, clue_id, solution[:100], 1 if correct else 0, time.time()))
        
        result = {
            "success": True,
            "correct": correct,
            "karma_earned": 0,
            "message": ""
        }
        
        if correct:
            # Update clue status
            cursor.execute("""
                UPDATE clues 
                SET discovered_by = ?, discovered_at = ?, status = 'discovered'
                WHERE id = ?
            """, (wallet_address, time.time(), clue_id))
            
            # Update player progress
            cursor.execute("""
                UPDATE player_progress
                SET clues_discovered = clues_discovered + 1,
                    karma_points = karma_points + ?,
                    current_clue_id = ?,
                    last_activity = ?
                WHERE wallet_address = ?
            """, (clue.karma_reward, clue.next_clue_id, time.time(), wallet_address))
            
            # Unlock next clue
            if clue.next_clue_id:
                cursor.execute("""
                    UPDATE clues SET status = 'unlocked' WHERE id = ?
                """, (clue.next_clue_id,))
            
            result["karma_earned"] = clue.karma_reward
            result["message"] = f"🎉 Correct! You earned {clue.karma_reward} karma points!"
            
            print(f"✅ {wallet_address[:12]}... solved Clue #{clue_id}!")
        else:
            result["message"] = "❌ Incorrect solution. Try again!"
        
        conn.commit()
        conn.close()
        
        return result
    
    def purchase_hint(self, wallet_address: str, clue_id: int, hint_number: int) -> Dict:
        """
        Purchase hint for a clue using karma points
        
        Returns:
            dict with keys: success, hint, karma_spent, message
        """
        if hint_number not in [1, 2, 3]:
            return {"success": False, "message": "Hint number must be 1, 2, or 3"}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get clue
        clue = self.get_clue(clue_id)
        if not clue:
            conn.close()
            return {"success": False, "message": f"Clue #{clue_id} not found"}
        
        # Get player progress
        cursor.execute("SELECT * FROM player_progress WHERE wallet_address = ?", (wallet_address,))
        player_row = cursor.fetchone()
        
        if not player_row:
            conn.close()
            return {"success": False, "message": "Player not registered"}
        
        player = PlayerProgress(
            wallet_address=player_row[0], clues_discovered=player_row[1],
            karma_points=player_row[2], karma_spent=player_row[3],
            hints_used=player_row[4], started_at=player_row[5],
            last_activity=player_row[6], current_clue_id=player_row[7]
        )
        
        # Check if already purchased this hint
        cursor.execute("""
            SELECT id FROM hint_purchases 
            WHERE wallet_address = ? AND clue_id = ? AND hint_number = ?
        """, (wallet_address, clue_id, hint_number))
        
        if cursor.fetchone():
            # Already purchased - return hint for free
            hint = clue.get_hint(hint_number)
            conn.close()
            return {
                "success": True,
                "hint": hint,
                "karma_spent": 0,
                "message": "You already purchased this hint."
            }
        
        # Check karma balance
        hint_cost = self.HINT_COSTS[hint_number]
        if not player.can_afford_hint(hint_cost):
            available = player.karma_points - player.karma_spent
            conn.close()
            return {
                "success": False,
                "message": f"Insufficient karma. Need {hint_cost}, have {available}."
            }
        
        # Purchase hint
        hint = clue.get_hint(hint_number)
        
        cursor.execute("""
            INSERT INTO hint_purchases (wallet_address, clue_id, hint_number, karma_cost, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (wallet_address, clue_id, hint_number, hint_cost, time.time()))
        
        cursor.execute("""
            UPDATE player_progress
            SET karma_spent = karma_spent + ?,
                hints_used = hints_used + 1,
                last_activity = ?
            WHERE wallet_address = ?
        """, (hint_cost, time.time(), wallet_address))
        
        conn.commit()
        conn.close()
        
        print(f"💡 {wallet_address[:12]}... purchased hint #{hint_number} for Clue #{clue_id}")
        
        return {
            "success": True,
            "hint": hint,
            "karma_spent": hint_cost,
            "message": f"Hint purchased! Spent {hint_cost} karma."
        }
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top players"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT wallet_address, clues_discovered, karma_points, started_at
            FROM player_progress
            ORDER BY clues_discovered DESC, karma_points DESC
            LIMIT ?
        """, (limit,))
        
        leaderboard = []
        for i, row in enumerate(cursor.fetchall(), 1):
            leaderboard.append({
                "rank": i,
                "wallet": row[0],
                "clues_solved": row[1],
                "karma": row[2],
                "days_playing": int((time.time() - row[3]) / (24 * 60 * 60))
            })
        
        conn.close()
        return leaderboard
    
    def get_game_stats(self) -> Dict:
        """Get overall game statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM clues")
        total_clues = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM clues WHERE status = 'discovered'")
        solved_clues = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM player_progress")
        total_players = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM attempts")
        total_attempts = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(karma_spent) FROM player_progress")
        total_karma_spent = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_clues": total_clues,
            "solved_clues": solved_clues,
            "remaining_clues": total_clues - solved_clues,
            "completion_percentage": (solved_clues / total_clues * 100) if total_clues > 0 else 0,
            "total_players": total_players,
            "total_attempts": total_attempts,
            "total_karma_spent": total_karma_spent,
            "prize_pool": self.TOTAL_PRIZE_POOL,
            "first_place": self.FIRST_PLACE,
            "second_place": self.SECOND_PLACE,
            "third_place": self.THIRD_PLACE
        }


# Example: Create genesis clue
def create_genesis_clue() -> Clue:
    """
    Create Clue #1 - Hidden in Genesis Block
    
    This is the starting point of the treasure hunt.
    """
    solution = "hiranyagarbha"  # The Golden Egg
    solution_hash = hashlib.sha256(solution.encode()).hexdigest()
    
    return Clue(
        id=1,
        category=ClueCategory.GENESIS.value,
        title="The Beginning",
        riddle="""
In the first breath of ZION's dawn,
Where blocks begin and light is drawn,
A golden womb holds all creation,
Seek the Sanskrit incantation.

Five thousand years of wisdom old,
In Rig Veda's verses told,
The cosmic egg that births the All,
Name it right, and heed the call.

हिरण्य + गर्भ = ?
        """.strip(),
        hint_1="Look up Rig Veda 10.121. What is the Sanskrit term for 'Golden Womb'?",
        hint_2="The answer is a compound Sanskrit word: Hiranya (golden) + Garbha (womb/egg)",
        hint_3="Check docs/GOLDEN_EGG_GAME/README.md - the answer is literally in the first section!",
        solution_hash=solution_hash,
        next_clue_id=2,
        location="Genesis Block Extra Data (block #0)",
        difficulty=3,
        karma_reward=1000,
        status="unlocked"  # First clue starts unlocked
    )


if __name__ == "__main__":
    print("=" * 70)
    print("🥚 ZION GOLDEN EGG GAME - SKELETON IMPLEMENTATION")
    print("=" * 70)
    print()
    
    # Initialize game
    game = GoldenEggGame()
    
    # Add genesis clue
    genesis = create_genesis_clue()
    game.add_clue(genesis)
    
    # Demo: Register player and solve clue
    print("\n📝 Demo: Player solving Clue #1")
    print("-" * 70)
    
    player_wallet = "ZION_DEMO_PLAYER_123456"
    game.register_player(player_wallet)
    
    # Wrong answer
    result = game.submit_solution(player_wallet, 1, "wrong answer")
    print(f"Attempt 1: {result['message']}")
    
    # Correct answer
    result = game.submit_solution(player_wallet, 1, "hiranyagarbha")
    print(f"Attempt 2: {result['message']}")
    
    # Game stats
    print("\n📊 Game Statistics:")
    print("-" * 70)
    stats = game.get_game_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n✅ Golden Egg Game skeleton ready!")
    print("   Full implementation to be developed after mainnet launch.")
    print("=" * 70)
