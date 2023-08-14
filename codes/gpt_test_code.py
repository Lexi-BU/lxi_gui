import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Sample dataframe
df = pd.DataFrame({
    'Datetime': pd.date_range('2023-01-01', periods=100, freq='D'),
    'Key': np.random.choice(['A', 'B', 'C'], 100),
    'Value': np.random.randn(100)
})

key_list = df['Key'].unique()

# Iterate over each key
for key in key_list:
    # Filter data for the current key
    data = df[df['Key'] == key]

    # Create a 2x2 plot
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 8))

    # Plot 1: Time series data
    axes[0, 0].plot(data['Datetime'], data['Value'])
    axes[0, 0].set_xlabel('Datetime')
    axes[0, 0].set_ylabel('Value')
    axes[0, 0].set_title('Time Series')

    # Plot 2: Histogram
    axes[0, 1].hist(data['Value'], bins=10)
    axes[0, 1].set_xlabel('Value')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].set_title('Histogram')

    # Plot 3: Heatmap
    heatmap_data = data.pivot(index='Datetime', columns='Key', values='Value')
    sns.heatmap(heatmap_data, cmap='RdBu_r', ax=axes[1, 0])
    axes[1, 0].set_title('Heatmap')

    # Plot 4: Statistical values
    axes[1, 1].axis('off')
    stats_text = f"Key: {key}\n\n" \
                 f"Minimum Time: {data['Datetime'].min()}\n" \
                 f"Maximum Time: {data['Datetime'].max()}\n\n" \
                 f"Minimum Value: {data['Value'].min()}\n" \
                 f"Maximum Value: {data['Value'].max()}\n\n" \
                 f"10th Percentile: {data['Value'].quantile(0.1)}\n" \
                 f"25th Percentile: {data['Value'].quantile(0.25)}\n" \
                 f"50th Percentile: {data['Value'].median()}\n" \
                 f"75th Percentile: {data['Value'].quantile(0.75)}\n" \
                 f"90th Percentile: {data['Value'].quantile(0.9)}\n\n" \
                 f"Mean: {data['Value'].mean()}\n" \
                 f"Standard Deviation: {data['Value'].std()}\n" \
                 f"Skewness: {data['Value'].skew()}\n" \
                 f"Kurtosis: {data['Value'].kurtosis()}"

    axes[1, 1].text(0.5, 0.5, stats_text, ha='center', va='center', fontsize=10)

    # Adjust spacing between subplots
    plt.tight_layout()

    # Show the plot
    plt.show()
