






About this User Guide

This guide helps you set up and use the Linear Progression Software for creating and analyzing predictive models. Whether you are a business manager, data analyst, or general user, you'll find clear steps to get the most out of the software's features.

Overview 

The Dataloader App simplifies the process, of uploading and managing data for various purposes. It helps you work efficiently with spreadsheets, databases, or files, making the process easy and hassle-free—even if you’re new to data management!

Project Features 

In this section, you will discover the key features of PredictEase (, a user-friendly software designed to simplify regression modelling and predictive analysis.

Table 1.1: Project Features

Getting Started

Welcome to PredictEase – an easy-to-use tool for data analysis and regression modelling, created through a collaboration between Seneca Polytechnic (Canada) and Universidade da Coruña (Spain) as part of the COIL Project.

With PredictEase, you can upload data, analyze it, visualize results, and manage regression models on a user-friendly Python-powered platform, making data-driven decisions simple for everyone, from beginners to experts.

Hardware/System Requirements

To use PredictEase effectively,  ensure your system meets the following hardware and software requirements:

Operating System-Specific Requirements

Table 2.1: System requirements for Mac and Windows devices.

General Hardware Requirements

Table 2.2. Minimum Hardware Specifications for Optimal Performance.

Additional Notes

Internet Connection: Required for downloading dependencies, updates, and certain online data integrations.

Supported File Formats: CSV, Excel (.xlsx), SQLite databases.

Environment: A stable and secure computing environment is recommended to avoid data loss or application interruptions.

For installation guidance and troubleshooting, refer to the  section of the user documentation.

PredictEase Interface Navigation

PredictEase has a simple, intuitive interface designed to help you create, manage, and visualize regression models. 

Overview of User Interface Components

The user interface is designed to provide a seamless experience for building, managing, and visualizing models. It is organized into three key components:

The user interface contains three parts: 

Loading a model interface 

Model generating interface 

Graph interface  

Loading a Model Interface 

The "Loading a Model" interface (see  for more details) lets you upload and manage pre-saved models. The key features and button positions are as follows:



  File Dropdown

Load Dataset

Load Model

Exit



Model Generating Interface

The Model Generating Interface (see  for more details)  provides tools for creating and refining your models. Key features include:



Input and Output Dropdowns (left-top)

Create Model Button (below dropdowns, centre)

Metrics Display Area (below the button)

Description Field (bottom centre)











































Figure 2.1: Model generating Interface 





















Data Dropdown

This section is about the drop-down list  that contains options to handle empty cells with no value, such as “n/a”, “na”, “non” and “nan” The software offers different options.



Table 3.1: Options in the Handle missing Data drop-down list.





Figure 3.2 Data Dropdown Menu

Use Case Scenario for Data Dropdown

A data analyst prepares a dataset for analysis and notices several empty cells. These missing values could affect the accuracy of the results. The analyst uses the Data Dropdown feature to handle the empty cells.















Data Analyst:

Uploads the dataset into the PredictEase App and identifies empty cells (e.g., “n/a”, “na”, “non”, or “nan”).

Opens the Data Dropdown menu and selects one of the following options

Removes rows with critical missing values.

Replaces missing numerical values with the column mean.

Replaces missing values with the column median to avoid the impact of outliers.

Replaces missing values with a specified constant (e.g., “0” or “unknown”).



Outcome:

The dataset is now consistent and ready for analysis. The missing values are handled based on the selected strategy, ensuring the integrity of the results.

The Data Dropdown gives users control over missing data, streamlining data preparation.

Graph Interface 

The Graph Interface in the Dataloader app enables users to visualize data and model predictions clearly and interactively. It supports types of graphical representations, helping users analyze the dataset and model outcomes efficiently. 



Graph Area (Center of the Interface) 

The current graph displays based on the selected dataset or model predictions.

Graph types may include scatter plots, line graphs, bar charts, etc.

Updates dynamically when the user selects different datasets or model predictions.



Legend and Axis Labels 

Automatically generated when a graph is plotted.

Provides information about data series, axis labels, and units, ensuring clear interpretation of the graph.

       Figure 4.1 Grap Area Interface

Prediction Dropdown

Use the model to predict outcomes based on the dataset. 



Figure 4.2 Prediction dropdown

Functions and Usage of PredictEase

This section describes how to use PredictEase functions to build a linear regression model. 

Using PredictEase

To use PredictEase, make sure your data file is up to date and all data is correctly defined. You can use PredictEase to process and save data sets, generate models for data analysis and prediction, and reload saved models for continuous analysis and customization. 



Opening Data Files 

To start using PredictEase open the data file. PredictEase works with CSV, Microsoft Excel, SQLite, .db and .xls

To open the data file: 

Open Predict Ease 

Click File dropdown in the menu bar. 

A file dialog box opens to choose the dataset file.

Select the compatible Data File > Open 

The data chart appears 

The selected data file opens in PredictEase, and the data chart is displayed, ready for analysis.









Entering a Model Description 

After opening the compatible data file in the software, you will now process the data. 

Locate the Input Column (independent variables) dropdown menu on the left of the home screen. 

Click the dropdown menu and select the desired independent variable (e.g., a column representing "Advertising Budget").

Locate the Output Column (dependent variables) dropdown menu on the left of the home screen. 

Click the dropdown.

Select the desired dependent variable (e.g., a column representing "Sales").

                You are now set to proceed with further model settings or data processing.

         



Building the Model

Generate and visualize the regression model using the selected variables.

Confirm the set input and output variable. 

Click the Create Model button.

Review the results:

A graph with the regression line and data points.

Metrics including:

R² (Coefficient of determination).

MSE (Mean squared error).

Description 

Prediction Result

The regression model is visualized, and key metrics are displayed.









Processing and Saving Model

This section guides you in processing and saving your regression model for future use. Define input and output variables, generate the model, evaluate its performance, and save it for reuse.

To process and save a file after creating the model: 

Click Data in the menu bar 

Select the processing option from the list.

Select Save Model. 

The Save as dialog will appear. 



Enter a file name and click Save.

A success dialog appears to indicate that the model data has been saved. 

Click Ok.

       The model is processed and saved successfully.

Predicting Values from Data Files

This section shows how to predict values using your data files in PredictEase. Load a data file, select input variables, and generate predictions with your regression model.

To predict a value: 

Go to Prediction in the Menu bar. 

Select Make Prediction.

The app displays a Prediction Input dialog box. 

Click OK

Note: If you do not see this test result, you may need to minimize the PredictEase window to full screen.

Select Save Model to save the prediction. 

The app displays the Prediction Input dialog box.

Use Case: Predicting House Prices Using PredictEase

Title: Predicting House Prices Based on Location and Size

Actor: Jane (Person trying to buy a house)

Goal: The homebuyer wants to predict the price of a house based on its location and size.

Preconditions:

Jane has access to the PredictEase app.

Jane has a data file with information about house prices, locations, and sizes.

Main Flow of the homebuyer:

Opens the PredictEase app.

Uploads a data file that includes house prices, locations, and sizes.

Selects "Median income" and "Median house value" as the input and output variables.

The app processes the data and generates a predicted house price ( for the result).

       Jane reviews the predicted price for a house based on their desired location and size.

Postconditions:

The homebuyer receives an estimated house price based on the selected location and size.

Alternative Flow:

If the data file is not in the correct format, the app prompts the homebuyer to upload a valid file.

Location and Size: The homebuyer can choose any location and enter the desired size of the house (e.g., square footage) to predict the house price.



Figure 5.1 Linear progression graph showing the predicted house price based on location and size.

Loading Previous Models 

In this section, you will learn how to load a saved model from your desktop and work with the dataset. This allows you to use customized data for predictions. Simply locate the saved file on your desktop, load it into the app, and start processing the dataset for predictions. 

To load model: 

From the PredictEase interface, select Load Model. 

The File Explorer dialog will open.

Select a previously saved file

Select Open > OK.

The previously generated model will display. 

Additional Information

This section will guide you through the contribution process to ensure a smooth and effective experience.

Contributing to PredictEase Guidelines

Thank you, for your interest in contributing to PredictEase! Your insights and expertise are invaluable in helping us improve our platform and resources.

To ensure a smooth and effective contribution process, please follow these guidelines:

 Contribution Process 

Fork the repository making sure, not to cover any code in the main branch.

Create a new branch for your features or bug fixes. 

Make the necessary changes, then commit to your branch. 

Submit a pull request. We will notify the creators and contact you when the request 	is confirmed or if more information is needed before approving the changes. 

Reporting Issues

If you encounter an issue while using the PredictEase App, we encourage you to report it here so we can address it promptly.







Acknowledgements 

We could not have developed and succeeded with the PredictEase App without the invaluable contributions of several individuals. We extend our heartfelt gratitude to:

Program Co-ordinator and Instructor

Amy Briggs, Seneca Polytechnic: For her guidance and dedication to fostering innovation and excellence in the Technical Communication Graduate Program.

Subject Matter Expert

Dr. Alberto José Alvarellos González, Universidade da Coruña: For sharing his expertise in Computer Science and Artificial Intelligence, offering valuable direction and encouragement.

Development Team
A sincere thank you to the developers for their hard work, creativity, and commitment to bringing PredictEase to life.

Alvaro Carpio (Universidade da Coruña)                                                                                                Role: Developer 

Focused on backend functionalities, including data validation and regression algorithms. 

Contributed to interface improvements, including enhancing the user experience () and user interface () design. 

Responsible for organizing the codebase and improving its modularity and maintainability. 

Alba González Peña (Universidade da Coruña)                                                                                 Role: Code Structure Specialist

Responsible for organizing the codebase and improving its modularity and maintainability. 

Focused on backend functionalities, including data validation and regression algorithms. 

Contributed to interface improvements, including enhancing the user experience (UX) and user interface (UI) design. 





Irene Tembrás Díaz (Universidade da Coruña)                                                                                      Role: Library Researcher 

Conducted research to identify and select appropriate ML libraries for the project. 

Implemented prediction functionalities based on the chosen libraries. 

Contributed to interface improvements and code structuring 

Assisted with project documentation, ensuring clarity and consistency. 

Nawfal Heiloua (Universidade da Coruña)                                                                                             Role: Developer and Scrum Leader                                 

Facilitated team meetings, sprint planning, and retrospectives to maintain alignment with Agile methodologies. 

Focused on backend functionalities, including data validation and regression algorithms.

Assisted with project documentation, ensuring clarity and consistency.

We are deeply grateful to everyone who contributed to this journey. Your support and collaboration have been instrumental in making PredictEase a reality. Thank you!



Hope you enjoy using the software!








Glossary Terms

Technical Terms and Definitions

PredictEase

                A Python-based platform designed for regression modeling and data analysis.

Regression Models

Models that predict outcomes by analyzing relationships between dependent and independent variables in datasets.

Linear Regression

A method to model the relationship between a dependent variable and one or more independent variables using a straight line.

Model-View-Controller (MVC)

               A software design pattern that separates an application into:

Model: Data and business logic

View: User interface (UI)

Controller: Manages user input and updates the model and view.

Mean Squared Error (MSE)

A measure of model accuracy, calculating the average squared difference between actual and predicted outcomes.

R² (Coefficient of Determination)

A statistical metric that indicates how well independent variables predict the dependent variable, ranging from 0 (poor) to 1 (perfect).

GitHub

A platform for version control and collaboration, using Git to manage code changes.

Visual Studio Code

A free, open-source code editor that supports multiple programming languages and integrates with version control systems.

Cross-Platform Compatibility

The ability of software to run on different operating systems (Windows, macOS, Linux) without modification.

Preprocessing

The process of cleaning, transforming, and organizing data before analysis, including handling missing values and normalizing data.

Null Data
Missing or empty data points in a dataset that can affect the results of a model if not properly handled.

Data Dropdown
A user interface element that provides options for handling missing or null data in a dataset, such as filling missing values with the mean, median, or a constant value.

Prediction Dropdown
A menu within the software that allows users to make predictions using a loaded regression model.

File Dialog Box
A window that allows users to navigate through directories and select files for loading into the software.

Save Model Button
A feature that allows users to save their created or modified models for future use or reference.

Preprocessing
The process of cleaning and preparing data for use in a model, which may involve handling missing values, scaling, or transforming data.

Fork the Repository
A version control term, referring to making a copy of the code repository to work on independently before submitting changes.

Pull Request
A request to merge changes from one branch of a code repository into the main branch after the changes have been reviewed.

Continuous Analysis
The process of ongoing examination and refinement of data and models as new data is introduced or as performance improves.





### Imagen 1
![Image 1](./Read_me_File_Images/image_1.png)

### Imagen 2
![Image 2](./Read_me_File_Images/image_2.png)

### Imagen 3
![Image 3](./Read_me_File_Images/image_3.png)

### Imagen 4
![Image 4](./Read_me_File_Images/image_4.png)

### Imagen 5
![Image 5](./Read_me_File_Images/image_5.png)

### Imagen 6
![Image 6](./Read_me_File_Images/image_6.png)

### Imagen 7
![Image 7](./Read_me_File_Images/image_7.png)

### Imagen 8
![Image 8](./Read_me_File_Images/image_8.png)

### Imagen 9
![Image 9](./Read_me_File_Images/image_9.png)

