"""Database connection and management"""
from prisma import Prisma
import logging

logger = logging.getLogger(__name__)

db = Prisma()


async def connect_db():
    """Connect to database"""
    try:
        await db.connect()
        logger.info("Connected to database successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise


async def disconnect_db():
    """Disconnect from database"""
    try:
        await db.disconnect()
        logger.info("Disconnected from database")
    except Exception as e:
        logger.error(f"Error disconnecting from database: {str(e)}")
