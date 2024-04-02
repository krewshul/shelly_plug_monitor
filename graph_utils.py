import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('TkAgg')
from datetime import datetime


def create_bar_graph(data, timestamps, xlabel, ylabel, title):
    if plt.fignum_exists(1):
        plt.close(1)  # Close the existing figure if it exists
    plt.rcParams['figure.figsize'] = [15, 8]
    plt.figure().clear()

    plt.bar(timestamps, data, color='#1f538d')  # Use index as x-values
    plt.xlabel(xlabel, fontsize=12, fontweight='bold', color='white')
    plt.ylabel(ylabel, fontsize=12, fontweight='bold', color='white')
    plt.title(f'{title}', fontsize=14, fontweight='bold', color='white')
    plt.gcf().set_facecolor('#2d2d2d')
    plt.gca().set_facecolor('#2d2d2d')
    plt.grid(True, linestyle='--', linewidth=0.5, color='orange')
    plt.yticks(color="white")
    plt.xticks(rotation=20, color='white') 
    plt.show()
    
def create_line_graph(data, timestamps, xlabel, ylabel, title):
    if plt.fignum_exists(1):
        plt.close(1)  # Close the existing figure if it exists
    plt.rcParams['figure.figsize'] = [15, 8]
    plt.figure().clear()

    plt.plot(range(len(data)), data, color='#1f538d')
    plt.xlabel(xlabel, fontsize=12, fontweight='bold', color='white')
    plt.ylabel(ylabel, fontsize=12, fontweight='bold', color='white')
    plt.title(title, fontsize=14, fontweight='bold', color='white')
    plt.gcf().set_facecolor('#2d2d2d')
    plt.gca().set_facecolor('#2d2d2d')
    plt.grid(True, linestyle=':', linewidth=0.5, color='orange')
    plt.yticks(color='white')

    # Debug statements to check lengths of data and timestamps
    print("Length of data:", len(data))
    print("Length of timestamps:", len(timestamps))
    
    plt.xticks(range(0, len(data), max(1, len(data) // 10)), [timestamps[i] for i in range(0, len(data), max(1, len(data) // 10))], rotation=20, color='white')
    plt.show()
