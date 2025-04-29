from src.database.database import init_db
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")

if __name__ == "__main__":
    main() 