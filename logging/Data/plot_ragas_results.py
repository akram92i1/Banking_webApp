import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_results():
    csv_file = "ragas_evaluation_results.csv"
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found.")
        return
        
    df = pd.read_csv(csv_file)
    
    # We will plot the average scores across all questions
    metrics = ["faithfulness", "answer_relevancy"]
    
    # Drop rows where metrics might be NaN (if evaluation failed for a row)
    df_clean = df.dropna(subset=metrics)
    
    if df_clean.empty:
        print("No valid metric scores found to plot.")
        return
        
    averages = df_clean[metrics].mean().reset_index()
    averages.columns = ["Metric", "Average Score"]
    
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(8, 6))
    
    ax = sns.barplot(x="Metric", y="Average Score", data=averages, palette="viridis", hue="Metric", legend=False)
    plt.ylim(0, 1.1)
    plt.title("Ragas Evaluation Metrics: Average Scores", fontsize=14, pad=15)
    plt.ylabel("Score", fontsize=12)
    plt.xlabel("Metric", fontsize=12)
    
    # Add data labels
    for index, row in averages.iterrows():
        ax.text(index, row["Average Score"] + 0.02, round(row["Average Score"], 3), 
                color='black', ha="center", fontweight='bold')
        
    output_file = "ragas_metrics_plot.png"
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Plot successfully saved to: {output_file}")

if __name__ == "__main__":
    plot_results()
