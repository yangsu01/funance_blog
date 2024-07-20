In this post, we will see how CAPM can be implemented on market data and used to select investments. All of our following analysis will assume that the assumptions of CAPM hold.

This post builds upon the theory discussed in the previous post on the [Capital Asset Pricing Model](https://www.funance.lol/blog/4hX4HVhNTKvkluqxK8RsrU/CAPM). Give that a read first if you need a refresher.

## 1 CAPM and Regression

Before implementing the model, we need to first slightly adjust our approach.

As a quick review, CAPM describes a linear relationship between the excess expected returns of the market $(\mu_M - \mu_f)$ and the excess expected returns of an asset $(\mu_i - \mu_f)$. This is represented in the form of the Security Market Line (SML):

$$
(\mu_i - \mu_f) = \beta_i (\mu_M - \mu_f) \quad (1)
$$

Note I moved the intercept $\mu_f$ to the left hand side to represent the excess returns of the asset $(\mu_i - \mu_f)$. This results in a linear equation with no y-intercept which is beneficial for finding alpha. More on this later...

While this equation works well in theory, there is one main issue. We are taking the expected values of return, ie $E[R] = \mu$ where $R$ is the actual returns (expected value of a random variable is the same as taking the mean). As a result, information about the variance ($\sigma^2$) of the returns is lost.

When working with real world stock data, variance of the distrubution is important as it quantifies the *risk* associated with the asset.

Theres a simple solution to this: we can just fit a regression model of the market returns vs asset returns. Since equation (1) is linear, we will fit a simple linear regression model:

$$
R'_i = \alpha_i + \beta_i R'_M + \epsilon_i \quad (2)
$$

Where $R'_i = (R_i - R_f)$ and $R'_M = (R_M - R_f)$ are the actual excess returns of the market and asset $i$ (the risk-free rate is not constant over time), $\epsilon_i$ is the error term, and $\alpha_i, \beta_i$ are the intercept and slope fitted by the regression model.

A few interesting observations can be made here:

1. $\beta_i$ IS the beta of asset $i$
2. $\alpha_i$ IS the alpha of asset $i$
3. Taking the expected values of equation (2) gives us equation (1). Note the expected value of error term is $0$.

### 1.1 Types of Risk

Using equation (2), we can quantify the variance, or risk of asset $i$.

Taking the variance of both sides:

$$
Var(R'_i) = Var(\alpha_i + \beta_i R'_M + \epsilon_i) \quad (3)
$$

We can simplify the right hand side using some properties of variance:

$$
Var(X + Y) = Var(X) + Var(Y) + 2Cov(X,Y) \quad (4)
$$

Where $Cov(X,Y)$ is the covariance of $X$ and $Y$. Note the covariance of two *independent* random variables as well as the covariance of a random variable and a constant are both $0$. Additionally, we also have:

$$
Var(cX) = c^2Var(X) \quad (5)
$$

Where $c$ is a constant.

Using equations (4) and (5), we can simplify equation (3) to get:

$$
\sigma_i = \sqrt{\beta^2_i \sigma^2_M + \sigma^2_{\epsilon, i}} \quad (6)
$$

Where $\sigma_i$ is the standard deviation, or risk of asset $i$, $\sigma^2_M$ is the variance of the market returns, and $\sigma^2_{\epsilon, i}$ is the variance of the regression error term.

Notice how the total risk of asset $i$ can be broken down to two components: 

- $\beta^2_i \sigma^2_M$, known as the `Market Risk` or `Systematic Risk`. This is the risk inherent in the market
- $\sigma^2_{\epsilon, i}$, known as the `Unique Risk` or `Unsystematic Risk`. This is the risk *unique* to each asset, which implies that $\sigma^2_{\epsilon, i}$ and $\sigma^2_{\epsilon, j}$ are **independent** for $i \neq j$

You might spot the issue here. $\sigma^2_{\epsilon, i}$ is not always *unique*. For example, different assets in the same sector usually share some underlying risk beyond market risk. Another shortcoming of CAPM.

### 1.2 Minimizing Risk Through Diversification*

I will now show how risk can be minimized through diversification (theoretically...).

The proof is not important to understanding this post so you can skip to the next section, but before you go heres a **TL;DR**: Unique Risk can be minimized through diversification while Market Risk cannot.

Suppose we want to construct a portfolio of $N$ assets with returns $R_1, R_2, ... R_N$. The asset weights in the portfolio are $w_1, w_2, ... w_N$. From portfolio theory, we know the total returns of the portfolio, $R_P$ is:

$$
R_P = \sum_{i=1}^{N} w_i R_i \quad (7)
$$

We know that $R_i$ is:

$$
R_i = \mu_f + \beta_i (R_M - \mu_f) + \epsilon_i \quad (8)
$$

This is just equaion (2) rearranged (we assume the risk free rate is constant). Now plug equation (8) into equation (7):

$$
R_P = \sum_{i=1}^{N} \left[ \mu_f + \beta_i ( R_M - \mu_f ) + \epsilon_i \right] w_i \quad (9)
$$

We can expand this into:

$$
R_P = \mu_f + \sum_{i=1}^{N} \beta_i w_i (R_M - \mu_f) + \sum_{i=1}^{N} \epsilon_i w_i \quad (10)
$$

Note $\sum_{i=1}^{N} w_i = 1$. The Beta and Error term for this portfolio is then:

$$
\beta_P = \sum_{i=1}^{N} \beta_i w_i \quad (11)
$$

$$
\epsilon_P = \sum_{i=1}^{N} \epsilon_i w_i \quad (12)
$$

Lets now look at the two components of risk defined in equation (6):

$$
\text{Market Risk =} \left( \sum_{i=1}^{N} \beta_i w_i \right)^2 \sigma_M^2 \quad (13)
$$

$$
\text{Unique Risk =} \left( \sum_{i=1}^{N} \sigma_i w_i \right)^2 (14)
$$

Lets assume we put equal weights to each asset in our portfolio. This means: $w_i = \frac{1}{N}$.

Looking at each risk component separately, the *market risk* becomes:

$$
\text{Market Risk} = \left( \frac{\sum_{i=1}^{N} \beta_i}{N} \right)^2 \sigma_M^2 \quad (15)
$$

Taking the *limit* of this equation for $N \rightarrow \infty$, we see the market risk does not converge (numerator scales at the same rate as the denominator). So the **market risk cannot be reduced through diversification**.

On the other hand, if we assume the variance of the error term is constant: $\sigma_{\epsilon, i}^2 = \sigma_{\epsilon}^2$. The *unique risk* becomes:

$$
\text{Unique Risk} = \frac{1}{N} \frac{\sum_{i=1}^{N} \sigma_{\epsilon, i}^2}{N} = \frac{\bar{\sigma_{\epsilon}}^2}{N} = \frac{\sigma_{\epsilon}^2}{N} \quad (16)
$$

Where $\bar{\sigma_{\epsilon}}^2$ is the mean of $\sigma_{\epsilon}^2$.

*Finally*, taking the limit of equation (16)...

$$
\lim_{N\to\infty} \frac{\sigma_{\epsilon}^2}{N} = 0 \quad (17)
$$

Bam, nique risk can be eliminated (Theoretically). So... **unique risk can be ruduced through diversification**.

## 2 Fitting Regression Models

Thats enough theory for now, time to fit some models.

Here are the specifications I used:

- Returns of the S&P500 index are used as market returns
- Risk-Free Rate is taken as the history of 10 year US Treasury Bond yield
- Daily data from 2023-01-01 to 2023-12-31 was used to fit the models. 

The frequency and period of data used should be adjusted according to investment goals. For example, short-term, high frequency data (ex, 1 year of daily prices) can maybe capture current trends but is often noisy. Lower frequency data can smooth out the noise but you might lose some information in the process.

Lets start with an example. I will fit a simple linear regression model for `COST - Costco Wholesale Corporation` described in equation (2). Using `statsmodels.api.OLS`, here is the summary:

![ols-summary](./figures/ols-summary.png)
*Figure 1.CAPM Linear Regression Summary. Obtained using `statsmodels.api.OLS`*

Currently, we are interested in three pieces of information:

1. This shows us the fitted constants as seen in equation (2). *const* is the intercept (alpha), and *x1* is the slope (beta)
2. Here we have the p-values of the coefficients. For this example, using a threshold of 0.05, we can reject the Null Hypothesis that $\beta=0$ but we cannot reject $\alpha=0$. This means alpha is not statistically different from 0. Here are some videos on [Hypothesis Testing](https://youtu.be/0oc49DyA3hU?si=MKlJYfgGbNe2vYPR) and [P-Values](https://youtu.be/vemZtEM63GY?si=S8ic0EDq_fukPjpJ) by *StatsQuest* if you're confused.
3. $R^2$ tells us how 'good' the fit is. Heres an [Invesopedia Article](https://www.investopedia.com/terms/r/r-squared.asp) if you want to learn more. In the context CAPM, $R^2$ tells us what portion of the risk is due to the market. So in *Figure 1*, 30.6% of the total risk associated with `COST` is due to the market risk and 69.4% is due to the unique risk.

Lets plot it:

![cost-regression](./figures/cost-regression.png)
*Figure 2. Linear Regression of Market and COST Excess Returns*

Thats pretty good. Notice how since we are using daily data, theres some outliers that may impact the final fit.

## 3 Picking Stocks

Ok, so now what?

Recall the definition of alpha and beta:

- $\alpha$ measures whether the stock outperformed ($\alpha > 0$) or underperformed ($\alpha < 0$) relative to the market.
- $\beta$ tells us whether the stocks is risky ($\beta$ > 1) or safe ($\beta$ < 1) relative to the market.

Using this, we can devise a simple investment strategy:

1. Fit regression models on a bunch of stocks
2. Filter out the stocks with $\alpha > 0$ (and are also statistically different from 0). You can also add a restriction for $\beta$ or $R^2$ but I wont for now
3. Using the selected stocks, construct an optimized portfolio according to Modern Portfolio Theory
4. Profit

Pretty simple strategy... But there is one problem (aside from the issues of CAPM).

### 3.1 Are Alpha and Beta Constant?

One of the observations we made in the CAPM intro blog post is: beta (and alpha) are not always constant. This is an issue since our strategy relies on $\alpha > 0$ to select stocks.

Fortunately, we can test for that. One such way of testing whether alpha and beta are constant is using a sliding window:

- Create subsets of data using the main dataset. For consistency, keep the length of each subset the same
- Fit a regression model on each subset of data
- Record the alphas and betas to see whether they change over time

While this approach would work, its quite computationally intensive since we need to repeatidly fit multiple models for each stock we evaluate. This method does not scale well.

#### 3.1.1 Multiple Linear Regression*

This part is also optional. **TL;DR**: we will use Multiple Linear Regression to test whether $\alpha$ and $\beta$ change over time.

Here is another method which requires us to only fit one model for each stock, as outlined in Chapter 7.10 of *Statistics and Finance: An Introduction* by Ruppert, D (2004).

We will be using `Multiple Linear Regression`. Heres a [StatQuest video](https://youtu.be/EkAQAi3a4js?si=rRPb-To97PoWD-XZ) if you want to learn more. 

Assume both $\alpha$ and $\beta$ are not constant, ie, they change overtime. For simplicity, we will assume a linear time varying relationship.

While we can use a simple $y = mx + b$ to represent this, it would likely result in a very small slope $m$ which may not be statistically different from 0. This is because even if alpha and 

$$
\alpha_t = \alpha_0 + \alpha_1 t \quad (18)
$$

$$
\alpha_t = \alpha_0 + \alpha_1 t \quad (19)
$$