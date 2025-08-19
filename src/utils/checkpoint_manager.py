import json
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

class CheckpointManager:
    def __init__(self, config: Any, logger: Any):
        self.config = config
        self.logger = logger
        self.checkpoint_dir = Path(self.config.get('output_config', {}).get('checkpoint_dir', 'checkpoints'))
        self.session_id = None

    async def initialize_session(self, target_size: int, quality_threshold: float, resume: bool) -> Tuple[str, int]:
        if resume:
            latest_session = await self.get_latest_session()
            if latest_session:
                self.session_id = latest_session['session_id']
                output_file = latest_session['output_file']
                current_count = latest_session['current_count']
                return output_file, current_count

        self.session_id = f"session_{time.strftime('%Y%m%d_%H%M%S')}_{int(time.time() * 1000) % 1000}"
        output_file = f"{self.session_id}.jsonl"
        
        session_data = {
            "session_id": self.session_id,
            "start_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            "output_file": output_file,
            "target_size": target_size,
            "quality_threshold": quality_threshold,
            "current_count": 0,
            "completed": False
        }
        
        await self._save_session_data(session_data)
        return output_file, 0

    async def add_qa_pair(self, qa_pair: Dict[str, Any]) -> bool:
        session_data = await self._load_session_data()
        if not session_data:
            return False

        output_path = self.checkpoint_dir / session_data['output_file']
        with open(output_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(qa_pair) + '\n')

        session_data['current_count'] += 1
        await self._save_session_data(session_data)

        if session_data['current_count'] >= session_data['target_size']:
            session_data['completed'] = True
            await self._save_session_data(session_data)
            return True
        return False

    def get_progress(self) -> Dict[str, Any]:
        session_data = self._load_session_data_sync()
        if not session_data:
            return {}
        return {
            "current_count": session_data.get('current_count', 0),
            "target_size": session_data.get('target_size', 0),
            "progress_percentage": (session_data.get('current_count', 0) / session_data.get('target_size', 1)) * 100
        }

    async def handle_interruption(self):
        self.logger.info("Handling interruption. Saving final checkpoint.")
        # Final save is handled by the main loop, this is a placeholder

    async def get_latest_session(self) -> Optional[Dict[str, Any]]:
        sessions = await self.list_sessions()
        incomplete_sessions = [s for s in sessions if not s['completed']]
        if incomplete_sessions:
            return max(incomplete_sessions, key=lambda s: s['start_time'])
        return None

    async def list_sessions(self) -> List[Dict[str, Any]]:
        sessions = []
        for session_file in self.checkpoint_dir.glob("*.json"):
            if session_file.name.startswith("session_"):
                with open(session_file, 'r', encoding='utf-8') as f:
                    sessions.append(json.load(f))
        return sessions

    async def cleanup_old_sessions(self, keep_days: int):
        cutoff = time.time() - (keep_days * 86400)
        for session_file in self.checkpoint_dir.glob("*.json"):
            if session_file.stat().st_mtime < cutoff:
                session_data = json.loads(session_file.read_text())
                if session_data.get('completed'):
                    output_file = self.checkpoint_dir / session_data['output_file']
                    if output_file.exists():
                        output_file.unlink()
                    session_file.unlink()

    async def _save_session_data(self, session_data: Dict[str, Any]):
        session_file = self.checkpoint_dir / f"{self.session_id}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=4)

    async def _load_session_data(self) -> Optional[Dict[str, Any]]:
        if not self.session_id:
            return None
        session_file = self.checkpoint_dir / f"{self.session_id}.json"
        if session_file.exists():
            with open(session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def _load_session_data_sync(self) -> Optional[Dict[str, Any]]:
        if not self.session_id:
            return None
        session_file = self.checkpoint_dir / f"{self.session_id}.json"
        if session_file.exists():
            with open(session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
