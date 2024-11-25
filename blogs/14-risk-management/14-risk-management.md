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
\widehat{\text{VaR}}_{np}(\alpha) = -S \widehat{q}(\alpha) \enspace(3)
$$

Where $S$ is the value of the position you hold and $\widehat{q}(\alpha)$ is the lower $\alpha$ sample quantile of the sample historical returns. Note "$\widehat{x}$" just means $x$ is an estimation from a sample.

And:

$$
\widehat{\text{ES}}_{np} = -S \frac{\sum_{i=1}^{n} I[R_i < \widehat{q}(\alpha)] R_i}{\sum_{i=1}^{n} I[R_i < \widehat{q}(\alpha)]} \enspace (4)
$$

Where $R_i$ is the $i$ the return and $I[R_i < \widehat{q}(\alpha)] = 1$ when $R_i < \widehat{q}(\alpha)$ and 0 otherwise. Basically, we are taking the average of all the returns less than $\widehat{q}(\alpha)$.

Using `COST - Costco Wholesale Corporation` as an example, here is the distribution of returns over the last 5 years:

![historical returns](./figures/historical_returns.png)

_Figure 1. Distribution of Returns and Non-Parametric Estimations for VaR and ES Quantiles_

Assuming we have a \$10000 worth of the stock, the VaR and ES for a 1 day period (we are using daily returns) can be found using _equations 3, 4_:

- VaR(0.01) = \$418.52
- ES(0.01) = \$617.33

So, if I hold a \$10000 long position in _COST_, I would expect a loss greater than \$418.45 1% of days (every 100 trading days). Furthermore, in the worst 1% of days, I expect an average loss of \$617.33.

VaR and ES allows us to quantify the down side risks associated with investments. Using it, we can compare different alternatives and adjust positions according to our personal `risk tolerance`.

## 2 Parametric Estimations

Another approach to calculating VaR and ES is using a parametric estimation where we first fit the sample data to a known distribution, then calculate the metrics using the fitted parameters. This approach allows us get reliable results with smaller sample sizes and can be used to estimate the VaR and ES in more complex applications.

### 2.1 The t-distribution

Starting off, lets check if the returns follow a `normal distribution`:

![normal distribution](./figures/normal_distribution.png)
_Figure 2. Distribution of Historical Returns Compared to a Normal Distribution_

Looking at the lower quantiles of the normal QQ plot, you can see that the observed values are more extreme than the theoretical quantiles of the normal distribution. So using it would underestimate the potential losses and lead to overconfidence.

A better alternative would be the `t-distribution` which generalizes the normal distribution by adding an additional parameter that describes the tails known as the `degrees of freedom` $\nu$. To fit the data to a t-distribution and find the parameters $\mu, \lambda, \nu$, we can use a `maximum likelihood estimation (MLE)` (watch this [video](https://youtu.be/XepXtl9YKwc?si=hUGVuNaQiSW42kkW) to learn more about MLE). Here are the results:

![t-distribution](./figures/t-distribution.png)
_Figure 3. Distribution of Historical Returns Compared to a t-distribution_

Still not perfect, but a lot better than before. The `scale parameter` $\lambda$ is not necessarily equal to the standard deviation $\sigma$. To convert $\lambda$ to $\sigma$, we can use:

$$
\widehat{\sigma} = \widehat{\lambda} \sqrt{\widehat{\nu} / (\widehat{\nu} - 2)} \enspace (5)
$$

Note that for $\nu \rightarrow \infty$, $\sigma = \lambda$ and the t-distribution becomes the normal distribution.

Assuming the returns are independent and identically distributed (i.i.d.), VaR and ES can be calculated using the fitted parameters with the following equations:

$$
\widehat{\text{VaR}}_t (\alpha) = -S (\widehat{\mu} + q_{\alpha}(\widehat{\nu}) \widehat{\lambda}) \enspace (6)
$$

Where $q_{\alpha}(\widehat{\nu})$ is the $\alpha$-quantile of the standard t-distribution with $\nu$ degrees of freedom.

And:

$$
\widehat{ES}_t (\alpha) = S \left( -\widehat{\mu} + \widehat{\lambda} \frac{f_{\widehat{\nu}} [q_{\alpha}(\widehat{\nu})] [\widehat{\nu} + q_{\alpha}(\widehat{\nu})^2]}{\alpha (\widehat{\nu} - 1)} \right) \enspace (7)
$$

where $f_{\widehat{\nu}}$ is the probability density function of the standard t-distribution.

Using _equations 6, 7_, we get:

- VaR(0.01) = \$394.01
- ES(0.01) = \$581.91

A slight underestimate compared to the non-parametric estimate.

### 2.2 Parametric Estimations for a Portfolio

As mentioned previously, parametric estimations allow us to calculate VaR and ES for complex applications such as portfolios.

## 3 Confidence Intervals

## 4 Limitations

## 5 Conclusions
