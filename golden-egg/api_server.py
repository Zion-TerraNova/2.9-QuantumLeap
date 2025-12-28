#!/usr/bin/env python3
"""
🥚 Golden Egg Game - REST API
==============================

FastAPI backend for Golden Egg treasure hunt.

Endpoints:
- GET /api/golden-egg/status - Game statistics
- GET /api/golden-egg/clue/:id - Get clue (if unlocked)
- POST /api/golden-egg/solve - Submit solution
- POST /api/golden-egg/hint - Purchase hint
- GET /api/golden-egg/progress/:wallet - Player progress
- GET /api/golden-egg/leaderboard - Top players

Author: ZION Network Team
Version: 0.1.0 (Skeleton)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from golden_egg.game_engine import GoldenEggGame, create_genesis_clue

# Initialize FastAPI app
app = FastAPI(
    title="ZION Golden Egg API",
    description="REST API for 1 Billion ZION treasure hunt",
    version="0.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize game engine
game = GoldenEggGame()

# Initialize with genesis clue if empty
try:
    genesis = create_genesis_clue()
    game.add_clue(genesis)
except:
    pass  # Already exists


# Request/Response models
class SolutionSubmit(BaseModel):
    wallet_address: str
    clue_id: int
    solution: str


class HintRequest(BaseModel):
    wallet_address: str
    clue_id: int
    hint_number: int


class PlayerRegister(BaseModel):
    wallet_address: str


# API Endpoints

@app.get("/")
async def root():
    """API root"""
    return {
        "name": "ZION Golden Egg API",
        "version": "0.1.0",
        "description": "1 Billion ZION treasure hunt",
        "endpoints": [
            "/api/golden-egg/status",
            "/api/golden-egg/clue/{id}",
            "/api/golden-egg/solve",
            "/api/golden-egg/hint",
            "/api/golden-egg/progress/{wallet}",
            "/api/golden-egg/leaderboard"
        ]
    }


@app.get("/api/golden-egg/status")
async def get_game_status():
    """Get overall game statistics"""
    return game.get_game_stats()


@app.get("/api/golden-egg/clue/{clue_id}")
async def get_clue(clue_id: int, wallet: Optional[str] = None):
    """
    Get clue details (riddle, difficulty, etc.)
    Hints are NOT included - must be purchased separately
    """
    clue = game.get_clue(clue_id)
    
    if not clue:
        raise HTTPException(status_code=404, detail=f"Clue #{clue_id} not found")
    
    # Check if clue is unlocked for this player
    if wallet:
        # TODO: Check player's current_clue_id
        pass
    
    # Return clue without hints (hints must be purchased)
    return {
        "id": clue.id,
        "category": clue.category,
        "title": clue.title,
        "riddle": clue.riddle,
        "difficulty": clue.difficulty,
        "karma_reward": clue.karma_reward,
        "status": clue.status,
        "discovered_by": clue.discovered_by[:12] + "..." if clue.discovered_by else None,
        "location_hint": clue.location
    }


@app.post("/api/golden-egg/register")
async def register_player(player: PlayerRegister):
    """Register new player"""
    progress = game.register_player(player.wallet_address)
    
    return {
        "success": True,
        "wallet_address": progress.wallet_address,
        "current_clue_id": progress.current_clue_id,
        "karma_points": progress.karma_points,
        "clues_discovered": progress.clues_discovered
    }


@app.post("/api/golden-egg/solve")
async def submit_solution(submission: SolutionSubmit):
    """Submit solution for a clue"""
    result = game.submit_solution(
        submission.wallet_address,
        submission.clue_id,
        submission.solution
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@app.post("/api/golden-egg/hint")
async def purchase_hint(request: HintRequest):
    """Purchase hint using karma points"""
    result = game.purchase_hint(
        request.wallet_address,
        request.clue_id,
        request.hint_number
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@app.get("/api/golden-egg/progress/{wallet_address}")
async def get_player_progress(wallet_address: str):
    """Get player's current progress"""
    import sqlite3
    
    conn = sqlite3.connect(game.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM player_progress WHERE wallet_address = ?
    """, (wallet_address,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Player not registered")
    
    available_karma = row[2] - row[3]  # karma_points - karma_spent
    
    return {
        "wallet_address": row[0],
        "clues_discovered": row[1],
        "karma_points": row[2],
        "karma_spent": row[3],
        "karma_available": available_karma,
        "hints_used": row[4],
        "current_clue_id": row[7],
        "days_playing": int((game._get_timestamp() - row[5]) / (24 * 60 * 60))
    }


@app.get("/api/golden-egg/leaderboard")
async def get_leaderboard(limit: int = 10):
    """Get top players"""
    return {
        "leaderboard": game.get_leaderboard(limit),
        "total_players": len(game.get_leaderboard(9999))
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ZION Golden Egg API",
        "version": "0.1.0"
    }


# Helper for timestamp
def _get_timestamp():
    import time
    return time.time()

GoldenEggGame._get_timestamp = _get_timestamp


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("🥚 ZION GOLDEN EGG API - STARTING")
    print("=" * 70)
    print()
    print("📡 API will be available at: http://localhost:8002")
    print("📖 Documentation at: http://localhost:8002/docs")
    print()
    print("🎮 Golden Egg treasure hunt is LIVE!")
    print("   Prize: 1,000,000,000 ZION")
    print("   Clues: 108 (currently 1 active)")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
