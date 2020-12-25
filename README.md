# CSEN1095-W20-Project
# Milestone 1
## An Overview of Used Datasets
##### All the datasets are collected from kaggle.com.
### World Happiness Report
###### This is a set of datasets taking a survey of the happiness score of 155 countries annually from 2015 to 2019. The dataset evaluates the happiness score alongside how six factors - economic production, social support, life expectancy, freedom, absence of corruption, and generosity – affect it. This is in comparison to a fictional nation Dystopia which has the lowest national average values in all of the six factors.
###### The link for the dataset in question is "https://www.kaggle.com/unsdsn/world-happiness"
### All 250 Country Data
###### This dataset compiles 11 columns of 250 countries in the world. It contains the name of the country, the region and subregion it is in, its population, area, gini index, and the percentages of its Real Growth Rate, Literacy Rate, Inflation and Unemployment. 
###### The link for the dataset in question is "https://www.kaggle.com/souhardyachakraborty/all-250-country-data"
### Life Expectancy (WHO)
###### This dataset considers aggregated data from the year 2000 to the year 2015 for 193 countries compiled from the Global Health Observatory(GHO) data repository under the World Heath Organization(WHO). It covers the life expectancy in those countries over the course of those years as well as the factors relating to it, including adult and infant mortality rates, alcohol consumption, government expendature on health, percentages of some immunized diseases, the mortalities of some as well as the number of reported cases of some others. 
###### The link for the dataset in question is "https://www.kaggle.com/kumarajarshi/life-expectancy-who"
## An Overview of Project Goals and Motivation
###### To be able to use the data effectively and efficiently by having the ability to extract vital, readible and credible information from our datasets as well as being able to interpret, observe and draw conclusions from it.
###### We do so by finding appropriate research questions that we can derive after observing the data as well as findinng the answers from our dataset. By doing such, we provide the data with more useful and powerful information.
## Descriptive steps used for the work done in this milestone.
###### First the three datasets were divided amongst us and the cleaning and tidying of each dataset was handled individually. This was done by the standardization of data values in columns, the filling of NaN values with different imputation methods and the discard of rows within each dataset that had too many missing values to be imputed. 
###### The next step was the locating and handling of outlier values in each dataset. We found the outlier values in each column of each data set and then used the winsorization method to handle the outliers in them. Winsorization is the transformation of statistics by limiting extreme values in the statistical data to reduce the effect of possibly spurious outliers.
###### The final step was the integration and merging of the 3 datasets into one covering all the information in each dataset. Before we did this, we needed to aggregate the world happiness report data so we would deal with only one year (the average of all 5 years). We then looked at the data as a cohesive whole and began asking questions that could be answered by the integration of columns we had done.
## Data exploration questions
#### The questions we asked were: 
###### 1. Does the level of schooling affected the literacy rate of a nation?
###### 2. Whether there is a correlation between happiness level and the rate of alcohol consumption per capita. It asks the question if people drink more when they are unhappy or is the fact that drinking raises the level of happiness in a population.
###### 3. Does the rate of unemployment has any effect on the Happiness Status, an engineered feature, of a nation?
###### 4. Whether or not there exists a relation between countries' Unemployement rate and their GDP?
###### 5. Whether the total percentage of immunized diseases, an engineered feature, affected the life expectancy in a country.
###### 6. Comparison of the Real Growth Rating of developing countries and that of developed ones.
# Milestone 2A
## Features Added
#### We utilized a number of feature engineering methods:
###### We used one-hot-encoding on the Status column of nations, dividing countries into Developed and Developing columns.
###### We used label-encoding on the Region column.
###### We discretized the Happiness Score and named the column Happiness Status and then label encoded the Happiness Status column with values of "Very Sad", "Mildly Sad", "Mildly Happy" and "Very Happy".
###### We also engineer a feature representing the total percentage of immunized diseases in a country. We do this by adding the percentages of all the immunized diseases,i.e Hepatitis B, Diptheria, and Polio and dividing their sum by the total number of diseases immunized recorded.
# Milestone 2B
## Description of the pipeline
