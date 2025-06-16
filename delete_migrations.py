import os

base_dir = os.path.dirname(os.path.abspath(__file__))

for root, dirs, files in os.walk(base_dir):
    if 'migrations' in dirs:
        migration_path = os.path.join(root, 'migrations')
        for file in os.listdir(migration_path):
            if file.endswith('.py') and file != '__init__.py':
                os.remove(os.path.join(migration_path, file))
                print(f"Eliminado: {os.path.join(migration_path, file)}")
            elif file.endswith('.pyc'):
                os.remove(os.path.join(migration_path, file))
                print(f"Eliminado: {os.path.join(migration_path, file)}")
