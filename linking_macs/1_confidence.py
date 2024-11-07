import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# Use a non-interactive backend
matplotlib.use('Agg')

# Define the directory to save plots
output_dir = '/media/sf_rathan-dataset/msc_thesis/hwsim_test/linking_macs/'

# Data for kernel time-based analysis
anonymity_sets = ["Set 3", "Set 5", "Set 7", "Set 9", "Set 11"]
test_kernel = [
    [75.000, 32.500, 26.415, 15.942, 12.941],
    [62.500, 22.500, 20.408, 18.050, 13.157],
    [33.333, 22.500, 21.739, 14.084, 9.876],
    [79.160, 22.222, 23.076, 13.636, 10.843],
    [54.167, 41.667, 28.181, 19.718, 10.975]
]
average_accuracy_kernel = [60.832, 28.258, 23.168, 16.286, 11.558]

# Data for AP-initiated MAC re-randomization scheme
test_ap = [
    [29.629, 15.384, 11.111, 9.722, 9.278],
    [44.444, 13.157, 8.196, 4.285, 18.181],
    [33.333, 20.000, 10.909, 5.000, 5.952],
    [33.333, 21.621, 12.903, 18.571, 7.142],
    [50.000, 22.727, 9.523, 11.111, 13.043]
]
average_accuracy_ap = [38.3472, 18.3778, 10.7484, 9.7378, 10.7176]

# Function to plot with combined confidence intervals and individual lines
def plot_combined_with_individual_tests(x, kernel_data, ap_data, kernel_avg, ap_avg, title, filename):
    plt.figure(figsize=(12, 8))

    # Plot individual test results for Kernel Time-Based Analysis
    for test in kernel_data:
        plt.plot(x, test, color='blue', alpha=0.1)
    kernel_means = np.mean(kernel_data, axis=0)
    kernel_std = np.std(kernel_data, axis=0)
    plt.errorbar(x, kernel_avg, yerr=kernel_std, fmt='o-', color='blue', capsize=5, label='Kernel Time-Based MAC Re-Randomization')

    # Plot individual test results for AP-Initiated MAC Re-Randomization
    for test in ap_data:
        plt.plot(x, test, color='red', alpha=0.1)
    ap_means = np.mean(ap_data, axis=0)
    ap_std = np.std(ap_data, axis=0)
    plt.errorbar(x, ap_avg, yerr=ap_std, fmt='o-', color='red', capsize=5, label='AP-Initiated MAC Re-Randomization')

    plt.title(title, fontsize=18)
    plt.xlabel('Anonymity Set (Number of Stations)', fontsize=16)
    plt.ylabel('Accuracy (%)', fontsize=16)
    plt.ylim(0, 80)
    plt.grid(True, color='gray', alpha=0.5)
    plt.xticks(rotation=45, fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(fontsize=14)
    plt.tight_layout()
    plt.savefig(filename, format='pdf')
    plt.close()

# Generate the combined plot with individual lines and confidence intervals
plot_combined_with_individual_tests(
    anonymity_sets,
    test_kernel,
    test_ap,
    average_accuracy_kernel,
    average_accuracy_ap,
    'Combined Analysis of Average Accuracies with Confidence Intervals',
    os.path.join(output_dir, 'combined_analysis_with_individual_tests.pdf')
)
