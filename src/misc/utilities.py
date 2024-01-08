from datetime import timedelta
from misc.database import cursor

async def format_time_left(time_left: timedelta):
    days, remainder = divmod(time_left.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    if days > 0:
        return f"{int(days)} days, {int(hours)} hours, and {int(minutes)} minutes remaining"
    elif hours > 0:
        return f"{int(hours)} hours and {int(minutes)} minutes remaining"
    else:
        return f"{int(minutes)} minutes and {int(seconds)} seconds remaining"
    
async def user_id_from_username(username: str) -> list:
    cursor.execute("SELECT user_id FROM users WHERE username = ?", (username, ))
    user_record = cursor.fetchone()
    return user_record
