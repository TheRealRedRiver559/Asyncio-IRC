import asyncio
from misc.database import cursor, conn

log_queue = asyncio.Queue()
async def process_log_queue() -> None:
    while True:
        await asyncio.sleep(10)  # Wait for 10 seconds before processing logs
        try:
            # Process all messages that are in the queue
            while not log_queue.empty():
                log_entry = await log_queue.get()
                # Insert log into the database
                cursor.execute("""
                    INSERT INTO logs (log_type, message, additional_info) 
                    VALUES (?, ?, ?);
                """, (log_entry['log_type'], log_entry['message'], log_entry['additional_info']))
                log_queue.task_done()  # Mark the task as done
            # If all went well, commit the transaction
            conn.commit()
        except Exception as e:
            # If an error occurs, roll back any changes made during the transaction
            conn.rollback()
            print(f"Error processing log queue: {e}")

# Function to add a new log to the queue
async def add_log(log_type: str, message: str, additional_info=None) -> None:
    log_entry = {
        'log_type': log_type,
        'message': message,
        'additional_info': additional_info
    }
    await log_queue.put(log_entry)

