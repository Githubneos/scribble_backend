from __init__ import app, db
from model.user import initUsers
from model.section import initSections
from model.group import initGroups
from model.channel import initChannels
from model.post import initPosts
from model.nestPost import initNestPosts
from model.vote import initVotes
from model.guess import initGuessDataTable
from model.leaderboard import initLeaderboardTable
from model.drawing import initDrawingTable

def init_db():
    with app.app_context():
        db.create_all()
        initUsers()
        initSections()
        initGroups()
        initChannels()
        initPosts()
        initNestPosts()
        initVotes()
        initGuessDataTable()
        initLeaderboardTable()
        initDrawingTable()
        print("Database and tables initialized.")

if __name__ == "__main__":
    init_db()
