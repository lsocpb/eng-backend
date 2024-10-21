
# Task to check if an auction has ended
def check_auctions():
    now = datetime.now(pytz.UTC)
    for auction in auctions:
        if auction["status"] == "active" and auction["end_time"] <= now:
            auction["status"] = "ended"
            # If there's a winner, send an email
            if auction["winner"]:
                print(f"Auction {auction['id']} ended, sending email to {auction['winner']}")
                # You can use BackgroundTasks or an async function to send email
                background_tasks.add_task(send_winner_email, auction["winner"])

# Set up APScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(check_auctions, 'interval', seconds=60)  # Check every minute
scheduler.start()

# Shut down the scheduler when exiting the app
