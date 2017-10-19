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

location_of_sqlite_full_text_database <- 'library_coverage_xml_and_fulltext_indicators.db'

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

library('bayesplot')
library('DBI')  # Load DBI to use RSQLite, following the RSQLite vignette
  # (https://cran.r-project.org/web/packages/RSQLite/vignettes/RSQLite.html)
library('RSQLite')
library('rstantools')
library('shinystan')

# Load data --------------------------------------------------------------------

# Load the original dois dataset:
doi_metadata_dataset <- read.table(
  location_of_original_tsv_datset,
  header = TRUE,
  sep = "\t",
  quote = "",
  strip.white = TRUE,
  stringsAsFactors = c(FALSE, TRUE)  # The two columns are DOI and O.A. color
)
# View(doi_metadata_dataset)  # Check the dataset visually

# Load the sqlite database that contains full-text holdings information:
fulltext_access_database <- dbConnect(
  RSQLite::SQLite(),
  location_of_sqlite_full_text_database
)
# dbListTables(fulltext_access_database)  # Check the list of database tables

# Get whatever full-text information we've stored in our sqlite database:
dois_and_full_text_indicator <- dbGetQuery(
  fulltext_access_database,
  'SELECT
    dois_table.doi,
    library_holdings_data.full_text_indicator
  FROM library_holdings_data
  JOIN dois_table
  ON library_holdings_data.doi_foreign_key = dois_table.database_id
  WHERE
    library_holdings_data.full_text_indicator IS NOT NULL'
)

dbDisconnect(fulltext_access_database)  # Close our connection with the database

# Join open-access color to the above:
full_doi_information_dataset <- merge(
  dois_and_full_text_indicator,
  doi_metadata_dataset,
  by = 'doi'
)
# View(full_doi_information_dataset)  # Check our work visually.

# Remove all duplicate DOIs except the *last* (i.e., most recently added to the
# database) instance of each:
full_doi_information_dataset <- full_doi_information_dataset[
  !duplicated(
    full_doi_information_dataset[, 'doi'],
    fromLast = T
  )
,]
# View(full_doi_information_dataset)  # Check our work visually.

# Summarize our dataset for the user -------------------------------------------

message("Our dataset has ", nrow(full_doi_information_dataset), " rows, each ",
  "of a unique doi (in cases of duplicate DOIs, only the last-listed instance ",
  "is retained)."
)

# Print a frequency table summarizing the different types of colors:
message("We have the following numbers of each type of Open Access color:"
)
message(paste0(capture.output(
  as.data.frame(
    table(
      full_doi_information_dataset[, c('oadoi_color')],
      dnn = 'Color'
    ),
    responseName = 'Frequency'
  )
), collapse = "\n"))


# Define a model for stan ------------------------------------------------------

# Below, we defined a basic stan model for a Bernoulli likelihood (data-
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
		N = nrow(full_doi_information_dataset),
		y = full_doi_information_dataset$full_text_indicator
	),
	iter = 1000,
	chains = 4,
	verbose = TRUE
)

# Analyze the stan output ------------------------------------------------------

## Explore the stan output manually --------------------------------------------

shinystan_object <- launch_shinystan(model_fit)

## Additional notes about interpreting this model ------------------------------

# Regarding the relationship between a Bayesian Credible Interval vs. a more
# standard Confidence Interval: From https://en.wikipedia.org/wiki/Credible_interval:
	# "For the case of a single parameter and data that can be summarised in a
  # single sufficient statistic, it can be shown that the credible interval and
  # the confidence interval will coincide if the unknown parameter is a location
  # parameter, with a prior that is a uniform flat distribution."

## Make some visualizations from the stan output -------------------------------

# This follows 
# http://mc-stan.org/bayesplot/reference/bayesplot-package.html#examples

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

# If we would like to get the Credible Interval ourselves, we can use the
# following:
# theta_posterior <- as.data.frame(posterior)$theta
# mean(theta_posterior)
# sd(theta_posterior)
# quantile(theta_posterior, c(.025, .50, .975))

