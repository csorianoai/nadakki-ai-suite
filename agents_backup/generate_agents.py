# generate_agents.py (v4.0 - Enterprise Edition)
import os
import json
import hashlib
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

TEMPLATE_DIR = 'templates'
BASE_DIR = Path('agents')
MANIFEST_PATH = 'agent_manifest.json'
REGISTRY_PATH = BASE_DIR / 'registry.py'


def load_template(complexity: str):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    return env.get_template(f'{complexity}_agent.jinja2')


def normalize_class_name(name: str) -> str:
    return ''.join(e for e in name.title() if e.isalnum())


def generate_hash(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def write_agent_file(path: Path, content: str):
    path.write_text(content, encoding='utf-8')


def update_manifest(manifest, agent_info):
    manifest.append(agent_info)
    with open(MANIFEST_PATH, 'w', encoding='utf-8') as file:
        json.dump(manifest, file, indent=2)


def generate_init_py(ecosystem_path: Path, ecosystem: str, agents: list):
    init_lines = [
        f'"""\nEcosistema {ecosystem.title()}\nGenerado automáticamente\n"""',
        '',
        '# Imports automáticos'
    ]
    for agent in agents:
        class_name = normalize_class_name(agent['name'])
        init_lines.append(f"from .{class_name.lower()} import {class_name}, create_agent as create_{class_name.lower()}")

    init_lines.append('\nAGENTS_REGISTRY = {')
    for agent in agents:
        class_name = normalize_class_name(agent['name'])
        init_lines.append(f"    '{class_name}': create_{class_name.lower()},")
    init_lines.append('}\n')

    init_lines.append('__all__ = [')
    for agent in agents:
        class_name = normalize_class_name(agent['name'])
        init_lines.append(f"    '{class_name}',")
    init_lines.append('    "AGENTS_REGISTRY"')
    init_lines.append(']')

    (ecosystem_path / '__init__.py').write_text('\n'.join(init_lines), encoding='utf-8')


def generate_registry(ecosystems: dict):
    lines = [
        '"""\nRegistry Central de Agentes - Nadakki AI Suite\nAuto-generado\n"""',
        '',
        'from typing import Dict, Any',
        'from . import *',
        '',
        'class AgentRegistry:',
        '    def __init__(self):',
        '        self.ecosystems = {'
    ]
    for eco in ecosystems:
        lines.append(f"            '{eco}': {eco},")
    lines.append('        }\n')

    lines.append('    def get_agent(self, ecosystem: str, agent_name: str, tenant_id: str):')
    lines.append('        eco = self.ecosystems.get(ecosystem)')
    lines.append('        if eco and hasattr(eco, "AGENTS_REGISTRY") and agent_name in eco.AGENTS_REGISTRY:')
    lines.append('            return eco.AGENTS_REGISTRY[agent_name](tenant_id)')
    lines.append('        return None\n')

    lines.append('    def list_agents(self) -> Dict[str, Any]:')
    lines.append('        return {eco: list(mod.AGENTS_REGISTRY.keys()) for eco, mod in self.ecosystems.items()}\n')

    lines.append('registry = AgentRegistry()\n')
    lines.append('__all__ = ["registry", "AgentRegistry"]')

    REGISTRY_PATH.write_text('\n'.join(lines), encoding='utf-8')


def main():
    with open('agent_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    manifest = []
    for ecosystem, eco_data in config['ecosystems'].items():
        eco_path = BASE_DIR / ecosystem.lower()
        eco_path.mkdir(parents=True, exist_ok=True)

        agents = eco_data['agents']
        generate_init_py(eco_path, ecosystem, agents)

        for agent in agents:
            class_name = normalize_class_name(agent['name'])
            filename = f"{class_name.lower()}.py"
            file_path = eco_path / filename
            template = load_template(agent['complexity'])

            context = {
                'class_name': class_name,
                'ecosystem': ecosystem,
                'description': agent['desc'],
                'performance': agent['perf'],
                'complexity': agent['complexity'],
                'timestamp': datetime.utcnow().isoformat()
            }

            rendered = template.render(**context)
            content_hash = generate_hash(rendered)

            if file_path.exists() and generate_hash(file_path.read_text('utf-8')) == content_hash:
                print(f"✅ Skipping unchanged: {file_path}")
                continue

            write_agent_file(file_path, rendered)
            update_manifest(manifest, {
                'name': class_name,
                'ecosystem': ecosystem,
                'path': str(file_path),
                'hash': content_hash,
                'timestamp': context['timestamp']
            })
            print(f"🛠️ Generated: {file_path}")

    generate_registry(config['ecosystems'])
    print("\n✅ Enterprise agent generation complete.")


if __name__ == '__main__':
    main()