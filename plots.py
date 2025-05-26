import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
hist_df = pd.read_csv("historical_data.csv")
f_g_df = pd.read_csv("fear_greed_index.csv")

hist_df['Timestamp'] = pd.to_datetime(hist_df['Timestamp IST'], format="%d-%m-%Y %H:%M")
hist_df['Hour'] = hist_df['Timestamp'].dt.hour
hist_df['win'] = hist_df['Closed PnL'] > 0

f_g_df['date'] = pd.to_datetime(f_g_df['date']).dt.date.astype(str)
hist_df['trade_date'] = hist_df['Timestamp'].dt.date.astype(str)
merged_df = hist_df.merge(f_g_df[['date','value','classification']], left_on='trade_date', right_on='date', how='left')

# Plot 1: Closed PnL Distribution by Trade Side
buy_pnl = hist_df[hist_df['Side']=="BUY"]['Closed PnL'].dropna()
sell_pnl = hist_df[hist_df['Side']=="SELL"]['Closed PnL'].dropna()
plt.figure(figsize=(8,6))
b = plt.boxplot([buy_pnl, sell_pnl], labels=["BUY","SELL"], patch_artist=True, showfliers=False)
for patch,color in zip(b['boxes'],["#2ca02c","#d62728"]):
    patch.set_facecolor(color)
    patch.set_edgecolor("black")
plt.title("Closed PnL Distribution by Trade Side")
plt.ylabel("Closed PnL (USD)")
plt.grid(axis="y", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig("buy_vs_sell_pnl.png")
plt.show()

# Plot 2: Number of Profits vs Losses by Trade Side
counts = hist_df.groupby("Side")['win'].value_counts().unstack(fill_value=0).rename(columns={True:"Profits",False:"Losses"})
ax = counts.plot(kind="bar", figsize=(8,6), color={"Profits":"#2ca02c","Losses":"#d62728"}, width=0.7)
for p in ax.patches:
    ax.annotate(int(p.get_height()), (p.get_x()+p.get_width()/2., p.get_height()), ha="center", va="bottom")
plt.title("Number of Profits vs. Losses by Trade Side")
plt.ylabel("Count of Trades")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("profits_losses_by_side.png")
plt.show()

# Plot 3: Average Closed PnL by Side
side_metrics = hist_df.groupby("Side").agg(mean_pnl=("Closed PnL","mean"), win_rate=("win","mean")).reset_index()
plt.figure(figsize=(8,4))
plt.bar(side_metrics['Side'], side_metrics['mean_pnl'])
plt.title("Average Closed PnL by Side")
plt.ylabel("Mean Closed PnL")
plt.tight_layout()
plt.savefig("chart_side_mean_pnl.png")
plt.show()

# Plot 4: Win Rate by Side
plt.figure(figsize=(8,4))
plt.bar(side_metrics['Side'], side_metrics['win_rate'])
plt.title("Win Rate by Side")
plt.ylabel("Win Rate")
plt.tight_layout()
plt.savefig("chart_side_win_rate.png")
plt.show()

# Plot 5: Average Closed PnL by Hour of Day
hour_metrics = hist_df.groupby("Hour").agg(mean_pnl=("Closed PnL","mean")).reset_index()
plt.figure(figsize=(8,4))
plt.plot(hour_metrics['Hour'], hour_metrics['mean_pnl'])
plt.title("Average Closed PnL by Hour of Day")
plt.xlabel("Hour (IST)")
plt.ylabel("Mean Closed PnL")
plt.tight_layout()
plt.savefig("chart_hourly_pnl.png")
plt.show()

# Plot 6: Mean Closed PnL for Top 10 Coins
coin_metrics = hist_df.groupby("Coin").agg(mean_pnl=("Closed PnL","mean"), trade_count=("Closed PnL","size")).reset_index()
top10 = coin_metrics.sort_values("trade_count", ascending=False).head(10)
plt.figure(figsize=(8,4))
plt.bar(top10['Coin'], top10['mean_pnl'])
plt.title("Mean Closed PnL for Top 10 Coins")
plt.ylabel("Mean Closed PnL")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("chart_top_coins_pnl.png")
plt.show()

# Plot 7: Cumulative Closed PnL Over Time
df_sorted = hist_df.sort_values("Timestamp")
df_sorted['cumPnL'] = df_sorted['Closed PnL'].cumsum()
plt.figure(figsize=(10,4))
plt.plot(df_sorted['Timestamp'], df_sorted['cumPnL'])
plt.title("Cumulative Closed PnL Over Time")
plt.ylabel("Cumulative PnL (USD)")
plt.xlabel("Time (IST)")
plt.tight_layout()
plt.savefig("chart_cumulative_pnl.png")
plt.show()

# Plot 8: Avg Closed PnL by Hour: Top 5 vs Bottom 5 Traders (by Total Profit)
profit_by_acct = hist_df.groupby("Account")['Closed PnL'].sum()
top5 = profit_by_acct.nlargest(5).index
bot5 = profit_by_acct.nsmallest(5).index
top5_hr = hist_df[hist_df['Account'].isin(top5)].groupby("Hour")['Closed PnL'].mean()
bot5_hr = hist_df[hist_df['Account'].isin(bot5)].groupby("Hour")['Closed PnL'].mean()
plt.figure(figsize=(8,4))
plt.plot(top5_hr.index, top5_hr.values, color="green", label="Top 5 by Profit")
plt.plot(bot5_hr.index, bot5_hr.values, color="red", label="Bottom 5 by Profit")
plt.axhline(0, color="black", linestyle="--")
plt.title("Avg Closed PnL by Hour: Top 5 vs Bottom 5")
plt.xlabel("Hour (IST)")
plt.ylabel("Avg Closed PnL (USD)")
plt.legend()
plt.tight_layout()
plt.savefig("top5_vs_bottom5_by_profit.png")
plt.show()

# Plot 9: Cumulative Closed PnL Over Time: Top 5 vs Bottom 5 Traders
top5_trades = hist_df[hist_df['Account'].isin(top5)].sort_values("Timestamp")
bot5_trades = hist_df[hist_df['Account'].isin(bot5)].sort_values("Timestamp")
top5_trades['cumPnL'] = top5_trades['Closed PnL'].cumsum()
bot5_trades['cumPnL'] = bot5_trades['Closed PnL'].cumsum()
plt.figure(figsize=(10,4))
plt.plot(top5_trades['Timestamp'], top5_trades['cumPnL'], color="green", label="Top 5 Traders")
plt.plot(bot5_trades['Timestamp'], bot5_trades['cumPnL'], color="red", label="Bottom 5 Traders")
plt.title("Cumulative PnL: Top-5 vs Bottom-5 Traders")
plt.ylabel("Cumulative PnL (USD)")
plt.xlabel("Time (IST)")
plt.legend()
plt.tight_layout()
plt.savefig("cumulative_pnl_top5_vs_bottom5.png")
plt.show()

# Plot 10: Trade PnL vs Fear/Greed Index (0-100)
plt.figure(figsize=(8,4))
sns.scatterplot(x="value", y="Closed PnL", data=merged_df, alpha=0.1, edgecolor=None)
sns.regplot(x="value", y="Closed PnL", data=merged_df, scatter=False, lowess=True, color="crimson", line_kws={"lw":2})
plt.title("Trade PnL vs Fear/Greed Index (0-100)")
plt.xlabel("Fear/Greed Index Value")
plt.ylabel("Closed PnL (USD)")
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig("pnl_vs_sentiment.png")
plt.show()
