# Project Information

## Description

This is a personal project I've been wanting to do for a while where the input is bank statements for a checking, credit card, and potentially other account statements in csv format. The csv statements are then reformatted into a single format. This will allow for the data, now all in one place, to be analyzed and visualized. This project uses Python 3.9.17.

## Running the Code

First add the end of the month statements into the data folder one csv file should have the word `Checking` somewhere in the filename and then (for now) it is assumed that the other file is the credit card transaction data. Navigate to the main folder and run the following command: `python -m program.main`. Then fill in the necessary information when prompted. Then all the transaction data will be added to the `data/budget.csv` file to be consumed in a different step.


## To Do

-   Add tests and debugging flag
-   Create machine learning model to handle the tags
-   Create a web app to display the results
-   Add plot and analysis into this model