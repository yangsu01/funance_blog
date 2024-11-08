`Risk Management` is an area often overlooked by retail investors. When evaluating assets, portfolios, or trading rules, we tend to focus on the _potential profitability_ (expected returns, volatility, Sharpe Ratio...). However, as discussed in my post on [_evaluating investment strategies_](https://www.funance.lol/blog/4ejCfGO8EcB1OF3SUrtFbn/evaluating-strategies), only looking at these metrics can lead to large unexpected losses as financial returns tend to have fat tails. This likelihood of extreme losses is known as `tail risk` and its often caused by unexpected events such as market crashes. Understanding and accounting for the various types of risk is a vital part of risk management.

So today, lets start off by looking at some of the metrics used in risk management and how they can be used in our own investment portfolios.

## 1 VaR and ES

The two most widely used metrics in risk management are `Value at Risk (VaR)` and `Expected Shortfall (ES)` (also referred to as `Conditional Value at Risk (CVaR)`).

**VaR** is defined by two parameters, the time horizon $T$ and confidence level $\alpha$. It basically answers the question: _"Over a period of $T$, how much money would I lose in the worst $\alpha$ percent of cases?"_ So if a portfolio has $\text{VaR}(0.01, 1\text{ day}) = \$1000$, then there is a $1\%$ chance of a loss exceeding \$1000 over the next day. Putting this into an equation:

$$
P\left[ L \geq \text{VaR}(\alpha) \right] = \alpha \enspace (1)
$$

Where $L$ is the loss over period $T$.

**ES** then answers the question: _"What is the average amount of money I would lose if the loss exceeds the VaR threshold?"_ So $\text{ES}(0.01) = \$1500$ means in the worst 1% of cases, I would lose on average \$1500. This can be described as:

$$
\text{ES}(\alpha) = E \left[ L \mid L \geq \text{VaR}(\alpha) \right] \enspace (2)
$$

### 1.1 Non-Parametric Estimations

The most straightforward method of calculating VaR and ES is using non-parametric estimation where we directly calculate the metrics using historical data.

Using this method, we can modify _equations 1, 2_ as:

$$
\text{VaR}_{np}(\alpha) = -S q(\alpha) \enspace(3)
$$

Where $S$ is the value of the position you hold and $q(\alpha)$ is the lower $\alpha$ sample quantile of the sample historical returns.

And:

$$
\text{ES}_{np} = -S \frac{\sum_{i=1}^{n} I[R_i < q(\alpha)] R_i}{\sum_{i=1}^{n} I[R_i < q(\alpha)]} \enspace (4)
$$

Where $R_i$ is the $i$ the return and $I[R_i < q(\alpha)] = 1$ when $R_i < q(\alpha)$ and 0 otherwise. Basically, we are taking the average of all the returns less than $q(\alpha)$.

Using `COST - Costco Wholesale Corporation` as an example, here is the distribution of returns over the last 5 years:

![historical returns](./figures/historical_returns.png)

_Figure 1. Distribution of Returns for COST_

Assuming we have a \$10000 worth of the stock, the VaR and ES for a 1 day period (we are using daily returns) can be found using _equations 3, 4_:

- VaR(0.01) = \$418.52
- ES(0.01) = \$617.33

So, if I hold a \$10000 long position in _COST_, I would expect a loss greater than \$418.45 1% of days (every 100 trading days). Furthermore, in the worst 1% of days, I expect an average loss of \$617.33.

VaR and ES allows us to quantify the down side risks associated with investments. Using it, we can compare different alternatives and adjust positions according to our personal `risk tolerance`.

## 2 Parametric Estimations

Another approach to calculating VaR and ES is using a parametric estimation where we first fit the sample data to a distribution, then calculate the metrics using the fitted distribution. This approach allows us

### 2.1 The t-distribution

Since we are focusing on the "tails", we cannot just assume the returns have a normal or log-normal distribution.

## 3 Confidence Intervals

## 4 Limitations

## 5 Conclusions
