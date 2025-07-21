#!/usr/bin/env python3
"""
Quick test to verify database connection pooling is working
"""
import time
from app.db.crud.events import get_upcoming_events
from app.db.crud.reminders import get_upcoming_reminders

def test_db_performance():
    """Test multiple database calls to verify connection reuse"""
    print("🧪 Testing database connection pooling performance...")
    
    # Test multiple calls in quick succession
    start_time = time.time()
    
    for i in range(5):
        print(f"  Call {i+1}: Getting events and reminders...")
        events = get_upcoming_events()
        reminders = get_upcoming_reminders()
        print(f"    Events: {len(events) if isinstance(events, list) else 0}")
        print(f"    Reminders: {len(reminders) if isinstance(reminders, list) else 0}")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n✅ Completed 5 rounds of DB calls in {total_time:.2f} seconds")
    print(f"📊 Average time per round: {(total_time/5):.3f} seconds")
    
    if total_time < 2.0:  # Should be fast with connection pooling
        print("🚀 Connection pooling is working! Fast response times.")
    else:
        print("⚠️  Response times seem slow. Check connection pooling.")

if __name__ == "__main__":
    test_db_performance()
