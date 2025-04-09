import matplotlib.pyplot as plt
import statistics
import numpy as np

from plane import PlaneModel

def run_single_sim(method="Random", door_config="1 Door"):
    """
    Run one instance of PlaneModel with the chosen method and door config,
    then return total steps used.
    """
    model = PlaneModel(method=method, shuffle_enable=True, common_bags='normal', door_config=door_config)
    while model.running:
        model.step()
    return model.schedule.steps

def run_multiple_sims(method="Random", door_config="1 Door", num_runs=1000):
    """
    Run multiple simulations with the specified method & door config.
    Return a list of final boarding times.
    """
    all_times = []
    for i in range(num_runs):
        steps_taken = run_single_sim(method=method, door_config=door_config)
        all_times.append(steps_taken)
        if (i+1) % 50 == 0:
            print(f"  --> Completed {i+1} simulations...")
    return all_times

if __name__ == "__main__":
    method_list = list(PlaneModel.method_types.keys())
    print("Available boarding methods:")
    for index, m in enumerate(method_list, start=1):
        print(f" {index}) {m}")

    user_method_choice = input("\nPick a method by number: ")
    try:
        choice_index = int(user_method_choice) - 1
        chosen_method = method_list[choice_index]
    except (ValueError, IndexError):
        print("Invalid choice. Defaulting to 'Random'.")
        chosen_method = "Random"

    # New prompt for door config
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
    std_time = statistics.pstdev(results)
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

    plt.hist(results, bins=40, edgecolor='black')
    plt.title(f"{chosen_method}, {chosen_door}, Runs: {num_sims}")
    plt.xlabel("Boarding Time (steps)")
    plt.ylabel("Frequency")
    plt.show()
