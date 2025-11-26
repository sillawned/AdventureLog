#!/usr/bin/env python3
"""
AdventureLog Frontend Build System

Uses Jinja2 to build a single-file HTML application from modular templates.
Supports watch mode for development with auto-rebuild on file changes.
"""

import os
import sys
import time
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


# Configuration
TEMPLATES_DIR = Path(__file__).parent / "templates"
OUTPUT_DIR = Path(__file__).parent / "dist"
OUTPUT_FILE = OUTPUT_DIR / "index.html"
STATIC_SRC = TEMPLATES_DIR / "static"
STATIC_DEST = OUTPUT_DIR / "static"
API_URL = os.getenv("API_URL", "http://localhost:8000/api")


def build_template():
    """Build the final index.html from Jinja2 templates."""
    try:
        # Create Jinja2 environment
        env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False  # Disable autoescape to prevent escaping $ in JavaScript
        )
        
        # Load base template
        template = env.get_template("base.html")
        
        # Render with context variables
        output = template.render(
            title="AdventureLog - Track Your Adventures",
            api_url=API_URL,
            version="2.0.0"
        )
        
        # Ensure output directory exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Copy static files
        if STATIC_SRC.exists():
            if STATIC_DEST.exists():
                shutil.rmtree(STATIC_DEST)
            shutil.copytree(STATIC_SRC, STATIC_DEST)
        
        # Write output
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(output)
        
        print(f"✓ Built {OUTPUT_FILE} ({len(output)} bytes)")
        return True
        
    except Exception as e:
        print(f"✗ Build failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def watch_mode():
    """Watch for file changes and rebuild automatically."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("watchdog not installed. Install with: pip install watchdog")
        print("Running single build instead...")
        return build_template()
    
    class TemplateChangeHandler(FileSystemEventHandler):
        def __init__(self):
            self.last_build = 0
            
        def on_modified(self, event):
            # Debounce: only rebuild if 0.5s passed since last build
            if time.time() - self.last_build < 0.5:
                return
            
            if event.is_directory:
                return
            
            # Only rebuild for template files
            if not event.src_path.endswith(('.html', '.css', '.js')):
                return
            
            print(f"\n→ Change detected: {event.src_path}")
            if build_template():
                self.last_build = time.time()
    
    print("👀 Watch mode enabled. Press Ctrl+C to stop.\n")
    
    # Initial build
    build_template()
    
    # Set up file watcher
    event_handler = TemplateChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, str(TEMPLATES_DIR), recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n✓ Stopping watch mode...")
        observer.stop()
    
    observer.join()


def main():
    """Main entry point."""
    print("🌍 AdventureLog Frontend Builder\n")
    
    # Check if templates directory exists
    if not TEMPLATES_DIR.exists():
        print(f"✗ Templates directory not found: {TEMPLATES_DIR}")
        sys.exit(1)
    
    # Check for watch mode flag
    if "--watch" in sys.argv or "-w" in sys.argv:
        watch_mode()
    else:
        # Single build
        success = build_template()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
