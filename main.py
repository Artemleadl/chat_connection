import os
from src.bot import create_bot
from src.database.database import init_db
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    # Create necessary directories
    os.makedirs("sessions", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Initialize database
    init_db()
    
    # Create and start bot
    bot = create_bot()
    logger.info("Starting bot...")
    bot.run_polling()

if __name__ == "__main__":
    main() 