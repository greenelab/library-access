# TODO(jlevern) Copyright statement placeholder
#   Portions of this code (marked below) are based on a stan model released 
#   by Bob Carpenter in 2012 under a "new BSD license" (i.e., a BSD 3-Clause
#   license).
# TODO(jlevern) Author placeholder
# TODO(jlevern) File description placeholder

# Settings ---------------------------------------------------------------------

# The location of the tsv dataset with DOI information (specifically, the
# DOI open access "colors"). This will be used below to allow subsetting data based on those colors.
location_of_original_tsv_datset <- 'Datasets/State_of_OA/state-of-oa-dois.tsv'

sqlite_database_with_library_holdings_information <- 'library_coverage_xml_and_fulltext_indicators.db'

# Load packages ----------------------------------------------------------------

## Load rstan ------------------------------------------------------------------

# rstan can be finicky to install (in Linux), so I've included an
# extended comment below to facilitate the process.

# Per https://github.com/stan-dev/rstan/wiki/Installing-RStan-on-Mac-or-Linux,
# rstan should be installed with the following:
# install.packages("rstan", repos = "https://cloud.r-project.org/", dependencies=TRUE)

# If you encounter an error about "lang__grammars__expression_grammar_inst" (or
# something similar) when installing rstan, doing the following may help to
# resolve it:
# - Create a file called ~/.R/Makevars, and add to it the following:
#   CXXFLAGS=-DBOOST_PHOENIX_NO_VARIADIC_EXPRESSION
#   This follows 
#   https://github.com/stan-dev/rstan/issues/447#issuecomment-325172186
# - Also, following 
#   http://sites.psu.edu/theubunturblog/2012/09/03/installing-rstan-in-ubuntu/,
#   install r-cran-rcpp and r-cran-inline using your system's package manager
#   (those are the Ubuntu package names).

# This follows the guide for loading rstan at
# http://mc-stan.org/workshops/ASA2016/day-1.pdf
library(rstan)
rstan_options(auto_write = TRUE)
options(mc.cores = parallel::detectCores())

## Load other packages ---------------------------------------------------------

library('shinystan')
library('bayesplot')
library('rstantools')

# Load data --------------------------------------------------------------------

sample_size <- 10000

probability_of_yes <- round(
	runif(1, min = 0, max = 1), 
	digits = 2
)

dataset <- data.frame(
	"Item_ID_Number" = 1:sample_size,
	"Do_We_Have_the_Item" = rbinom(
		n = sample_size, 
		size = 1, 
		prob = probability_of_yes
	)
)
# View(example_binary_data)

# Define a model for stan ------------------------------------------------------

# Below is defined a basic stan model for a Bernoulli likelihood (data-
# generating) function, with a flat beta-distributed prior:
# This comes from the stan developers' examples, at
# https://github.com/stan-dev/example-models/blob/master/basic_estimators/bernoulli.stan,
# which, per https://github.com/stan-dev/example-models, is released under a
# New BSD License, copyright Bob Carpenter 2012.
stan_model <- "
data { 
  int<lower=0> N;
  int<lower=0,upper=1> y[N];
} 
parameters {
  real<lower=0,upper=1> theta;
} 
model {
  theta ~ beta(1,1); // A flat prior
  for (n in 1:N)
    y[n] ~ bernoulli(theta);
}
"

# Run the stan model -----------------------------------------------------------

model_fit <- stan(
	model_code = stan_model,
	model_name = "Bernoulli likelihood, Beta(1,1) Prior",
	data = list(
		N = length(dataset$Do_We_Have_the_Item),
		y = dataset$Do_We_Have_the_Item
	),
	iter = 1000,
	chains = 4,
	verbose = TRUE
)

# Explore the stan output manually ---------------------------------------------

shinystan_object <- launch_shinystan(model_fit)

# NOTE WELL re: a credible interval vs. a confidence interval: From https://en.wikipedia.org/wiki/Credible_interval:
	# "For the case of a single parameter and data that can be summarised in a single sufficient statistic, it can be shown that the credible interval and the confidence interval will coincide if the unknown parameter is a location parameter, with a prior that is a uniform flat distribution."

# Make some visualizations, following http://mc-stan.org/bayesplot/reference/bayesplot-package.html#examples

posterior <- as.matrix(model_fit)

plot_title <- ggtitle(
	"Posterior distribution",
  "with median and 95% credible interval"
)
mcmc_areas(
	posterior,
  pars = c("theta"),
  prob = 0.95
) + 
plot_title


