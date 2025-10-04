"""
Unit tests for configuration and logging setup.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_config, setup_logging, get_logger, DevelopmentConfig, ProductionConfig, TestingConfig


class TestConfiguration:
    """Test configuration loading and validation."""
    
    def test_development_config(self):
        """Test development configuration."""
        os.environ['FLASK_ENV'] = 'development'
        config = get_config()
        
        assert isinstance(config, DevelopmentConfig)
        assert config.DEBUG is True
        assert config.LOG_LEVEL == 'DEBUG'
        assert config.FLASK_ENV == 'development'
    
    def test_production_config(self):
        """Test production configuration with required values."""
        # Set required production environment variables
        os.environ['FLASK_ENV'] = 'production'
        os.environ['SECRET_KEY'] = 'a' * 32  # 32 character secret key
        os.environ['NASA_NEO_API_KEY'] = 'test_production_key'
        
        config = get_config()
        
        assert isinstance(config, ProductionConfig)
        assert config.DEBUG is False
        assert config.LOG_LEVEL == 'INFO'
        assert config.FLASK_ENV == 'production'
        assert len(config.SECRET_KEY) >= 32
        assert config.NASA_NEO_API_KEY == 'test_production_key'
    
    def test_testing_config(self):
        """Test testing configuration."""
        os.environ['FLASK_ENV'] = 'testing'
        config = get_config()
        
        assert isinstance(config, TestingConfig)
        assert config.TESTING is True
        assert config.DEBUG is True
        assert config.LOG_LEVEL == 'WARNING'
        assert config.FLASK_ENV == 'testing'
    
    def test_config_validation(self):
        """Test configuration validation."""
        os.environ['FLASK_ENV'] = 'development'
        os.environ['LOG_LEVEL'] = 'INVALID'
        
        with pytest.raises(ValueError, match="LOG_LEVEL must be one of"):
            get_config()
        
        # Clean up
        del os.environ['LOG_LEVEL']


class TestLogging:
    """Test logging configuration."""
    
    def test_logging_setup(self):
        """Test basic logging setup."""
        os.environ['FLASK_ENV'] = 'development'
        config = get_config()
        
        # Use temporary log file
        with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as tmp_log:
            log_file_path = tmp_log.name
        
        config.LOG_FILE = log_file_path
        
        # Setup logging
        setup_logging(config)
        
        # Get logger and test
        logger = get_logger(__name__)
        
        logger.info("Test log message")
        
        # Close all handlers to release file locks
        import logging
        for handler in logging.getLogger().handlers[:]:
            handler.close()
            logging.getLogger().removeHandler(handler)
        
        # Verify log file was created and contains message
        assert Path(log_file_path).exists()
        
        with open(log_file_path, 'r') as f:
            log_contents = f.read()
            assert "Test log message" in log_contents
        
        # Clean up
        try:
            os.unlink(log_file_path)
        except PermissionError:
            # On Windows, sometimes the file is still locked
            pass
    
    def test_log_levels(self):
        """Test different log levels."""
        os.environ['FLASK_ENV'] = 'development'
        config = get_config()
        config.LOG_LEVEL = 'WARNING'
        
        with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as tmp_log:
            log_file_path = tmp_log.name
        
        config.LOG_FILE = log_file_path
        
        setup_logging(config)
        logger = get_logger(__name__)
        
        # These should not appear in log (below WARNING level)
        logger.debug("Debug message")
        logger.info("Info message")
        
        # These should appear in log
        logger.warning("Warning message")
        logger.error("Error message")
        
        # Close handlers to release file locks
        import logging
        for handler in logging.getLogger().handlers[:]:
            handler.close()
            logging.getLogger().removeHandler(handler)
        
        with open(log_file_path, 'r') as f:
            log_contents = f.read()
            assert "Debug message" not in log_contents
            assert "Info message" not in log_contents
            assert "Warning message" in log_contents
            assert "Error message" in log_contents
        
        # Clean up
        try:
            os.unlink(log_file_path)
        except PermissionError:
            # On Windows, sometimes the file is still locked
            pass


if __name__ == '__main__':
    # Simple test runner for manual testing
    test_config = TestConfiguration()
    test_logging = TestLogging()
    
    print("Testing configuration loading...")
    test_config.test_development_config()
    test_config.test_testing_config()
    print("✓ Configuration tests passed")
    
    print("Testing logging setup...")
    test_logging.test_logging_setup()
    test_logging.test_log_levels()
    print("✓ Logging tests passed")
    
    print("All tests completed successfully!")