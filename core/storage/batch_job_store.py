"""
Persistence layer for batch job results.
"""
from typing import Dict, Optional, Any
import json
import os
from datetime import datetime, timedelta, timezone
import uuid
from pathlib import Path

# Ensure the data directory exists
DATA_DIR = Path("data/batch_jobs")
DATA_DIR.mkdir(parents=True, exist_ok=True)

class BatchJobStore:
    """
    Simple file-based storage for batch job results.
    
    In production, consider using a database like PostgreSQL or MongoDB.
    """
    
    @staticmethod
    def _get_job_path(job_id: str) -> Path:
        """Get the file path for a job."""
        return DATA_DIR / f"{job_id}.json"
    
    @classmethod
    async def save_job(cls, job_id: str, data: Dict[str, Any]) -> None:
        """
        Save job data to storage.
        
        Args:
            job_id: Unique job identifier
            data: Job data to store
        """
        file_path = cls._get_job_path(job_id)
        with open(file_path, 'w') as f:
            json.dump({
                'job_id': job_id,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'data': data
            }, f, indent=2)
    
    @classmethod
    async def get_job(cls, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve job data from storage.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Optional[Dict]: Job data if found, None otherwise
        """
        file_path = cls._get_job_path(job_id)
        if not file_path.exists():
            return None
            
        with open(file_path, 'r') as f:
            return json.load(f)
    
    @classmethod
    async def cleanup_old_jobs(cls, max_age_days: int = 7) -> int:
        """
        Remove job files older than the specified number of days.
        
        Args:
            max_age_days: Maximum age in days to keep job files
            
        Returns:
            int: Number of jobs deleted
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        deleted = 0
        
        for file_path in DATA_DIR.glob('*.json'):
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime, tz=datetime.timezone.utc)
            if file_mtime < cutoff_time:
                file_path.unlink()
                deleted += 1
                
        return deleted

# Global instance
job_store = BatchJobStore()
