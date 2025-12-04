#!/usr/bin/env python3
"""
Example Cleanup Script
Demonstrates automated cleanup operations using the automation toolkit
"""

import sys
from pathlib import Path
from automation_toolkit import AutomationLogger, FileManager, SystemOperations
import json
import argparse

def run_daily_cleanup(target_dir: str, log_output: bool = True) -> dict:
    """
    Execute daily cleanup operations on target directory
    
    Operations:
    1. Remove files older than 30 days
    2. Clean up empty directories
    3. Organize remaining files by extension
    4. Generate cleanup report
    """
    
    # Initialize logger
    logger_instance = AutomationLogger()
    logger = logger_instance.get_logger()
    
    logger.info("="*80)
    logger.info(f"Daily Cleanup Started - Target: {target_dir}")
    logger.info("="*80)
    
    # Verify target exists
    target_path = Path(target_dir)
    if not target_path.exists():
        logger.error(f"Target directory does not exist: {target_dir}")
        return {'success': False, 'error': 'Directory not found'}
    
    # Initialize file manager
    file_mgr = FileManager(logger)
    sys_ops = SystemOperations(logger)
    
    results = {
        'success': True,
        'timestamp': str(Path.cwd()),
        'operations': {}
    }
    
    try:
        # Operation 1: Cleanup old files (older than 30 days)
        logger.info("Starting old file cleanup...")
        cleanup_result = file_mgr.cleanup_old_files(target_dir, days=30)
        results['operations']['old_file_cleanup'] = cleanup_result
        
        # Operation 2: Remove empty directories
        logger.info("Starting empty directory cleanup...")
        empty_dir_result = file_mgr.cleanup_empty_dirs(target_dir, recursive=True)
        results['operations']['empty_dir_cleanup'] = empty_dir_result
        
        # Operation 3: Check system health
        logger.info("Checking system health...")
        disk_usage = sys_ops.check_disk_usage()
        results['operations']['disk_usage'] = disk_usage
        
        # Generate report
        logger.info("Generating cleanup report...")
        if log_output:
            print("\n" + "="*80)
            print("CLEANUP REPORT")
            print("="*80)
            print(f"Old files deleted: {cleanup_result['deleted']}")
            print(f"Errors during deletion: {cleanup_result['errors']}")
            print(f"Empty directories removed: {empty_dir_result['removed']}")
            print(f"Errors during removal: {empty_dir_result['errors']}")
            if disk_usage['success']:
                print(f"Disk usage: {disk_usage['percent']:.1f}% ({disk_usage['used']:.1f}GB/{disk_usage['total']:.1f}GB)")
            print("="*80 + "\n")
        
        logger.info("Daily cleanup completed successfully")
        
    except Exception as e:
        logger.error(f"Cleanup operation failed: {e}")
        results['success'] = False
        results['error'] = str(e)
    
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Daily cleanup automation script')
    parser.add_argument('--target', '-t', type=str, default='/tmp', help='Target directory for cleanup')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress report output')
    
    args = parser.parse_args()
    
    result = run_daily_cleanup(args.target, log_output=not args.quiet)
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)
