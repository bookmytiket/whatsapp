import os
import requests
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from bridge import WhatsAppBridge
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="BookMyTicket WhatsApp Bridge")

# Initialize bridge as a singleton
bridge = None

@app.on_event("startup")
def startup_event():
    global bridge
    print("Starting WhatsApp Bridge...")
    bridge = WhatsAppBridge()
    # Note: On first run, you must scan the QR code.
    # We don't block here, but send_message will fail until logged in.

@app.on_event("shutdown")
def shutdown_event():
    if bridge:
        bridge.quit()

def process_webhook(payload: dict):
    global bridge
    try:
        # Extract data from Supabase Webhook payload
        record = payload.get("record", {})
        table = payload.get("table")
        
        # Determine notification type
        phone = record.get("phone") or record.get("customer_details", {}).get("phone")
        if not phone:
            print("No phone number found in record")
            return

        # Simple number cleanup
        phone = "".join(filter(str.isdigit, str(phone)))
        if len(phone) == 10:
            phone = "91" + phone # Default to India if 10 digits

        message = ""
        
        if table == "bookings":
            # Fetch event name from events table
            event_name = "your event"
            event_id = record.get("event_id")
            if event_id:
                try:
                    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
                    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
                    res = requests.get(
                        f"{supabase_url}/rest/v1/events?id=eq.{event_id}&select=title",
                        headers={
                            "apikey": supabase_key,
                            "Authorization": f"Bearer {supabase_key}"
                        }
                    )
                    event_data = res.json()
                    if event_data and len(event_data) > 0:
                        event_name = event_data[0].get("title")
                except Exception as ex:
                    print(f"Failed to fetch event name: {ex}")

            message = f"🎉 *Booking Confirmed!*\n\nEvent: {event_name}\nDate: {record.get('date', 'N/A')}\nBooking ID: {record.get('id', 'N/A')}\n\nThank you for booking with us!"
        
        elif table == "profiles" or table == "users":
            message = f"Welcome to BookMyTicket! 🎉\n\nYour account has been successfully created."
        
        if message and bridge:
            bridge.send_message(phone, message)
            
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")

@app.post("/hook/booking")
async def handle_booking_hook(request: Request, background_tasks: BackgroundTasks):
    # Verify secure header if you set one in Supabase (e.g., x-webhook-secret)
    # if request.headers.get("x-webhook-secret") != os.getenv("WEBHOOK_SECRET"):
    #     raise HTTPException(status_code=401, detail="Unauthorized")

    payload = await request.json()
    print(f"Received webhook for table: {payload.get('table')}")
    
    # Process in background to avoid blocking Supabase
    background_tasks.add_task(process_webhook, payload)
    
    return {"status": "accepted"}

@app.get("/status")
def get_status():
    return {"status": "running", "logged_in": bridge.is_logged_in() if bridge else False}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
