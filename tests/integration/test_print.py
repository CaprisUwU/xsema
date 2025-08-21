"""Test script to verify print functionality."""

def test_print():
    """Test different print scenarios."""
    # Test basic print
    print("1. Basic print")
    
    # Test print with emoji
    print("2. Print with emoji: 🌐")
    
    # Test print with special characters
    print("3. Print with special chars: áéíóú")
    
    # Test print with long line
    print("4. " + "=" * 100)
    
    # Test print with different encodings
    try:
        print("5. Trying to print with default encoding")
        print("6. Trying to print with emoji: 🌐")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test print with manual encoding
    try:
        print("7. Manual encoding: " + "🌐".encode('utf-8').decode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")
    
    # Test print with ASCII fallback
    try:
        s = "8. ASCII fallback: 🌐"
        print(s.encode('ascii', 'ignore').decode('ascii'))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("=== Starting print test ===")
    test_print()
    print("=== Print test completed ===")
