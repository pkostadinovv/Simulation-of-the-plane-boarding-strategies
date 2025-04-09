import matplotlib.pyplot as plt
import statistics
import numpy as np
from scipy.stats import ttest_ind

from plane import PlaneModel

def run_single_sim(method="Random", door_config="1 Door"):
    """Run one instance of PlaneModel with the chosen method and door config, then return total steps used."""
    model = PlaneModel(method=method, shuffle_enable=True, common_bags='normal', door_config=door_config)
    while model.running:
        model.step()
    return model.schedule.steps

def run_multiple_sims(method="Random", door_config="1 Door", num_runs=1000):
    """Run multiple simulations with the specified method & door config. Return a list of final boarding times."""
    all_times = []
    for i in range(num_runs):
        steps_taken = run_single_sim(method=method, door_config=door_config)
        all_times.append(steps_taken)
        if (i+1) % 50 == 0:
            print(f"  --> Completed {i+1} simulations... ({method}, {door_config})")
    return all_times


if __name__ == "__main__":
    print("What would you like to do?")
    print(" 1) Run multiple simulations for a user-chosen method & door config")
    print(" 2) Run T-test comparing single-door vs. two-door for the same method")
    print(" 3) Run T-test comparing 'Back-to-front' vs. 'Random' (Single door)")
    choice = input("\nEnter your choice [1/2/3]: ").strip()

    if choice not in ("1", "2", "3"):
        print("Invalid input. Defaulting to option '1'.")
        choice = "1"

    # --- Option 1: Normal user scenario with chosen method & door config ---
    if choice == "1":
        method_list = list(PlaneModel.method_types.keys())
        print("\nAvailable boarding methods:")
        for index, m in enumerate(method_list, start=1):
            print(f" {index}) {m}")

        user_method_choice = input("\nPick a method by number: ")
        try:
            choice_index = int(user_method_choice) - 1
            chosen_method = method_list[choice_index]
        except (ValueError, IndexError):
            print("Invalid choice. Defaulting to 'Random'.")
            chosen_method = "Random"

        door_choice = input("\nPick door config (1 or 2) [default=1]: ").strip()
        if door_choice == "2":
            chosen_door = "2 Doors"
        else:
            chosen_door = "1 Door"

        user_input = input("\nHow many simulations? [default=1000]: ").strip()
        if user_input == "":
            num_sims = 1000
        else:
            num_sims = int(user_input)

        print(f"\nRunning {num_sims} simulations using method '{chosen_method}' with {chosen_door}...\n")
        results = run_multiple_sims(chosen_method, chosen_door, num_runs=num_sims)

        mean_time = statistics.mean(results)
        median_time = statistics.median(results)
        std_time = statistics.stdev(results)  # sample stdev
        min_time = min(results)
        max_time = max(results)
        q1 = np.percentile(results, 25)
        q3 = np.percentile(results, 75)

        print(f"\nResults for {chosen_method} with {chosen_door} ({num_sims} runs):")
        print(f"  Mean:     {mean_time:.2f}")
        print(f"  Median:   {median_time:.2f}")
        print(f"  Std Dev:  {std_time:.2f}")
        print(f"  Min:      {min_time}")
        print(f"  Q1:       {q1:.2f}")
        print(f"  Q3:       {q3:.2f}")
        print(f"  Max:      {max_time}\n")

        # Ask if user wants a histogram
        do_plot = input("Do you want to plot the histogram? (y/n) [default=n]: ").lower() == "y"
        if do_plot:
            plt.hist(results, bins=40, edgecolor='black')
            plt.title(f"{chosen_method}, {chosen_door}, Runs: {num_sims}")
            plt.xlabel("Boarding Time (steps)")
            plt.ylabel("Frequency")
            plt.show()


    # --- Option 2: T-test (one door vs. two doors) using the same method ---
    elif choice == "2":
        method_list = list(PlaneModel.method_types.keys())
        print("\nAvailable boarding methods for T-test:")
        for index, m in enumerate(method_list, start=1):
            print(f" {index}) {m}")
        method_choice = input("\nPick a method for T-test by number [default=Random]: ").strip()
        try:
            idx = int(method_choice) - 1
            test_method = method_list[idx]
        except (ValueError, IndexError):
            test_method = "Random"

        test_run_input = input("\nNumber of simulations per door config [default=1000]: ").strip()
        if test_run_input == "":
            test_runs = 1000
        else:
            test_runs = int(test_run_input)

        print(f"\n=== T-TEST: Single vs. Two Door Boarding (Method='{test_method}') ===")
        print(f"Running {test_runs} simulations each for Single-Door and Two-Door...")

        results_1d = run_multiple_sims(method=test_method, door_config="1 Door", num_runs=test_runs)
        results_2d = run_multiple_sims(method=test_method, door_config="2 Doors", num_runs=test_runs)

        stat, p_value = ttest_ind(results_1d, results_2d, equal_var=False)

        mean_1d = statistics.mean(results_1d)
        mean_2d = statistics.mean(results_2d)
        diff = mean_1d - mean_2d
        diff_pct = (diff / mean_1d * 100) if mean_1d != 0 else 0.0

        print("\n--- T-Test (Welch) Results ---")
        print(f" Single-Door Mean: {mean_1d:.2f}")
        print(f" Two-Door   Mean: {mean_2d:.2f}")
        print(f" Difference: {diff:.2f}  ({diff_pct:.2f}%)")
        print(f" t-stat = {stat:.3f}, p-value = {p_value:.6f}")

        if p_value < 0.05:
            print(" ==> We can reject H0: There's a significant difference between single-door and two-door means.")
        else:
            print(" ==> We fail to reject H0: No significant difference found (p>=0.05).")

        # === PLOT side by side histograms ===
        do_plot = input("\nPlot both distributions side-by-side? (y/n) [default=n]: ").lower() == "y"
        if do_plot:
            plt.figure(figsize=(10, 4))

            # Left subplot: single-door
            plt.subplot(1, 2, 1)
            plt.hist(results_1d, bins=40, edgecolor='black', alpha=0.7)
            plt.title(f"{test_method} (Single-Door) - {test_runs} runs\nMean={mean_1d:.1f}")

            # Right subplot: two-door
            plt.subplot(1, 2, 2)
            plt.hist(results_2d, bins=40, edgecolor='black', alpha=0.7, color='orange')
            plt.title(f"{test_method} (Two-Door) - {test_runs} runs\nMean={mean_2d:.1f}")

            plt.tight_layout()
            plt.show()


    # --- Option 3: T-test comparing 'Back-to-front' vs. 'Random' under single-door
    elif choice == "3":
        print("\n=== T-TEST: Comparing 'Back-to-front' vs. 'Random' (Single Door) ===")
        runs_input = input("How many simulations per method? [default=1000]: ").strip()
        if runs_input == "":
            test_runs = 1000
        else:
            test_runs = int(runs_input)

        print(f"\nRunning {test_runs} simulations each for 'Back-to-front' and 'Random' under Single-Door...\n")
        results_back_front = run_multiple_sims(method="Back-to-front", door_config="1 Door", num_runs=test_runs)
        results_random = run_multiple_sims(method="Random", door_config="1 Door", num_runs=test_runs)

        stat, p_value = ttest_ind(results_back_front, results_random, equal_var=False)

        mean_bf = statistics.mean(results_back_front)
        mean_rn = statistics.mean(results_random)
        diff = mean_bf - mean_rn
        diff_pct = (diff / mean_bf * 100) if mean_bf != 0 else 0.0

        print("\n--- T-Test (Welch) Results ---")
        print(f" Back-to-front Mean: {mean_bf:.2f}")
        print(f" Random        Mean: {mean_rn:.2f}")
        print(f" Difference:        {diff:.2f}  ({diff_pct:.2f}%)")
        print(f" t-stat = {stat:.3f}, p-value = {p_value:.6f}")

        if p_value < 0.05:
            print(" ==> We can reject H0: There's a significant difference between 'Back-to-front' and 'Random' in single-door mode.")
        else:
            print(" ==> We fail to reject H0: No significant difference found (p>=0.05).")

        # === PLOT side by side histograms ===
        do_plot = input("\nPlot both distributions side-by-side? (y/n) [default=n]: ").lower() == "y"
        if do_plot:
            plt.figure(figsize=(10, 4))

            # Left subplot: back-to-front
            plt.subplot(1, 2, 1)
            plt.hist(results_back_front, bins=40, edgecolor='black', alpha=0.7)
            plt.title(f"Back-to-front - {test_runs} runs\nMean={mean_bf:.1f}")

            # Right subplot: random
            plt.subplot(1, 2, 2)
            plt.hist(results_random, bins=40, edgecolor='black', alpha=0.7, color='green')
            plt.title(f"Random - {test_runs} runs\nMean={mean_rn:.1f}")

            plt.tight_layout()
            plt.show()

    print("\nAll done!")
