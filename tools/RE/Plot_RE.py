import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import matplotlib.cm as cm
from tools.maybeExcel import getDataFromExcel


########----------------------------Wind_Nature------------------------------------##################
def __draw_wind_nature2(wind_speed6, wind_dir6, wind_speed19, wind_dir19, wind_speed33, wind_dir33, day):
    """
    Draw wind rose charts for wind speeds and directions at different heights with time series information.

    Parameters:
    wind_speed6 (list or array-like): Wind speeds at 6ft, length should be equal to the number of time intervals.
    wind_dir6 (list or array-like): Wind directions at 6ft, in degrees, length should be equal to the number of time intervals.
    wind_speed19 (list or array-like): Wind speeds at 19ft, length should be equal to the number of time intervals.
    wind_dir19 (list or array-like): Wind directions at 19ft, in degrees, length should be equal to the number of time intervals.
    wind_speed33 (list or array-like): Wind speeds at 33ft, length should be equal to the number of time intervals.
    wind_dir33 (list or array-like): Wind directions at 33ft, in degrees, length should be equal to the number of time intervals.

    Outputs:
    Displays a figure with three wind rose charts, each representing wind data at different heights (6ft, 19ft, 33ft),
    with color encoding time of day from 0 to 24 hours.

    Functionality:
    - Creates three subplots, each with polar coordinates for plotting wind roses.
    - Each wind rose shows wind speed and direction data, with color indicating the time of day.
    - Adds a color bar at the bottom to indicate the time of day.
    - Titles and labels the plots accordingly.
    """

    # Time in hours, assuming equal intervals for the provided wind data
    time_hours = np.arange(0, 24, 24 / len(wind_dir6))

    # Grouping wind data with corresponding titles
    groups = [
        (wind_speed6, wind_dir6, time_hours, '6ft'),
        (wind_speed19, wind_dir19, time_hours, '19ft'),
        (wind_speed33, wind_dir33, time_hours, '33ft')
    ]

    # Find the maximum wind speed across all heights
    max_speed = max(max(wind_speed6), max(wind_speed19), max(wind_speed33))

    # Define y-axis ticks, limiting to 4-6 ticks
    num_ticks = 5
    y_ticks = np.linspace(0, max_speed, num_ticks + 1).astype(int)

    # Create wind rose plots
    fig, axs = plt.subplots(1, 3, figsize=(18, 6), subplot_kw={'polar': True})

    # Set up color map and normalization based on time of day
    cmap = cm.viridis
    norm = Normalize(vmin=time_hours.min(), vmax=time_hours.max())

    for ax, (speeds, dirs, times, title) in zip(axs, groups):
        for i in range(len(dirs)):
            # Plot each wind bar with color based on time of day
            ax.bar(np.deg2rad(dirs[i]), speeds[i], color=cmap(norm(times[i])), alpha=0.7, edgecolor='white')

        # Set y-axis limits and labels with extra space for leave margin
        ax.set_ylim(0, max_speed * 1.1)
        ax.set_yticks(y_ticks)  # Set y-ticks as integers
        ax.set_yticklabels([f'{tick} m/s' if tick == y_ticks[-1] else str(tick) for tick in y_ticks])
        ax.set_title(title)

    # Add color bar at the bottom to indicate time of day
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar_ax = fig.add_axes([0.1, 0.05, 0.8, 0.03])
    cbar = plt.colorbar(sm, cax=cbar_ax, orientation='horizontal')
    cbar.set_label('Time (hours)')

    # Set the main title for the figure
    fig.suptitle('Wind Rose with Time Series Information by Time of Day'+ str(day) , fontsize=16)

    # Adjust layout to add some margin
    plt.tight_layout(rect=[0, 0.1, 1, 0.95])

    # Display the plot
    plt.show()


def draw_wind_nature_ending(day):
    file = "D:\project\diffusion\data\RE\\2024_re_nature_" + str(day) + ".xlsx"
    wind_speed6 = getDataFromExcel(file, 3, 4, 0, 96).flatten()
    wind_dir6 = getDataFromExcel(file, 3 + 4, 4 + 4, 0, 96).flatten()
    wind_speed6 = wind_speed6[::4]
    wind_dir6 = wind_dir6[::4]
    wind_speed19 = getDataFromExcel(file, 3 + 1, 4 + 1, 0, 96).flatten()
    wind_dir19 = getDataFromExcel(file, 3 + 4 + 1, 4 + 4 + 1, 0, 96).flatten()
    wind_speed19 = wind_speed19[::4]
    wind_dir19 = wind_dir19[::4]
    wind_speed33 = getDataFromExcel(file, 3 + 3, 4 + 3, 0, 96).flatten()
    wind_dir33 = getDataFromExcel(file, 3 + 4 + 3, 4 + 4 + 3, 0, 96).flatten()
    wind_speed33 = wind_speed33[::4]
    wind_dir33 = wind_dir33[::4]
    __draw_wind_nature2(wind_speed6, wind_dir6, wind_speed19, wind_dir19, wind_speed33, wind_dir33, day)

########----------------------------Wind_Power------------------------------------##################
def plot_wind_power2(output_6ft, output_19ft, output_33ft):
    """
    Plot wind power output curves at different heights

    Parameters:
    output_6ft (list or array-like): Wind power output array at 6ft, length 96
    output_19ft (list or array-like): Wind power output array at 19ft, length 96
    output_33ft (list or array-like): Wind power output array at 33ft, length 96
    """

    # Ensure the input arrays have length 96
    if len(output_6ft) != 96 or len(output_19ft) != 96 or len(output_33ft) != 96:
        raise ValueError("Input arrays must have length 96")

    # Create time axis in hours, 96 points for a day
    time = [i / 4 for i in range(96)]

    # Convert power output from W to kW
    output_6ft_kw = [p / 1000 for p in output_6ft]
    output_19ft_kw = [p / 1000 for p in output_19ft]
    output_33ft_kw = [p / 1000 for p in output_33ft]

    # Set up the plot size
    plt.figure(figsize=(12, 6))

    # Plot wind power output at 6ft
    plt.plot(time, output_6ft_kw, label='6ft', color='#1f77b4', linestyle='-', linewidth=2)

    # Plot wind power output at 19ft
    plt.plot(time, output_19ft_kw, label='19ft', color='#ff7f0e', linestyle='--', linewidth=2)

    # Plot wind power output at 33ft
    plt.plot(time, output_33ft_kw, label='33ft', color='#2ca02c', linestyle='-.', linewidth=2)

    # Add title and labels
    plt.title('Wind Power Output at Different Heights')
    plt.xlabel('Time (hours)')
    plt.ylabel('Wind Power Output (kW)')
    plt.legend()

    # Set x-axis ticks every 4 hours
    plt.xticks(range(0, 25, 4))

    # Add grid
    plt.grid(True, linestyle='--', alpha=0.7)

    # Show the plot
    plt.show()

########----------------------------Solar_Nature------------------------------------##################
def draw_solar_nature(global_radiation, direct_radiation, diffuse_radiation, day):
    """
    Plot the natural attributes of photovoltaic including global radiation, direct radiation, and diffuse radiation
    with stacked bar chart and total radiation as a line chart.

    Parameters:
    global_radiation (list or array-like): Global radiation values, length 96
    direct_radiation (list or array-like): Direct radiation values, length 96
    diffuse_radiation (list or array-like): Diffuse radiation values, length 96

    Outputs:
    Displays a plot with stacked bar charts representing the global, direct, and diffuse radiation over a 24-hour period,
    and a line chart representing the total radiation.
    """

    # Ensure the input arrays have length 96
    if len(global_radiation) != 96 or len(direct_radiation) != 96 or len(diffuse_radiation) != 96:
        raise ValueError("Input arrays must have length 96")

    # Create time axis in hours, 96 points for a day
    time = np.arange(0, 24, 24 / 96)

    # Calculate total radiation
    total_radiation = np.array(global_radiation) + np.array(direct_radiation) + np.array(diffuse_radiation)

    # Set up the plot size
    fig, ax1 = plt.subplots(figsize=(12, 6))

    bar_width = 0.2  # Set a smaller bar width

    # Plot stacked bar chart
    ax1.bar(time, direct_radiation, label='Direct Radiation', color='#FF4500', width=bar_width, edgecolor='white')
    ax1.bar(time, diffuse_radiation, label='Diffuse Radiation', bottom=direct_radiation, color='#1E90FF', width=bar_width, edgecolor='white')
    ax1.bar(time, global_radiation, label='Global Radiation', bottom=np.array(direct_radiation) + np.array(diffuse_radiation), color='#FDB813', width=bar_width, edgecolor='white')

    # Add a second y-axis to plot the total radiation line chart
    ax2 = ax1.twinx()
    ax2.plot(time, total_radiation, label='Total Radiation', color='#006400', linestyle='-', linewidth=2)

    # Add title and labels
    ax1.set_title('Photovoltaic Natural Attributes (Day' + str(day) + ')', fontsize=16)
    ax1.set_xlabel('Time (hours)', fontsize=14)
    ax1.set_ylabel('Radiation (W/m²)', fontsize=14)
    ax2.set_ylabel('Total Radiation (W/m²)', fontsize=14)

    # Set x-axis ticks every 4 hours
    ax1.set_xticks(np.arange(0, 25, 4))

    # Add grid
    ax1.grid(True, linestyle='--', alpha=0.7)

    # Combine legends from both axes
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper left')

    # Show the plot
    plt.show()

########----------------------------Solar_Power------------------------------------##################
def plot_solar_wind_power(output_6ft, output_19ft, output_33ft, output_solar, day):
    """
        Plot wind and solar power output curves

        Parameters:
        output_6ft (list or array-like): Wind power output array at 6ft, length 96
        output_19ft (list or array-like): Wind power output array at 19ft, length 96
        output_33ft (list or array-like): Wind power output array at 33ft, length 96
        output_solar (list or array-like): Solar power output array, length 96
        """

    # Ensure the input arrays have length 96
    if len(output_6ft) != 96 or len(output_19ft) != 96 or len(output_33ft) != 96 or len(output_solar) != 96:
        raise ValueError("Input arrays must have length 96")

    # Create time axis in hours, 96 points for a day
    time = [i / 4 for i in range(96)]

    # Convert power output from W to kW
    output_6ft_kw = [p / 1000 for p in output_6ft]
    output_19ft_kw = [p / 1000 for p in output_19ft]
    output_33ft_kw = [p / 1000 for p in output_33ft]
    output_solar_kw = [p / 1000 for p in output_solar]

    # Set up the plot size
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot wind power output
    ax1.plot(time, output_6ft_kw, label='6ft Wind Power', color='#4682B4', linestyle='-', linewidth=2)
    ax1.plot(time, output_19ft_kw, label='19ft Wind Power', color='#32CD32', linestyle='--', linewidth=2)
    ax1.plot(time, output_33ft_kw, label='33ft Wind Power', color='#006400', linestyle='-.', linewidth=2)

    ax1.set_xlabel('Time (hours)', fontsize=14)
    ax1.set_ylabel('Wind Power Output (kW)', fontsize=14)
    ax1.set_xticks(range(0, 25, 4))
    ax1.grid(True, linestyle='--', alpha=0.7)

    # Add a second y-axis to plot the solar power output
    ax2 = ax1.twinx()
    ax2.plot(time, output_solar_kw, label='Solar Power', color='#FFA500', linestyle='-', linewidth=2)
    ax2.set_ylabel('Solar Power Output (kW)', fontsize=14)

    # Combine legends from both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    # Add title
    plt.title('Wind and Solar Power Output at Different Heights' + "(Day" + str(day)+")", fontsize=16)

    # Show the plot
    plt.show()


