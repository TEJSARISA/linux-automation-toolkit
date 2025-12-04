#!/usr/bin/env python3
"""
Linux Automation Toolkit
Comprehensive Python-based automation for Linux system operations
Features: File management, cleanup, permissions, logging, monitoring
"""

import os
import sys
import logging
import subprocess
import json
import time
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

class AutomationLogger:
    """Centralized logging system for automation toolkit"""
    
    def __init__(self, log_dir: str = "/var/log/automation"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger('automation_toolkit')
        self.logger.setLevel(logging.DEBUG)
        
        fh = logging.FileHandler(self.log_dir / f"automation_{datetime.now().strftime('%Y%m%d')}.log")
        fh.setLevel(logging.DEBUG)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def get_logger(self):
        return self.logger

print("Logger configured")

# ============================================================================
# FILE MANAGEMENT MODULE
# ============================================================================

class FileManager:
    """File management and organization automation"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def organize_by_extension(self, source_dir: str) -> Dict:
        """Organize files by extension into subdirectories"""
        self.logger.info(f"Starting file organization in {source_dir}")
        source_path = Path(source_dir)
        results = {'organized': 0, 'errors': 0, 'details': []}
        
        if not source_path.exists():
            self.logger.error(f"Source directory does not exist: {source_dir}")
            return results
        
        try:
            for file_path in source_path.glob('*'):
                if file_path.is_file():
                    ext = file_path.suffix or 'no_extension'
                    ext_dir = source_path / ext.lstrip('.')
                    ext_dir.mkdir(exist_ok=True)
                    
                    try:
                        shutil.move(str(file_path), str(ext_dir / file_path.name))
                        results['organized'] += 1
                        self.logger.info(f"Organized: {file_path.name} -> {ext}")
                        results['details'].append(f"Moved {file_path.name} to {ext}/")
                    except Exception as e:
                        results['errors'] += 1
                        self.logger.error(f"Failed to organize {file_path.name}: {e}")
        except Exception as e:
            self.logger.error(f"File organization failed: {e}")
            results['errors'] += 1
        
        self.logger.info(f"File organization complete: {results['organized']} organized, {results['errors']} errors")
        return results
    
    def cleanup_empty_dirs(self, target_dir: str, recursive: bool = True) -> Dict:
        """Remove empty directories"""
        self.logger.info(f"Cleaning empty directories in {target_dir}")
        target_path = Path(target_dir)
        results = {'removed': 0, 'errors': 0}
        
        if not target_path.exists():
            self.logger.error(f"Target directory does not exist: {target_dir}")
            return results
        
        try:
            if recursive:
                for dir_path in sorted(target_path.rglob('.'), reverse=True):
                    if dir_path.is_dir() and not list(dir_path.iterdir()):
                        try:
                            dir_path.rmdir()
                            results['removed'] += 1
                            self.logger.info(f"Removed empty directory: {dir_path}")
                        except Exception as e:
                            results['errors'] += 1
                            self.logger.warning(f"Could not remove {dir_path}: {e}")
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            results['errors'] += 1
        
        self.logger.info(f"Cleanup complete: {results['removed']} directories removed")
        return results
    
    def cleanup_old_files(self, target_dir: str, days: int = 30) -> Dict:
        """Delete files older than specified days"""
        self.logger.info(f"Cleaning files older than {days} days in {target_dir}")
        target_path = Path(target_dir)
        results = {'deleted': 0, 'errors': 0, 'details': []}
        cutoff_time = time.time() - (days * 86400)
        
        if not target_path.exists():
            self.logger.error(f"Target directory does not exist: {target_dir}")
            return results
        
        try:
            for file_path in target_path.rglob('*'):
                if file_path.is_file():
                    file_time = file_path.stat().st_mtime
                    if file_time < cutoff_time:
                        try:
                            file_path.unlink()
                            results['deleted'] += 1
                            self.logger.info(f"Deleted old file: {file_path}")
                            results['details'].append(f"Deleted {file_path.name}")
                        except Exception as e:
                            results['errors'] += 1
                            self.logger.warning(f"Could not delete {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Old file cleanup failed: {e}")
            results['errors'] += 1
        
        self.logger.info(f"Old file cleanup complete: {results['deleted']} deleted, {results['errors']} errors")
        return results
    
    def change_permissions(self, target_path: str, mode: int, recursive: bool = False) -> Dict:
        """Change file/directory permissions"""
        self.logger.info(f"Changing permissions for {target_path} to {oct(mode)}")
        target = Path(target_path)
        results = {'changed': 0, 'errors': 0}
        
        if not target.exists():
            self.logger.error(f"Target does not exist: {target_path}")
            return results
        
        try:
            if recursive and target.is_dir():
                for item in target.rglob('*'):
                    try:
                        item.chmod(mode)
                        results['changed'] += 1
                        self.logger.debug(f"Changed permissions: {item}")
                    except Exception as e:
                        results['errors'] += 1
                        self.logger.warning(f"Could not change {item}: {e}")
            else:
                target.chmod(mode)
                results['changed'] += 1
                self.logger.info(f"Changed permissions for {target_path}")
        except Exception as e:
            self.logger.error(f"Permission change failed: {e}")
            results['errors'] += 1
        
        return results
    
    def find_large_files(self, target_dir: str, size_mb: int = 100) -> List[Dict]:
        """Find files larger than specified size"""
        self.logger.info(f"Searching for files larger than {size_mb}MB in {target_dir}")
        target_path = Path(target_dir)
        large_files = []
        size_bytes = size_mb * 1024 * 1024
        
        try:
            for file_path in target_path.rglob('*'):
                if file_path.is_file():
                    file_size = file_path.stat().st_size
                    if file_size > size_bytes:
                        large_files.append({
                            'path': str(file_path),
                            'size_mb': round(file_size / (1024 * 1024), 2)
                        })
                        self.logger.info(f"Found large file: {file_path.name} ({file_size / (1024 * 1024):.2f}MB)")
        except Exception as e:
            self.logger.error(f"Failed to search for large files: {e}")
        
        return large_files

# ============================================================================
# SYSTEM OPERATIONS MODULE
# ============================================================================

class SystemOperations:
    """System-level automation operations"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def execute_command(self, command: str, check: bool = True) -> Dict:
        """Execute shell command with error handling"""
        self.logger.info(f"Executing command: {command}")
        result = {'success': False, 'output': '', 'error': '', 'return_code': -1}
        
        try:
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=check
            )
            result['success'] = True
            result['output'] = process.stdout
            result['return_code'] = process.returncode
            self.logger.info(f"Command executed successfully: {command}")
        except subprocess.CalledProcessError as e:
            result['error'] = e.stderr or str(e)
            result['return_code'] = e.returncode
            self.logger.error(f"Command failed: {command}. Error: {result['error']}")
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Command execution error: {command}. Error: {result['error']}")
        
        return result
    
    def check_disk_usage(self, path: str = '/') -> Dict:
        """Check disk usage statistics"""
        self.logger.info(f"Checking disk usage for {path}")
        result = {'total': 0, 'used': 0, 'free': 0, 'percent': 0, 'success': False}
        
        try:
            import shutil
            stat = shutil.disk_usage(path)
            result['total'] = stat.total / (1024**3)  # Convert to GB
            result['used'] = stat.used / (1024**3)
            result['free'] = stat.free / (1024**3)
            result['percent'] = (stat.used / stat.total) * 100
            result['success'] = True
            self.logger.info(f"Disk usage: {result['percent']:.1f}% used ({result['used']:.1f}GB/{result['total']:.1f}GB)")
        except Exception as e:
            self.logger.error(f"Failed to check disk usage: {e}")
        
        return result
    
    def get_process_info(self, process_name: str) -> Dict:
        """Get information about running processes"""
        self.logger.info(f"Checking process: {process_name}")
        cmd_result = self.execute_command(f"ps aux | grep {process_name}", check=False)
        
        result = {'found': False, 'processes': [], 'error': cmd_result.get('error', '')}
        
        if cmd_result['success'] and cmd_result['output']:
            result['found'] = True
            result['processes'] = [line for line in cmd_result['output'].split('\n') if line.strip()]
            self.logger.info(f"Found {len(result['processes'])} instances of {process_name}")
        
        return result
    
    def generate_report(self, file_manager: 'FileManager') -> Dict:
        """Generate comprehensive system automation report"""
        self.logger.info("Generating system automation report")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'disk_usage': self.check_disk_usage(),
            'system_info': {
                'hostname': os.uname()[1],
                'system': os.uname()[0]
            },
            'operations': []
        }
        
        self.logger.info("System automation report generated")
        return report

print("System operations module loaded")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    # Initialize logger
    logger_instance = AutomationLogger()
    logger = logger_instance.get_logger()
    
    logger.info("="*80)
    logger.info("Linux Automation Toolkit Started")
    logger.info("="*80)
    
    # Initialize modules
    file_mgr = FileManager(logger)
    sys_ops = SystemOperations(logger)
    
    logger.info("All modules initialized successfully")
    logger.info("Ready for automation tasks")
    
    # Example: Check system status
    disk_status = sys_ops.check_disk_usage()
    if disk_status['success']:
        logger.info(f"System Health: Disk usage at {disk_status['percent']:.1f}%")
    
    logger.info("="*80)
    logger.info("Linux Automation Toolkit Ready")
    logger.info("="*80)
