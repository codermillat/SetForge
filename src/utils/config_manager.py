import os
import yaml
from typing import Dict, Any, List, cast
class ConfigManager:
    def __init__(self, data: Any = None, config_path: str = 'config.yaml'):
        if data is None:
            self._data: Dict[str, Any] = self._load_config(config_path)
        elif isinstance(data, dict):
            self._data: Dict[str, Any] = data
        else:
            self._data: Dict[str, Any] = {}

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                loaded_yaml = yaml.safe_load(f)
                if isinstance(loaded_yaml, dict):
                    yaml_dict = cast(Dict[Any, Any], loaded_yaml)
                    return {str(k): v for k, v in yaml_dict.items()}
        return {}

    def __getattr__(self, name: str) -> Any:
        value = self._data.get(name)
        if isinstance(value, dict):
            return ConfigManager(data=value)
        if isinstance(value, list):
            list_value = cast(List[Any], value)
            processed_list: List[Any] = []
            for item in list_value:
                if isinstance(item, dict):
                    processed_list.append(ConfigManager(data=item))
                else:
                    processed_list.append(item)
            return processed_list
        return value

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        return self._data

    def update_from_args(self, args: Dict[str, Any]):
        arg_map = {
            'target': ['generation_config', 'target_size'],
            'quality': ['quality_config', 'minimum_quality_score'],
            'multilingual': ['generation_config', 'multilingual'],
            'edge_cases': ['generation_config', 'edge_cases'],
            'semantic_analysis': ['quality_config', 'semantic_analysis'],
            'batch_size': ['generation_config', 'batch_size'],
            'parallel': ['generation_config', 'parallel_requests'],
            'output': ['output_config', 'output_file'],
            'checkpoint_interval': ['output_config', 'checkpoint_interval'],
            'hybrid_ratio': ['api_config', 'hybrid_ratio'],
            'enable_backup': ['api_config', 'enable_backup'],
            'steps': ['steps'],
            'force_rebuild': ['data_config', 'force_rebuild']
        }
        
        for arg_key, config_path in arg_map.items():
            if arg_key in args and args[arg_key] is not None:
                d = self._data
                for key in config_path[:-1]:
                    d = d.setdefault(key, {})
                d[config_path[-1]] = args[arg_key]
