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

# --------------------------------------------------------------
# We'll define a helper function to get (or store) the baseline
# "Random, 1 Door" scenario that the paper uses as 100%.
# --------------------------------------------------------------
_baseline_cache = None

def ensure_baseline(num_runs=1000):
    """
    Runs 'Random, 1 Door' with num_runs (if not already done),
    returns the baseline mean. This is the reference scenario
    we'll call 100% (like in the paper).
    """
    global _baseline_cache
    if _baseline_cache is None:
        print(f"--- Computing baseline scenario: Random (1 Door), {num_runs} runs ---")
        results_base = run_multiple_sims(method="Random", door_config="1 Door", num_runs=num_runs)
        _baseline_cache = statistics.mean(results_base)
        print(f"Baseline Single-Door Random Mean => {_baseline_cache:.2f} steps\n")
    return _baseline_cache

if __name__ == "__main__":
    print("This script first establishes 'Random, 1 Door' as a baseline = 100%,")
    print("then expresses all scenario means as a ratio to that baseline.")
    print("\nWhat would you like to do?")
    print(" 1) Run multiple simulations for a user-chosen method & door config (reports ratio vs. baseline)")
    print(" 2) Run T-test comparing single-door vs. two-door for the same method (also ratio vs. baseline)")
    print(" 3) Run T-test comparing 'Back-to-front' vs. 'Random' (Single door)")
    print(" 4) Run T-test comparing 'Back-to-front' vs. 'Random' (Two Doors)")

    choice = input("\nEnter your choice [1/2/3/4]: ").strip()
    if choice not in ("1", "2", "3", "4"):
        print("Invalid input. Defaulting to option '1'.")
        choice = "1"

    # We'll also let the user define how many runs for the baseline so it matches the next tests:
    baseline_runs_input = input("\nHow many baseline runs? [default=1000]: ").strip()
    if baseline_runs_input == "":
        baseline_runs = 1000
    else:
        baseline_runs = int(baseline_runs_input)

    # Step 1: ensure we have the baseline from single-door random
    baseline_mean = ensure_baseline(num_runs=baseline_runs)

    # --- Option 1: normal scenario, but we also express ratio vs. baseline
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

        ratio_vs_baseline = (mean_time / baseline_mean)*100 if baseline_mean != 0 else 0

        print(f"\nResults for {chosen_method} with {chosen_door} ({num_sims} runs):")
        print(f"  Mean:     {mean_time:.2f}  => {ratio_vs_baseline:.1f}% of baseline (random 1D)")
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

    # --- Option 2: T-test (one door vs. two doors) using the same method
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

        mean_1d = statistics.mean(results_1d)
        mean_2d = statistics.mean(results_2d)

        # Compare to baseline:
        ratio_1d = (mean_1d / baseline_mean)*100 if baseline_mean else 0
        ratio_2d = (mean_2d / baseline_mean)*100 if baseline_mean else 0

        stat, p_value = ttest_ind(results_1d, results_2d, equal_var=False)

        print("\n--- T-Test (Welch) Results ---")
        print(f" Single-Door Mean: {mean_1d:.2f} => {ratio_1d:.1f}% of baseline")
        print(f" Two-Door   Mean: {mean_2d:.2f} => {ratio_2d:.1f}% of baseline")

        diff = mean_1d - mean_2d
        diff_pct = (diff / mean_1d * 100) if mean_1d != 0 else 0.0
        print(f" Difference: {diff:.2f}  ({diff_pct:.2f}%)")
        print(f" t-stat = {stat:.3f}, p-value = {p_value:.6f}")

        if p_value < 0.05:
            print(" ==> We can reject H0: There's a significant difference between single-door and two-door means.")
        else:
            print(" ==> We fail to reject H0: No significant difference found (p>=0.05).")

        # Plot side-by-side
        do_plot = input("\nPlot both distributions side-by-side? (y/n) [default=n]: ").lower() == "y"
        if do_plot:
            plt.figure(figsize=(10, 4))

            # Left subplot: single-door
            plt.subplot(1, 2, 1)
            plt.hist(results_1d, bins=40, edgecolor='black', alpha=0.7)
            plt.title(f"{test_method} (Single-Door)\nMean={mean_1d:.1f}\n({ratio_1d:.1f}% of baseline)")

            # Right subplot: two-door
            plt.subplot(1, 2, 2)
            plt.hist(results_2d, bins=40, edgecolor='black', alpha=0.7, color='orange')
            plt.title(f"{test_method} (Two-Door)\nMean={mean_2d:.1f}\n({ratio_2d:.1f}% of baseline)")

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

        mean_bf = statistics.mean(results_back_front)
        mean_rn = statistics.mean(results_random)

        # Compare both to the random-1door baseline from earlier
        ratio_bf = (mean_bf / baseline_mean)*100 if baseline_mean else 0
        ratio_rn = (mean_rn / baseline_mean)*100 if baseline_mean else 0

        stat, p_value = ttest_ind(results_back_front, results_random, equal_var=False)

        print("\n--- T-Test (Welch) Results ---")
        print(f" Back-to-front Mean: {mean_bf:.2f} => {ratio_bf:.1f}% of baseline")
        print(f" Random        Mean: {mean_rn:.2f} => {ratio_rn:.1f}% of baseline")

        diff = mean_bf - mean_rn
        diff_pct = (diff / mean_bf * 100) if mean_bf != 0 else 0.0
        print(f" Difference:        {diff:.2f}  ({diff_pct:.2f}%)")
        print(f" t-stat = {stat:.3f}, p-value = {p_value:.6f}")

        if p_value < 0.05:
            print(" ==> We can reject H0: There's a significant difference between 'Back-to-front' and 'Random' in single-door mode.")
        else:
            print(" ==> We fail to reject H0: No significant difference found (p>=0.05).")

        do_plot = input("\nPlot both distributions side-by-side? (y/n) [default=n]: ").lower() == "y"
        if do_plot:
            plt.figure(figsize=(10, 4))

            # BFS
            plt.subplot(1, 2, 1)
            plt.hist(results_back_front, bins=40, edgecolor='black', alpha=0.7)
            plt.title(f"Back-to-front (1D)\nMean={mean_bf:.1f}\n({ratio_bf:.1f}% of baseline)")

            # Random
            plt.subplot(1, 2, 2)
            plt.hist(results_random, bins=40, edgecolor='black', alpha=0.7, color='green')
            plt.title(f"Random (1D)\nMean={mean_rn:.1f}\n({ratio_rn:.1f}% of baseline)")

            plt.tight_layout()
            plt.show()

    # --- Option 4: T-test comparing 'Back-to-front' vs. 'Random' under two doors
    elif choice == "4":
        print("\n=== T-TEST: Comparing 'Back-to-front' vs. 'Random' (Two Doors) ===")
        runs_input = input("How many simulations per method? [default=1000]: ").strip()
        if runs_input == "":
            test_runs = 1000
        else:
            test_runs = int(runs_input)

        print(f"\nRunning {test_runs} simulations each for 'Back-to-front' and 'Random' under Two Doors...\n")
        results_bf_2d = run_multiple_sims(method="Back-to-front", door_config="2 Doors", num_runs=test_runs)
        results_rn_2d = run_multiple_sims(method="Random", door_config="2 Doors", num_runs=test_runs)

        mean_bf = statistics.mean(results_bf_2d)
        mean_rn = statistics.mean(results_rn_2d)

        ratio_bf = (mean_bf / baseline_mean)*100 if baseline_mean else 0
        ratio_rn = (mean_rn / baseline_mean)*100 if baseline_mean else 0

        stat, p_value = ttest_ind(results_bf_2d, results_rn_2d, equal_var=False)

        print("\n--- T-Test (Welch) Results ---")
        print(f" Back-to-front (2D) Mean: {mean_bf:.2f} => {ratio_bf:.1f}% of baseline")
        print(f" Random (2D)        Mean: {mean_rn:.2f} => {ratio_rn:.1f}% of baseline")

        diff = mean_bf - mean_rn
        diff_pct = (diff / mean_bf * 100) if mean_bf != 0 else 0.0
        print(f" Difference:             {diff:.2f}  ({diff_pct:.2f}%)")
        print(f" t-stat = {stat:.3f}, p-value = {p_value:.6f}")

        if p_value < 0.05:
            print(" ==> We can reject H0: There's a significant difference between 'Back-to-front' and 'Random' in two-door mode.")
        else:
            print(" ==> We fail to reject H0: No significant difference found (p>=0.05).")

        do_plot = input("\nPlot both distributions side-by-side? (y/n) [default=n]: ").lower() == "y"
        if do_plot:
            plt.figure(figsize=(10, 4))

            # BFS (2D)
            plt.subplot(1, 2, 1)
            plt.hist(results_bf_2d, bins=40, edgecolor='black', alpha=0.7)
            plt.title(f"Back-to-front (2D)\nMean={mean_bf:.1f}\n({ratio_bf:.1f}% of baseline)")

            # Random (2D)
            plt.subplot(1, 2, 2)
            plt.hist(results_rn_2d, bins=40, edgecolor='black', alpha=0.7, color='green')
            plt.title(f"Random (2D)\nMean={mean_rn:.1f}\n({ratio_rn:.1f}% of baseline)")

            plt.tight_layout()
            plt.show()

    print("\nAll done!")
