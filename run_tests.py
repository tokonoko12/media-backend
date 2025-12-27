import os
import subprocess
import sys

def run_tests():
    tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
    test_files = [f for f in os.listdir(tests_dir) if f.startswith('test_') and f.endswith('.py')]
    
    print(f"=== Found {len(test_files)} test files in {tests_dir} ===")
    
    passed = 0
    failed = 0
    
    for test_file in sorted(test_files):
        print(f"\n>> Running {test_file}...")
        try:
            # Run the test script as a subprocess
            result = subprocess.run(
                [sys.executable, os.path.join(tests_dir, test_file)],
                capture_output=False, # Let stdout/stderr flow to console
                check=True
            )
            print(f">> {test_file} PASSED")
            passed += 1
        except subprocess.CalledProcessError:
            print(f">> {test_file} FAILED")
            failed += 1
            
    print("\n" + "="*30)
    print(f"Summary: {passed} PASSED, {failed} FAILED")
    print("="*30)
    
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
