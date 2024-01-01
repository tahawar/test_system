# Test_questions_generator

# Streamlit Application for Keyword Generation and Question Formulation

## Overview
This Streamlit application is designed to automate the process of generating relevant keywords and formulating scenario-based multiple-choice questions. It aids HR professionals and recruiters in creating assessment materials and job descriptions, leveraging OpenAI's GPT models (GPT-3.5 and GPT-4).

## Features
- AI Model Selection: Choose between GPT-3.5 and GPT-4 models.
- Automatic Website Summary Extraction: Scrape and summarize company website content.
- Manual Summary Input: Option for manual summary input when automatic extraction fails.
- Keyword Generation: Generate keywords from job descriptions, website summaries, and skills.
- Customizable Complexity Level: Adjust complexity levels for scenario-based questions.
- Scenario-based Question Formulation: Create relevant multiple-choice questions.
- Feedback and Iteration: Provide feedback and regenerate questions as needed.
- Export Functionality: Save questions and feedback in CSV format.

## How to Use
1. Set Up Environment: Install Streamlit and necessary libraries.
2. Launch Application: Run the Streamlit app and use the sidebar for inputs.
3. Enter Job Details: Input job description and website URL.
4. Check Website Summary: Automatically or manually summarize the company website.
5. Generate Keywords: Use the AI model to generate relevant keywords.
6. Formulate Questions: Generate scenario-based questions based on the keywords.
7. Provide Feedback: Offer feedback on generated questions and regenerate if needed.
8. Export Results: Save accepted questions and feedback to CSV files.

## Installation
Clone the repository and install dependencies:
1. git clone <https://github.com/codrivity/Test_questions_generator>
2. cd Test_questions_generator
3. pip install -r requirements.txt


## Running the Application
To start the Streamlit app, run:
streamlit run app.py







