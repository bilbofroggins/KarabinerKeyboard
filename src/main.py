import logging
import os
import sys
import traceback
import warnings

# Set up logging to file for debugging
log_dir = os.path.expanduser('~/.config/karabiner_keyboard')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'app.log')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Starting KarabinerKeyboard")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Platform: {sys.platform}")
        
        import platform
        logger.info(f"Machine architecture: {platform.machine()}")
        
        warnings.simplefilter('always', DeprecationWarning)
        
        logger.info("Loading YAML config...")
        from src.logic.yaml_config import YAML_Config
        YAML_Config()
        
        logger.info("Setting enabled flag...")
        from src.logic.merge_kb_config import set_enabled_flag
        set_enabled_flag()
        
        logger.info("Initializing raylib/window...")
        from window import MyApp
        app = MyApp()
        
        # Track app launch (non-blocking, runs in background)
        logger.info("Sending analytics...")
        from src.analytics import track_event
        track_event("app_launch")
        
        logger.info("Starting main loop...")
        app.run()
        
        logger.info("Application closed normally")
    except Exception as e:
        logger.error(f"Application crashed: {e}")
        logger.error(traceback.format_exc())
        raise

if __name__ == '__main__':
    main()
