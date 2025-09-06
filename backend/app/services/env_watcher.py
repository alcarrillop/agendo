"""
Environment File Watcher Service.
Monitors .env file changes and triggers webhook updates automatically.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Optional, Callable, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.core.config import get_settings
from app.services.webhook_manager import webhook_manager
from app.database.connection import get_async_db

logger = logging.getLogger(__name__)


class EnvFileHandler(FileSystemEventHandler):
    """Handles .env file change events."""
    
    def __init__(self, callback: Callable):
        self.callback = callback
        self.env_file_path = Path(__file__).parent.parent.parent / ".env"
        logger.info(f"👀 Watching .env file: {self.env_file_path}")
    
    def on_modified(self, event):
        """Called when a file is modified."""
        if event.is_directory:
            return
        
        # Check if the modified file is our .env file
        if Path(event.src_path).resolve() == self.env_file_path.resolve():
            logger.info("📝 .env file changed - triggering webhook update")
            asyncio.create_task(self.callback())


class EnvWatcher:
    """
    Watches the .env file for changes and triggers webhook updates.
    """
    
    def __init__(self):
        self.observer: Optional[Observer] = None
        self.is_running = False
        self.last_webhook_url = None
    
    async def start_watching(self):
        """Start watching the .env file for changes."""
        try:
            if self.is_running:
                logger.warning("⚠️  EnvWatcher is already running")
                return
            
            # Get the directory containing the .env file
            env_dir = Path(__file__).parent.parent.parent
            
            if not (env_dir / ".env").exists():
                logger.warning(f"⚠️  .env file not found at {env_dir / '.env'}")
                return
            
            # Create file handler
            event_handler = EnvFileHandler(self._on_env_changed)
            
            # Create observer
            self.observer = Observer()
            self.observer.schedule(event_handler, str(env_dir), recursive=False)
            
            # Start observer
            self.observer.start()
            self.is_running = True
            
            # Store initial webhook URL
            settings = get_settings()
            self.last_webhook_url = settings.WEBHOOK_BASE_URL
            
            logger.info("✅ EnvWatcher started successfully")
            
        except Exception as e:
            logger.error(f"❌ Error starting EnvWatcher: {e}")
    
    async def stop_watching(self):
        """Stop watching the .env file."""
        try:
            if self.observer and self.is_running:
                self.observer.stop()
                self.observer.join()
                self.is_running = False
                logger.info("🛑 EnvWatcher stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping EnvWatcher: {e}")
    
    async def _on_env_changed(self):
        """Called when .env file changes."""
        try:
            logger.info("🔄 Processing .env file changes...")
            
            # Wait a bit for file to be fully written
            await asyncio.sleep(1)
            
            # Reload settings (this might require restarting the app in some cases)
            # For now, we'll just check if WEBHOOK_BASE_URL changed
            new_settings = get_settings()
            new_webhook_url = new_settings.WEBHOOK_BASE_URL
            
            if new_webhook_url != self.last_webhook_url:
                logger.info(f"🔗 Webhook URL changed: {self.last_webhook_url} → {new_webhook_url}")
                self.last_webhook_url = new_webhook_url
                
                # Update webhooks
                async for db in get_async_db():
                    await webhook_manager.on_settings_change(db)
                    break
                
                logger.info("✅ Webhooks updated after .env change")
            else:
                logger.info("ℹ️  .env changed but WEBHOOK_BASE_URL unchanged")
            
        except Exception as e:
            logger.error(f"❌ Error processing .env changes: {e}")


# Global env watcher instance
env_watcher = EnvWatcher()


async def start_env_watcher():
    """Start the environment file watcher."""
    await env_watcher.start_watching()


async def stop_env_watcher():
    """Stop the environment file watcher."""
    await env_watcher.stop_watching()
