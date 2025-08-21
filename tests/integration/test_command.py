"""
Test script to verify basic Python command execution.
"""
import os
import sys
import platform

def main():
    print("=== Test Script Running ===")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Working Directory: {os.getcwd()}")
    
    # Test file creation
    test_file = "test_output.txt"
    try:
        with open(test_file, "w") as f:
            f.write("Test successful!")
        print(f"\n✓ Successfully created file: {test_file}")
        
        # List files in current directory
        print("\nFiles in current directory:")
        for file in os.listdir('.'):
            if os.path.isfile(file):
                print(f"- {file}")
                
    except Exception as e:
        print(f"\n✗ Error during file operations: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
