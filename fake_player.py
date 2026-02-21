import time
import random
import argparse
import multiplayer
from multiplayer import GameClient

def run_fake_player(host, port, name):
    client = GameClient(host, port, name)
    print(f"Connecting to {host}:{port} as {name}...")
    if not client.connect():
        print("Failed to connect!")
        return
        
    print("Connected! Simulating player...")
    
    x = 100
    y = 300
    rot = 0
    velocity = 0
    jump_velocity = 12
    gravity = 0.5 * 60
    fps = 60
    tick_time = 1 / fps
    
    alive = True
    score = 0
    
    # Wait for welcome state
    timeout = 10
    start_t = time.time()
    while client.client_id is None:
        time.sleep(0.1)
        if time.time() - start_t > timeout:
            print("Timeout waiting for welcome.")
            return

    try:
        while True:
            # Sleep to match ~60 FPS update rate locally
            time.sleep(tick_time)
            
            if client.connection_error or client.was_kicked:
                print("Disconnected from server.")
                break
                
            if client.should_start_game:
                client.should_start_game = False
                print("Game Started! Resetting state...")
                alive = True
                score = 0
                y = 300
                velocity = 0
                x = 100
                
            if alive:
                # Randomly jump
                if random.random() < 0.02:
                    velocity = -jump_velocity
                    
                velocity += gravity * tick_time
                y += velocity * tick_time * 60
                rot = max(min(velocity * -2.5, 30), -90)
                
                # Keep within bounds vaguely, or let it die if it falls too far
                if y > 600:
                    y -= 600 # Wrap around or die? Let's say die.
                    alive = False
                    print(f"{name} died! Pressing Ready...")
                    client.send_ready(True)
                if y < 0:
                    y = 0
                    velocity = 0
                    
                # Simulating points
                if random.random() < 0.05:
                     score += 1
                     
            client.send_update(x, y, rot, alive, score)
            
    except KeyboardInterrupt:
        print("Stopping fake player.")
        client.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=multiplayer.DEFAULT_PORT)
    parser.add_argument("--name", default=f"Bot_{random.randint(100,999)}")
    args = parser.parse_args()
    
    run_fake_player(args.host, args.port, args.name)
