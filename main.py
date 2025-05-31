#!/usr/bin/env python3
"""
Main entry point for the game application.
"""
import sys
import os

# Add the menu directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'menu'))

from menu import Menu

if __name__ == "__main__":
    menu = Menu()
    menu.executer()