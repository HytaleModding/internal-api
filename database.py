import aiomysql
import os
from contextlib import asynccontextmanager

class Database:
    def __init__(self):
        self.pool = None
    
    async def init_pool(self):
        self.pool = await aiomysql.create_pool(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            db=os.getenv('DB_NAME', 'hytale_modding'),
            autocommit=True
        )
    
    async def get_server_stats(self, guild_id: int, limit: int = 10):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("""
                    SELECT * FROM server_stats 
                    WHERE guild_id = %s 
                    ORDER BY timestamp DESC 
                    LIMIT %s
                """, (guild_id, limit))
                return await cursor.fetchall()
    
    async def get_latest_server_stats(self, guild_id: int):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("""
                    SELECT * FROM server_stats 
                    WHERE guild_id = %s 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """, (guild_id,))
                return await cursor.fetchone()
    
    async def get_user_activity(self, guild_id: int, days: int = 7):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("""
                    SELECT * FROM user_activity 
                    WHERE guild_id = %s 
                    AND last_message >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    ORDER BY last_message DESC
                """, (guild_id, days))
                return await cursor.fetchall()
    
    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

db = Database()