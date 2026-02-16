"""
Locivox GUI Application Entry Point
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from src.gui.main_window import MainWindow
from src.gui_controller import GUIController


def setup_logging(config: dict):
    """Configure logging for GUI application"""
    # Get log level from config (default to INFO)
    log_level_str = config.get('logging', {}).get('level', 'INFO').upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    # Get log file path from config
    log_file = config.get('logging', {}).get('file', 'locivox_gui.log')
    
    # Create formatters
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # File handler (with error handling)
    handlers = [console_handler]
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
        print(f"Logging to file: {log_file}")
    except Exception as e:
        print(f"Warning: Could not create log file {log_file}: {e}")
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    # Set all locivox loggers to same level
    for logger_name in ['locivox', 'locivox.gui', 'locivox.gui.controller', 
                        'locivox.gui.worker', 'locivox.gui.audio_capture']:
        logging.getLogger(logger_name).setLevel(log_level)
    
    logging.info(f"Logging initialized at {log_level_str} level")


def exception_hook(exctype, value, tb):
    """Global exception handler for uncaught exceptions"""
    import traceback
    logger = logging.getLogger('locivox.gui.main')
    
    # Log the exception
    logger.critical("Uncaught exception:", exc_info=(exctype, value, tb))
    
    # Print to console too
    print("=" * 80)
    print("CRITICAL ERROR - Application crashed!")
    print("=" * 80)
    traceback.print_exception(exctype, value, tb)
    print("=" * 80)
    print("Please report this error with the log file: locivox_gui.log")
    print("=" * 80)
    
    # Show error dialog
    try:
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Critical Error")
        msg.setText("Application crashed unexpectedly")
        msg.setDetailedText(''.join(traceback.format_exception(exctype, value, tb)))
        msg.setInformativeText("Please check locivox_gui.log for details")
        msg.exec()
    except:
        pass  # If GUI is dead, just print


def main():
    """Main entry point for GUI application"""
    # Load config first
    from src.utils import load_config
    config = load_config()
    
    # Setup logging with config
    setup_logging(config)
    logger = logging.getLogger('locivox.gui.main')
    logger.info("Starting Locivox GUI")
    
    # Install global exception handler
    sys.excepthook = exception_hook
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Locivox")
    app.setOrganizationName("Locivox")
    
    # Enable high DPI scaling
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    try:
        # Create controller
        controller = GUIController()
        
        # Create main window (pass config and controller)
        window = MainWindow(config, controller)
        
        # Connect controller to window
        window.start_requested.connect(controller.start_recording)
        window.stop_requested.connect(controller.stop_recording)
        window.stop_requested.connect(window.transcription.stop_cursor_blink)  # Stop cursor
        window.mic_changed.connect(controller.set_microphone_device)
        
        # Connect controller signals to window
        controller.transcription_ready.connect(window.append_transcription)
        controller.status_changed.connect(window.update_status)
        controller.error_occurred.connect(
            lambda msg: QMessageBox.critical(window, "Error", msg)
        )
        controller.vocabulary_correction.connect(
            lambda orig, corr: window.transcription.replace_text(orig, corr)
        )
        
        # Connect recording_actually_started to controls widget
        controller.recording_actually_started.connect(window.controls.start_recording)
        controller.start_failed.connect(window.controls.on_start_failed)
        
        # Start cursor blinking when recording starts
        controller.recording_actually_started.connect(window.transcription.start_cursor_blink)
        
        # Connect model/device changes from controls
        window.controls.model_changed.connect(
            lambda model: controller.update_config('model.size', model)
        )
        window.controls.device_changed.connect(
            lambda device: controller.update_config('model.device', device)
        )
        
        # Log initial state
        logger.info(f"Selected microphone: {window.controls.get_selected_mic_index()}")
        logger.info(f"Selected model: {window.controls.get_selected_model()}")
        logger.info(f"Selected device: {window.controls.get_selected_device()}")
        
        # Show window
        window.show()
        
        # Run application
        logger.info("GUI ready")
        exit_code = app.exec()
        
        # Cleanup
        controller.cleanup()
        
        return exit_code
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        QMessageBox.critical(
            None,
            "Fatal Error",
            f"Failed to start application:\n\n{e}"
        )
        return 1


if __name__ == '__main__':
    sys.exit(main())
