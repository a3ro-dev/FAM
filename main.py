from libs import utilities


Util = utilities.Utilities()

class Setup:
    def __init__(self):
        self.db = 'db/user.db'

    async def insert_user_data(self, name, city, email, assistant_name):
        import aiosqlite
        # Connect to the SQLite database
        async with aiosqlite.connect(self.db) as db:
            # SQL statement to insert the user data
            insert_sql = """
            INSERT INTO User (name, city, email, assistant_name) 
            VALUES (?, ?, ?, ?);
            """
            # Execute the SQL statement
            await db.execute(insert_sql, (name, city, email, assistant_name))
            # Commit the transaction
            await db.commit()

    def setup(self):
        Util.speak('Welcome to the setup wizard. Please follow the instructions to setup the assistant.')
        Util.speak('Please enter the name by which you would like to call the assistant.')
        name = Util.getSpeech()
        Util.speak(f'Do you want to call the assistant {name}?, [yes/no]')
        response: str = Util.getSpeech()
        if 'yes' in response:
            self.name = name
            Util.speak('Setup 1 completed successfully.')
        elif 'no' in response:
            Util.speak('Please enter the name by which you would like to call the assistant.')
            name = Util.getSpeech()
            self.name = name
            Util.speak('Setup 1 completed successfully.')
        Util.speak('Please enter the city for which you would like to get weather updates.')
        city = Util.getSpeech()
        Util.speak(f'Do you want to get weather updates for {city}?, [yes/no]')
        response = Util.getSpeech()
        if 'yes' in response:
            self.city = city
            Util.speak('Setup 2 completed successfully.')
        elif 'no' in response:
            Util.speak('Please enter the city for which you would like to get weather updates.')
            city = Util.getSpeech()
            self.city = city
            Util.speak('Setup 2 completed successfully.')
        Util.speak('Please enter the email address to which you would like to receive emails.')
        email = Util.getSpeech()
        Util.speak(f'Do you want to receive emails on {email}?, [yes/no]')
        response = Util.getSpeech()
        if 'yes' in response:
            self.email = email
            Util.speak('Setup 3 completed successfully.')
        elif 'no' in response:
            Util.speak('Please enter the email address to which you would like to receive emails.')
            email = Util.getSpeech()
            self.email = email
            Util.speak('Setup 3 completed successfully.')
        Util.speak('Please enter your name:')
        name = Util.getSpeech()
        Util.speak(f'Welcome! {name}')
        Util.speak('Finishing setup wizard...')
        try:
            import asyncio
            Util.speak('Saving user data to the database...')
            asyncio.run(self.insert_user_data(name, city, email, self.name))
            Util.speak('User data saved successfully.')
            Util.speak('Setup completed successfully.')
        except Exception as e:
            Util.speak('An error occurred while saving user data to the database.')
            Util.speak(f'Error: {e}')



if __name__ == '__main__':
    pass
        

        
