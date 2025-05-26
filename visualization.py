import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv(r"D:\DS_project\assignment\historical_data.csv")  # adjust path as needed


buy_pnl  = df.loc[df['Side'] == 'BUY',  'Closed PnL'].dropna()
sell_pnl = df.loc[df['Side'] == 'SELL', 'Closed PnL'].dropna()

plt.figure(figsize=(8, 6))
box = plt.boxplot(
    [buy_pnl, sell_pnl],
    labels=['BUY', 'SELL'],
    patch_artist=True,
    showfliers=False
)


colors = ['#2ca02c',  # a richer green
          '#d62728']  # a rich red
for patch, color in zip(box['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_edgecolor('black')


plt.title("Closed PnL Distribution by Trade Side", fontsize=16, fontweight='bold')
plt.ylabel("Closed PnL (USD)", fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()


plt.savefig("buy_vs_sell_pnl.png", dpi=300)
plt.show()



df['win'] = df['Closed PnL'] > 0


counts = (
    df.groupby('Side')['win']
      .value_counts()
      .unstack(fill_value=0)
      .rename(columns={True: 'Profits', False: 'Losses'})
)


ax = counts.plot(
    kind='bar',
    figsize=(8, 6),
    color={'Profits': '#2ca02c', 'Losses': '#d62728'},
    width=0.7
)


ax.set_title("Number of Profits vs. Losses by Trade Side", fontsize=14, fontweight='bold')
ax.set_xlabel("Trade Side", fontsize=12)
ax.set_ylabel("Count of Trades", fontsize=12)
ax.legend(title="")
for p in ax.patches:
    ax.annotate(
        int(p.get_height()),
        (p.get_x() + p.get_width() / 2., p.get_height()),
        ha='center', va='bottom',
        fontsize=11
    )
plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig("profits_losses_by_side.png", dpi=300)
plt.show()




side_metrics = df.groupby('Side').agg(
    mean_pnl   = ('Closed PnL','mean'),
    win_rate   = ('win','mean'),
    trade_count= ('Closed PnL','size')
).reset_index()
print("\n=== Performance by Side ===\n", side_metrics)

plt.figure()
plt.bar(side_metrics['Side'], side_metrics['mean_pnl'])
plt.title("Average Closed PnL by Side")
plt.ylabel("Mean Closed PnL")
plt.xlabel("Side")
plt.tight_layout()
plt.savefig("chart_side_mean_pnl.png")

plt.figure()
plt.bar(side_metrics['Side'], side_metrics['win_rate'])
plt.title("Win Rate by Side")
plt.ylabel("Win Rate")
plt.xlabel("Side")
plt.tight_layout()
plt.savefig("chart_side_win_rate.png")


df['Hour'] = df['Timestamp'].dt.hour
hour_metrics = df.groupby('Hour').agg(mean_pnl=('Closed PnL','mean')).reset_index()
print("\n=== Mean PnL by Hour ===\n", hour_metrics)

plt.figure()
plt.plot(hour_metrics['Hour'], hour_metrics['mean_pnl'])
plt.title("Average Closed PnL by Hour of Day")
plt.ylabel("Mean Closed PnL")
plt.xlabel("Hour (IST)")
plt.tight_layout()
plt.savefig("chart_hourly_pnl.png")


coin_metrics = df.groupby('Coin').agg(
    mean_pnl   = ('Closed PnL','mean'),
    win_rate   = ('win','mean'),
    trade_count= ('Closed PnL','size')
).reset_index()
top10 = coin_metrics.sort_values('trade_count', ascending=False).head(10)
print("\n=== Top 10 Coins ===\n", top10)

plt.figure()
plt.bar(top10['Coin'], top10['mean_pnl'])
plt.title("Mean Closed PnL for Top 10 Coins")
plt.ylabel("Mean Closed PnL")
plt.xlabel("Coin")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("chart_top_coins_pnl.png")


df_sorted = df.sort_values('Timestamp')
df_sorted['cumulative_pnl'] = df_sorted['Closed PnL'].cumsum()
plt.figure()
plt.plot(df_sorted['Timestamp'], df_sorted['cumulative_pnl'])
plt.title("Cumulative Closed PnL Over Time")
plt.ylabel("Cumulative PnL")
plt.xlabel("Time (IST)")
plt.tight_layout()
plt.savefig("chart_cumulative_pnl.png")






df['Timestamp'] = pd.to_datetime(df['Timestamp IST'], format="%d-%m-%Y %H:%M")
df['Hour'] = df['Timestamp'].dt.hour

profit_by_acct = df.groupby('Account')['Closed PnL'].sum()

top5_accts    = profit_by_acct.nlargest(5).index
bottom5_accts = profit_by_acct.nsmallest(5).index

top5_hourly    = df[df['Account'].isin(top5_accts)].groupby('Hour')['Closed PnL'].mean()
bottom5_hourly = df[df['Account'].isin(bottom5_accts)].groupby('Hour')['Closed PnL'].mean()

plt.figure(figsize=(10,6))
plt.plot(top5_hourly.index,    top5_hourly.values,    color='green', label='Top 5 by Profit',   linewidth=2)
plt.plot(bottom5_hourly.index, bottom5_hourly.values, color='red',   label='Bottom 5 by Profit', linewidth=2)
plt.axhline(0, color='black', linestyle='--', linewidth=1)

plt.title("Avg. Closed PnL by Hour: Top 5 vs Bottom 5 Traders (by Total Profit)", 
          fontsize=14, fontweight='bold')
plt.xlabel("Hour of Day (IST, 0–23)", fontsize=12)
plt.ylabel("Average Closed PnL (USD)", fontsize=12)
plt.xticks(range(0,24,2))
plt.legend(loc="upper right", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()

plt.savefig("top5_vs_bottom5_by_profit.png", dpi=300)
plt.show()




total_profit = df.groupby('Account')['Closed PnL'].sum()
top5_accts    = total_profit.nlargest(5).index
bottom5_accts = total_profit.nsmallest(5).index


top5_trades    = df[df['Account'].isin(top5_accts)].copy()
bottom5_trades = df[df['Account'].isin(bottom5_accts)].copy()

top5_trades    = top5_trades.sort_values('Timestamp')
bottom5_trades = bottom5_trades.sort_values('Timestamp')

top5_trades['cumPnL']    = top5_trades['Closed PnL'].cumsum()
bottom5_trades['cumPnL'] = bottom5_trades['Closed PnL'].cumsum()

plt.figure(figsize=(12,6))
plt.plot(top5_trades['Timestamp'],    top5_trades['cumPnL'],    label="Top 5 Traders",    color='green', linewidth=2)
plt.plot(bottom5_trades['Timestamp'], bottom5_trades['cumPnL'], label="Bottom 5 Traders", color='red',   linewidth=2)

plt.title("Cumulative Closed PnL Over Time\nTop-5 vs. Bottom-5 Traders (by Total Profit)", 
          fontsize=14, fontweight='bold')
plt.xlabel("Time", fontsize=12)
plt.ylabel("Cumulative PnL (USD)", fontsize=12)
plt.legend(loc="upper left", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

# 7) Save or show
plt.savefig("cumulative_pnl_top5_vs_bottom5.png", dpi=300)
plt.show()


plt.figure(figsize=(10,6))
sns.scatterplot(x="value", y="Closed PnL", data=merged_df, alpha=0.1, edgecolor=None)
sns.regplot(x="value", y="Closed PnL", data=merged_df, 
            scatter=False, lowess=True, color="crimson", 
            line_kws={"lw":2, "alpha":0.8})

plt.title("Trade PnL vs. Fear/Greed Index (0–100)", fontsize=14, fontweight="bold")
plt.xlabel("Fear/Greed Index Value", fontsize=12)
plt.ylabel("Closed PnL (USD)", fontsize=12)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()


historical_df = pd.read_csv("historical_data.csv")
fear_greed_df = pd.read_csv("fear_greed_index.csv")

historical_df['Timestamp'] = pd.to_datetime(
    historical_df['Timestamp IST'],
    format="%d-%m-%Y %H:%M"
)
historical_df['trade_date'] = historical_df['Timestamp'].dt.date.astype(str)

fear_greed_df['date'] = pd.to_datetime(fear_greed_df['date']).dt.date.astype(str)


merged_df = historical_df.merge(
    fear_greed_df[['date', 'value', 'classification']],
    left_on='trade_date',
    right_on='date',
    how='left'
)

plt.figure(figsize=(10,6))
sns.scatterplot(x="value", y="Closed PnL", data=merged_df, alpha=0.1, edgecolor=None)
sns.regplot(x="value", y="Closed PnL", data=merged_df, 
            scatter=False, color="crimson", 
            line_kws={"lw":2, "alpha":0.8})


plt.title("Trade PnL vs. Fear/Greed Index (0–100)", fontsize=14, fontweight="bold")
plt.xlabel("Fear/Greed Index Value", fontsize=12)
plt.ylabel("Closed PnL (USD)", fontsize=12)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()


