import os
import matplotlib.pyplot as plt

# Define the directory to save plots
output_dir = '/media/sf_rathan-dataset/msc_thesis/hwsim_test/linking_macs/'
#os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist

# Data for kernel time-based analysis
anonymity_sets_kernel = ["Set 3", "Set 5", "Set 7", "Set 9", "Set 11"]
test_1_kernel = [75.000, 32.500, 26.415, 15.942, 12.941]
test_2_kernel = [62.500, 22.500, 20.408, 18.050, 13.157]
test_3_kernel = [33.333, 22.500, 21.739, 14.084, 9.876]
test_4_kernel = [79.160, 22.222, 23.076, 13.636, 10.843]
test_5_kernel = [54.167, 41.667, 28.181, 19.718, 10.975]
average_accuracy_kernel = [60.832, 28.258, 23.168, 16.286, 11.558]

# Data for AP-initiated MAC re-randomization scheme
anonymity_sets_ap = ["Set 3", "Set 5", "Set 7", "Set 9", "Set 11"]
test_1_ap = [29.629, 15.384, 11.111, 9.722, 9.278]
test_2_ap = [44.444, 13.157, 8.196, 4.285, 18.181]
test_3_ap = [33.333, 20.000, 10.909, 5.000, 5.952]
test_4_ap = [33.333, 21.621, 12.903, 18.571, 7.142]
test_5_ap = [50.000, 22.727, 9.523, 11.111, 13.043]
average_accuracy_ap = [38.3472, 18.3778, 10.7484, 9.7378, 10.7176]

# Create individual plots for Kernel Time-Based Analysis
plt.figure(figsize=(10, 8))
for test in [test_1_kernel, test_2_kernel, test_3_kernel, test_4_kernel, test_5_kernel]:
    plt.plot(anonymity_sets_kernel, test, marker='o')
plt.plot(anonymity_sets_kernel, average_accuracy_kernel, marker='o', linestyle='--', color='black', label='Average Accuracy')
plt.title('Kernel Time-Based Analysis')
plt.xlabel('Anonymity Set')
plt.ylabel('Accuracy (%)')
plt.ylim(0, 100)
plt.grid()
plt.xticks(rotation=45)
plt.legend()
plt.savefig(os.path.join(output_dir, 'kernel_time_analysis.png'))  # Save the figure to a file

# Create individual plots for AP-Initiated MAC Re-Randomization Scheme
plt.figure(figsize=(10, 8))
for test in [test_1_ap, test_2_ap, test_3_ap, test_4_ap, test_5_ap]:
    plt.plot(anonymity_sets_ap, test, marker='o')
plt.plot(anonymity_sets_ap, average_accuracy_ap, marker='o', linestyle='--', color='black', label='Average Accuracy')
plt.title('AP-Initiated MAC Re-Randomization Scheme')
plt.xlabel('Anonymity Set')
plt.ylabel('Accuracy (%)')
plt.ylim(0, 100)
plt.grid()
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'ap_initiated_analysis.png'))  # Save the figure to a file

# Create a combined plot for averages
plt.figure(figsize=(10, 8))
plt.plot(anonymity_sets_kernel, average_accuracy_kernel, marker='o', linestyle='-', color='blue', label='Kernel Time-Based')
plt.plot(anonymity_sets_ap, average_accuracy_ap, marker='o', linestyle='-', color='orange', label='AP-Initiated')

plt.title('Average Accuracies of Linking Re-Randomized MAC Addresses')
plt.xlabel('Anonymity Set (Number of Stations)')
plt.ylabel('Average Accuracy (%)')
plt.ylim(0, 100)
plt.grid()
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'combined_analysis.png'))  # Save the figure to a file

# Show the combined graph
