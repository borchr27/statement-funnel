# Project Information

## Description

This is a personal project I've been wanting to do for a while where the input is bank statements for a checking, credit card, savings, and potentially other account statements in csv format. The csv statements are then reformatted into a single format. Then we output the data into a common format into a csv file. This will allow for the data, now all in one place, to be analyzed and visualized. This project uses Python 3.10 with conda. 

## Running the Code

First add the end of the month statements into the data folder. Then modify the CONFIG in the `.envtemplate` file and rename the file to `.env`. Navigate to the main folder and run the following command: `python -m program.main`. Then fill in the necessary information when prompted. Then all the transaction data will be added to the `data/budget.csv` file to be consumed in a separate program.

## Testing

We use Pytest for testing where we have a few simple tests setup to test imports and check if the CONFIG file is being imported correctly using DotEnv.

## To Do

-   Account up to date for 2024 need to finish revolut and all other accounts for 2025
-   Add tests and debugging flag
-   Fix the messy if statements in the data import function
-   Create a web app to display the results
-   Add plot and analysis into this model
-   Connect LLM api for help labelling lo confidence tags

## To Done

-   Create machine learning model to handle the tags

## Label Structure (not all used)

- Income
- Fixed Expenses
  - housing
  - utilities
  - insurance
  - debt payments
  - subscriptions and memberships
- Variable Expenses
  - food
  - dining
  - events
  - health
  - clothes 
  - goods
  - misc
  - transport
  - vacation
  - education
- Investing (+Saving)
