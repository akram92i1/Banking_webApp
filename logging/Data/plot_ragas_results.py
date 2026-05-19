import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_results():
    original_csv = "ragas_evaluation_results.csv"
    mmr_csv = "ragas_evaluation_results_mmr.csv"
    
    dfs = []
    
    if os.path.exists(original_csv):
        df_orig = pd.read_csv(original_csv)
        df_orig['System'] = 'Original'
        dfs.append(df_orig)
        
    if os.path.exists(mmr_csv):
        df_mmr = pd.read_csv(mmr_csv)
        df_mmr['System'] = 'MMR Optimized'
        dfs.append(df_mmr)
        
    if not dfs:
        print(f"Error: Neither {original_csv} nor {mmr_csv} were found.")
        return
        
    df_all = pd.concat(dfs, ignore_index=True)
    metrics = ["faithfulness", "answer_relevancy"]
    df_clean = df_all.dropna(subset=metrics)
    
    if df_clean.empty:
        print("No valid metric scores found to plot.")
        return
        
    # Melt the dataframe for seaborn grouped bar plot
    df_melt = df_clean.melt(id_vars=['System'], value_vars=metrics, var_name='Metric', value_name='Score')
    
    # Calculate averages
    averages = df_melt.groupby(['System', 'Metric'])['Score'].mean().reset_index()
    
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))
    
    ax = sns.barplot(x="Metric", y="Score", hue="System", data=averages, palette="viridis")
    plt.ylim(0, 1.1)
    plt.title("Ragas Evaluation Metrics: Original vs MMR Optimized", fontsize=14, pad=15)
    plt.ylabel("Average Score", fontsize=12)
    plt.xlabel("Metric", fontsize=12)
    
    # Add data labels
    for p in ax.patches:
        ax.annotate(format(p.get_height(), '.3f'), 
                   (p.get_x() + p.get_width() / 2., p.get_height()), 
                   ha = 'center', va = 'center', 
                   xytext = (0, 9), 
                   textcoords = 'offset points',
                   fontweight='bold')
        
    output_file = "ragas_metrics_comparison_plot.png"
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Comparison plot successfully saved to: {output_file}")

if __name__ == "__main__":
    plot_results()
