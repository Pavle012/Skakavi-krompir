import os
import sys

# Ensure we're in the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Add the root directory to sys.path so we can import shared and kivy_game
sys.path.insert(0, os.getcwd())

from kivy_game.main import SkakaviApp

if __name__ == '__main__':
    SkakaviApp().run()
