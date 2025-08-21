"""
Direct test of portfolio module import.
"""
import sys
import os

def main():
    print("Direct Portfolio Import Test")
    print("==========================")
    
    # Print current working directory
    print(f"Current directory: {os.getcwd()}")
    
    # Print Python path
    print("\nPython path:")
    for i, path in enumerate(sys.path, 1):
        print(f"{i:2d}. {path}")
    
    # Try to import the portfolio module
    print("\nAttempting to import portfolio module...")
    try:
        import portfolio
        print("✓ Successfully imported 'portfolio' module")
        print(f"   Module location: {portfolio.__file__}")
        
        # Try to access some attributes
        print("\nAvailable attributes in portfolio module:")
        for attr in dir(portfolio):
            if not attr.startswith('_'):
                print(f"- {attr}")
                
    except ImportError as e:
        print(f"✗ Failed to import 'portfolio' module: {e}")
    except Exception as e:
        print(f"✗ Error importing 'portfolio' module: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
