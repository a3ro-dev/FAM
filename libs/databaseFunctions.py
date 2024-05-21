import aiosqlite

class Database:
    """
    A class that provides database functions for retrieving user information.
    """

    def __init__(self):
        self.db_path = r"F:\ai-assistant\pico-files\db\user.db"

    async def get_name(self, name):
        """
        Retrieves the name of a user from the database.

        Args:
            name (str): The name of the user.

        Returns:
            str: The name of the user if found, None otherwise.
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT name FROM User WHERE name = ?", (name,))
            row = await cursor.fetchone()
            return row[0] if row else None

    async def get_email(self, name):
        """
        Retrieves the email of a user from the database.

        Args:
            name (str): The name of the user.

        Returns:
            str: The email of the user if found, None otherwise.
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT email FROM User WHERE name = ?", (name,))
            row = await cursor.fetchone()
            return row[0] if row else None

    async def get_assistant_name(self, name):
        """
        Retrieves the assistant name of a user from the database.

        Args:
            name (str): The name of the user.

        Returns:
            str: The assistant name of the user if found, None otherwise.
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT assistant_name FROM User WHERE name = ?", (name,))
            row = await cursor.fetchone()
            return row[0] if row else None

    async def get_location(self, name):
        """
        Retrieves the location of a user from the database.

        Args:
            name (str): The name of the user.

        Returns:
            str: The location of the user if found, None otherwise.
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT city FROM User WHERE name = ?", (name,))
            row = await cursor.fetchone()
            return row[0] if row else None


# # Example Usage        
# import asyncio

# async def main():
#     db = Database()
#     print(await db.get_name('akshat'))
#     print(await db.get_email('akshat'))
#     print(await db.get_assistant_name('akshat'))
#     print(await db.get_location('akshat'))

# # Run the main function using asyncio.run, which creates a new event loop and runs the coroutine
# asyncio.run(main())