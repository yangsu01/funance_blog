In past posts, we have looked at two types of investment strategies: active trading (pairs trading, ARIMA forecasting) and portfolio allocation (PCA+FA, CAPM). While some of the strategies seemed promising, the posts primarily focused on the theory. There was no standardized way of evaluating the effectiveness or robustness of the strategies.

So thats what we're focusing on today: how you can evaluate different investment strategies.

## 1 Example - EWMAC

I will be using `exponentially weighted moving average crossovers (EWMAC)` as an example. **EWMAC** is a popular trend-following trading strategy that uses two exponentially weighted moving averages (one long and one short) to generate trading signals based on **momentum**. Each EWMA is calculated using:

$$
\text{EWMA}_t = \alpha P_t + (1 - \alpha) \text{EWMA}_{t-1} \enspace (1)
$$

$$
\alpha = \frac{2}{N+1} \enspace (2)
$$

Where $P_t$ is the price at time $t$ and $N$ is the number of periods in the lookback window. The difference between EWMA and **simple moving average (SMA)** is that more weight is is put on recent prices ($\alpha P_t + \alpha (1-\alpha) P_{t-1} + \alpha (1-\alpha)^2 P_{t-2} ...$).

The signals are as follows:

- Buy (long) when **short EWMA** crosses above **long EWMA**. This indicates an uptrend in the price
- Sell (short) when **long EWMA** crosses above **short EWMA**. This indicates a downtrend in the price

Heres an example of trading **SPY** using a short window of 16 days and long window of 64 days.

![ewmac-signals](./figures/ewmac-signals.png)
_Figure 1. EWMAC Signals on SPY using Long Window of 16 Days and Short Window of 64 Days. No Shorting_

Since this post is focused on trading rule evaluation, I will just use the same windows moving forward and not worry about optimizing the strategy.

## 2 Comparing Strategies

Alright, now that we have the trading rules, how would you evaluate how profitable it is?

The first step I would take is to do a simple backtest. Since EWMAC is a trend-following rule, it would likely perform differently under different market conditions (bull, bear, sideways...). Using a large range of data would produce more realistic results so I used the daily prices from 1999-2024. Here is the portfolio value over time:

![ewmac-portfolio-value](./figures/ewmac-portfolio-value.png)
_Figure 2. Backtested Portfolio Value of EWMAC on SPY_

Cool, but this doesn't tell us much. To quantify the performance, we need to compare it to some alternatives...

### 2.1 Quantifying Performance

Interestingly, you can analyze trading rules the same way you analyze stocks: by looking at its returns. This allows us to directly compare different rules and strategies. You can even take this one step further by creating a trading strategy using a portfolio of trading rules constructed with portfolio theory. But thats another post for another day...

Comparing EWMAC to holding the stock:

|                   | Mean Returns | Annual Returns | Annual Volatility |
| :---------------- | :----------- | :------------- | :---------------- |
| **EWMAC (16/64)** | 0.02124%     | 5.497%         | 11.59%            |
| **Buy and Hold**  | 0.03084%     | 8.081%         | 19.39%            |

_Table 1. Returns and Volatility (standard deviation) of EWMAC and Holding SPY_

Holding SPY would have more returns but also involves more risk. To take that into account, we can use the risk adjusted returns, or **Sharpe Ratio**. EWMAC has a Sharpe Ratio of **0.1852** and holding SPY has a Sharpe Ratio of **0.1939**.

### 2.2 Distribution of Returns

If the data is normally distributed, we could just stop here. Unfortunately, this is often not the case as financial time series tend to have **heavy tails**, meaning outliers occur more frequently. Only looking at the mean and standard deviation of returns can lead to overconfidence and unexpected losses.

Studying the distribution of returns can help you understand the **risk profile** of the investment strategy. Heres a plot of the backtested EWMAC returns:

![returns-distribution](./figures/returns-distribution.png)
_Figure 3. Distribution of Backtested Returns of EWMAC_

The histogram and kernel density estimation (KDE) gives us an approximation of the sample distribution while the normal QQ (quantile-quantile) plot compares the sample distribution to a normal distribution. Heres a few metrics you can use to quantify this:

`Skew` is a measure of symmetry around the mean. A trading strategy with **positive skew** has frequent small losses with occasional large gains (ex. trend following) while a strategy with **negative skew** has frequent small gains with rate large losses (ex. pairs trading). Understanding the skew of your investment strategy can help you estimate the expected risks.

Additionally, when you have highly skewed data, using the **mean** as a performance metric may lead to unrealistic expectations. In such cases, the **median** could be a better estimator. From the histogram and KDE, it seems that the backtested returns have no obvious skew.

`Kurtosis` measures the frequency of outliers in the data. As mentioned above, financial time series often have **heavy tails**. From the normal QQ plot, we can see this is indeed the case as there are more extreme values when compared to a normal distribution.

We can confirm these graphical observations by calculating the values numerically:

|                         | Skew     | Kurtosis |
| :---------------------- | :------- | :------- |
| **EWMAC (16/64)**       | -0.4922  | 5.596    |
| **Buy and Hold**        | -0.01314 | 11.27    |
| **Normal Distribution** | 0        | 3        |

_Table 2. Skew and Kurtosis of EWMAC and Holding SPY_

So from the backtest results, EWMAC using a short window of 16 days and a long window of 64 days on SPY has a slightly negative skew. When compared to just holding SPY, EWMAC has less extreme returns.

We can dive deeper and look into **risk management** but that will be a topic for a future post.

## 3 Robustness of Backtests

Again, you could stop here; we calculated the performance metrics (mean, volatility, Sharpe Ratio) and risk profile (skew, kurtosis) by backtesting the trading rule. Now you can use these values to compare different variations and strategies.

How much can we trust the results from the backtest? Since the data we used was a random sample of the overall population, the metrics we calculated from it are also random samples. Sure, using a large amount of data could minimize some of the error due to the **law of large numbers** but there still may be some underlying bias. Different samples would likely produce different backtested results. How do we know the ones we got are 'realistic'?

While in past posts, I have **walk-forward tests** to achieve this, today, we will look at a more statistical approach: **bootstrapping**.

Specifically, I referring to `non-parametric bootstrapping` which is a resampling method used to generate different price series by sampling the original time series **with replacement** (meaning each datapoint can be sampled multiple times). Since each sample is generated from the original data, it maintains the same distribution. By then applying the backtest to each sample and re-calculating the metrics, we can test the robustness of the trading rule by looking at the cofidence interval and other statistics.

Still with me? Alright, let's walk through the specific steps...

1. Resample historical returns with replacement. *An alternative would be to first fit the data (likely some **t-distribution**) then sample according to the **PDF (probability density function)**. This is known as **parametric bootstrapping**.*

2. 

## 4 Conclusion
