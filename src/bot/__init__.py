from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from src.bot.handlers import BotHandlers
from src.database.operations import DatabaseOperations
from src.core.session_manager import SessionManager
from src.database.database import get_db
from config.config import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def create_bot() -> Application:
    """
    Создает и настраивает бота
    """
    # Create application
    application = Application.builder().token(settings.BOT_TOKEN).build()
    
    # Create handlers
    db = next(get_db())
    db_ops = DatabaseOperations(db)
    session_manager = SessionManager(settings.SESSION_DIR)
    handlers = BotHandlers(db_ops, session_manager)
    
    # Add handlers
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CallbackQueryHandler(handlers.add_account, pattern="^add_account$"))
    application.add_handler(CallbackQueryHandler(handlers.check_account, pattern="^check_account$"))
    application.add_handler(CallbackQueryHandler(handlers.add_links, pattern="^add_links$"))
    application.add_handler(CallbackQueryHandler(handlers.start_joining, pattern="^start_joining$"))
    application.add_handler(CallbackQueryHandler(handlers.cancel_joining, pattern="^cancel_joining$"))
    application.add_handler(CallbackQueryHandler(handlers.show_errors, pattern="^show_errors$"))
    
    # Add message handlers
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handlers.handle_account_input
    ))
    
    return application 