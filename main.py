import os
from src.bot import create_bot
from src.database.database import init_db
from src.utils.logger import setup_logger
import signal
import sys

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

    def shutdown(signum, frame):
        logger.info(f"Received signal {signum}, shutting down bot...")
        bot.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    bot.run_polling()

if __name__ == "__main__":
    main() 