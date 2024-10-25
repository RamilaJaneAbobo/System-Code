import os
import sys

def run_file(file_name):
    try:
        print(f"\nRunning {file_name}...\n")
        os.system(f"python {file_name}")
    except Exception as e:
        print(f"Error running {file_name}: {e}")

def main():
    while True:
        # Display options for the user
        print("\nSelect which file you want to run:")
        print("1. combine.py")
        print("2. dataprocessing.py")
        print("3. k-anonymity.py")
        print("4. Exit")
        
        # Get the user's choice
        choice = input("Enter 1, 2, 3 or 4: ")

        if choice == '1':
            run_file("combine.py")
        elif choice == '2':
            run_file("dataprocessing.py")
             elif choice == '3':
            run_file("k-anonymity.py")
        elif choice == '4':
            print("Exiting the program.")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
        
        # Ask if the user wants to run another file
        run_another = input("\nDo you want to run another file? (yes/no): ").strip().lower()
        if run_another != 'yes':
            print("Exiting the program.")
            sys.exit(0)

if __name__ == "__main__":
    main()
