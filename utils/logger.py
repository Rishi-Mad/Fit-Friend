"""
Logging utilities for AI Fitness Coach
Comprehensive logging system with different levels and handlers
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional
import json
from functools import wraps
import time

class FitnessCoachLogger:
    """Custom logger for AI Fitness Coach"""
    
    def __init__(self, name: str = 'fitness_coach', level: str = 'INFO'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup logging handlers"""
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        file_handler = logging.FileHandler('logs/fitness_coach.log')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        # Error file handler
        error_handler = logging.FileHandler('logs/errors.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(message, extra=kwargs)
    
    def log_analysis(self, analysis_data: dict):
        """Log analysis results"""
        self.info("Analysis completed", analysis_data=analysis_data)
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics"""
        self.info(f"Performance: {operation} took {duration:.2f}s", 
                 operation=operation, duration=duration, **kwargs)
    
    def log_error_with_context(self, error: Exception, context: dict = None):
        """Log error with additional context"""
        error_data = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }
        self.error(f"Error occurred: {error}", error_data=error_data)

# Global logger instance
logger = FitnessCoachLogger()

def log_function_call(func):
    """Decorator to log function calls"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.debug(f"Calling {func.__name__}", 
                    args_count=len(args), kwargs_count=len(kwargs))
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f"Function {func.__name__} completed in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Function {func.__name__} failed after {duration:.2f}s", 
                        error=str(e))
            raise
    
    return wrapper

def log_analysis_session(session_id: str, exercise_type: str, duration: float, 
                        frame_count: int, score: float):
    """Log analysis session data"""
    session_data = {
        'session_id': session_id,
        'exercise_type': exercise_type,
        'duration': duration,
        'frame_count': frame_count,
        'score': score,
        'timestamp': datetime.now().isoformat()
    }
    logger.info("Analysis session completed", session_data=session_data)

class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    def __init__(self):
        self.metrics = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation"""
        self.metrics[operation] = {'start': time.time()}
    
    def end_timer(self, operation: str) -> float:
        """End timing an operation and return duration"""
        if operation in self.metrics:
            duration = time.time() - self.metrics[operation]['start']
            logger.log_performance(operation, duration)
            del self.metrics[operation]
            return duration
        return 0.0
    
    def log_memory_usage(self):
        """Log current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            logger.info("Memory usage", 
                       memory_mb=memory_info.rss / 1024 / 1024)
        except ImportError:
            logger.debug("psutil not available for memory monitoring")

# Global performance monitor
performance_monitor = PerformanceMonitor() 