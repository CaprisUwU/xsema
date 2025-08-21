import sys
import os

print("Python Path:")
for path in sys.path:
    print(f"- {path}")

print("\nCurrent Working Directory:", os.getcwd())
print("\nTrying to import portfolio...")

try:
    import portfolio
    print("✅ Successfully imported portfolio")
    print("Portfolio module location:", portfolio.__file__)
except ImportError as e:
    print(f"❌ Failed to import portfolio: {e}")
    
    # Try adding the current directory to the path
    print("\nTrying to add project root to Python path...")
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    print(f"Added to path: {project_root}")
    
    try:
        import portfolio
        print("✅ Successfully imported portfolio after path adjustment")
        print("Portfolio module location:", portfolio.__file__)
    except ImportError as e:
        print(f"❌ Still failed to import portfolio: {e}")
        print("\nTrying to list directory contents:")
        print(os.listdir(project_root))
