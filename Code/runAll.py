import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
import ast 

ALLOWED_IMPORTS = ["json", "collections", "router", "packet", "dijkstar", "networkx", "typing", "dataclasses", "copy"]

TEST_FILES = [f"test{i}.json" for i in range(1, 6)]
ROUTER_CLASSES = ["DV", "LS"]
BONUS_POINTS = 10

GRADES = {
    "test1": {"small_networks": 3},
    "test2": {
        "all_correct": 5,
        "1_incorrect": 3,
        "2_incorrect": 2,
        "3_incorrect": 1,
    },
    "test3": {"medium_network": 10},
    "test4": {"large_network": 12},
    "test5": {
        "all_correct": 15,
        "1_incorrect": 12,
        "2_incorrect": 10,
        "3_incorrect": 8,
        "5_incorrect": 5,
    },
}

def analyze_code(file_path: str) -> bool:
    """
    Analyze the student's code for restricted imports or functions.
    Deduct marks for violations.
    """
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            code = f.read()
    else:
        print(f"File {file_path} does not exist.")
        return False

    # Mapping of aliases (e.g., "o" -> "os") cuz students can do weird import os as o
    alias_map = {}

    try:
        # Parse the code into an AST (Abstract Syntax Tree) best thing ever
        tree = ast.parse(code)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    alias_map[alias.asname or alias.name] = alias.name
                    if alias.name not in ALLOWED_IMPORTS:
                        print(f"\033[91m[RESTRICTED IMPORT]\033[0m {alias.name} found!")
                        return True

            elif isinstance(node, ast.ImportFrom):
                # we will flag all "from os ..." imports
                if node.module not in ALLOWED_IMPORTS:
                    print(
                        f"\033[91m[RESTRICTED IMPORT]\033[0m from {node.module} import ... is not allowed!")
                    return True
    except Exception as e:
        print(f"Error analyzing code: {e}")
        return False

    return False


def run_test(test_file, router_class):
    """
    Run a single test file with the specified router class.
    
    Args:
        test_file (str): Path to the test file.
        router_class (str): The router class ("DV" or "LS").
    
    Returns:
        tuple: (test_file, router_class, output) where `output` is the result of the subprocess.
    """
    try:
        print(f"Running {test_file} with {router_class}...")
        result = subprocess.run(
            ["python3", "network.py", test_file, router_class],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            print(f"Error running test case {test_file} with {router_class} : \n{result.stderr}")
        return test_file, router_class, result.stdout
    except Exception as e:
        print(f"Error running test {test_file} with {router_class}: {e}")
        return test_file, router_class, None


def calculate_score(test_name, output):
    """
    Calculate the score for a test case based on the output.
    
    Args:
        test_name (str): Name of the test (e.g., "test1").
        output (str): Output from the subprocess.
    
    Returns:
        int: The score for the test case.
    """
    if not output:
        return 0

    if test_name == "test1":
        return GRADES["test1"]["small_networks"] if "All Routes correct!" in output else 0
    elif test_name == "test2":
        if "All Routes correct!" in output:
            return GRADES["test2"]["all_correct"]
        if "1 route is incorrect" in output:
            return GRADES["test2"]["1_incorrect"]
        if "2 routes are incorrect" in output:
            return GRADES["test2"]["2_incorrect"]
        if "3 routes are incorrect" in output:
            return GRADES["test2"]["3_incorrect"]
    elif test_name == "test3":
        return GRADES["test3"]["medium_network"] if "All Routes correct!" in output else 0
    elif test_name == "test4":
        return GRADES["test4"]["large_network"] if "All Routes correct!" in output else 0
    elif test_name == "test5":
        if "All Routes correct!" in output:
            return GRADES["test5"]["all_correct"]
        if "1 route is incorrect" in output:
            return GRADES["test5"]["1_incorrect"]
        if "2 routes are incorrect" in output:
            return GRADES["test5"]["2_incorrect"]
        if "3 routes are incorrect" in output:
            return GRADES["test5"]["3_incorrect"]
        if "5 routes are incorrect" in output:
            return GRADES["test5"]["5_incorrect"]
    return 0


def main():
    """
    Main function to execute all tests and calculate total scores.
    """
    total_scores = {"LS": 0, "DV": 0, "Bonus": 0}
    results = []
    
    if analyze_code("LSrouter.py") or analyze_code("DVrouter.py"):
        print("Code contains restricted imports or functions. Skipping tests.")
        print("Final Score: 0/45")
        exit(0)

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(run_test, test_file, router_class)
            for router_class in ROUTER_CLASSES
            for test_file in TEST_FILES
        ]

        for future in futures:
            results.append(future.result())

    for test_file, router_class, output in results:
        test_name = os.path.splitext(test_file)[0]
        score = calculate_score(test_name, output)
        print(f"{test_file} ({router_class}): {score} points")
        total_scores[router_class] += score

    total_scores["Bonus"] = 0
    if total_scores["DV"] == 45 and total_scores["LS"] == 45:
        total_scores["Bonus"] = BONUS_POINTS 
        total_grade = total_scores["DV"] + total_scores["Bonus"]
    else:
        total_grade = max(total_scores["DV"], total_scores["LS"]) + total_scores["Bonus"]
        
        
    print("\n--- Total Grade ---")
    for category, score in total_scores.items():
        print(f"{category}: {score} points")
    print(f"\nFinal Score: {total_grade}/45")


if __name__ == "__main__":
    main()
