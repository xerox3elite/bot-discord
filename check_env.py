#!/usr/bin/env python3
# Basic environment check for Render
import os
import sys

print("🔍 Arsenal Environment Check")
print("Python:", sys.version)
print("DISCORD_TOKEN:", "✅ Present" if os.getenv('DISCORD_TOKEN') else "❌ Missing")
print("Environment check completed")
