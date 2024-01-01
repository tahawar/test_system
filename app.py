import datetime
import time
import streamlit as st
import json
import openai
from openai import OpenAI
import re
import csv
import os
import string
from datetime import datetime
import validators
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import WebBaseLoader
from langchain.chains.summarize import load_summarize_chain
import base64
import configparser
from urllib.parse import urlparse
import shutil
import logging
import streamlit.components.v1 as components
# from streamlit.script_request_queue import RerunData
# from streamlit.script_runner import RerunException

logging.basicConfig(level=logging.INFO)

# Encode SVG file to base64
with open("innoflow-01.svg", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode()

# Embed the base64 encoded image within the HTML
encoded_image_html = f"data:image/svg+xml;base64,{encoded_string}"


# Create a ConfigParser object
config = configparser.ConfigParser()
config.read('config.ini')

os.environ["OPENAI_API_KEY"] = config['OPENAI']['OPENAI_API_KEY']


# Initialize session state for keywords and feedback
if 'keywords' not in st.session_state:
    st.session_state['keywords'] = {}
if 'feedback' not in st.session_state:
    st.session_state['feedback'] = []
if 'questions' not in st.session_state:
    st.session_state['questions'] = {}
if 'keywords' not in st.session_state:
    st.session_state.keywords = {}

if 'delete_status' not in st.session_state:
    st.session_state.delete_status = False
if 'csv_filenames' not in st.session_state:
    st.session_state.csv_filenames = {'accepted': None, 'rejected': None}

# Initialize session state variables
if 'session_started' not in st.session_state:
    st.session_state.session_started = False

# Initialize session state variables for file paths
if 'download_file_paths' not in st.session_state:
    st.session_state.download_file_paths = {'accepted': None, 'rejected': None}

# Initialize a dictionary in session state to track user satisfaction for each keyword
if 'user_satisfaction' not in st.session_state:
    st.session_state.user_satisfaction = {}


# Initialize session state variables
if 'CompanyWebsiteSummary' not in st.session_state:
    st.session_state.CompanyWebsiteSummary = ''

if 'manual_summary_needed' not in st.session_state:
    st.session_state.manual_summary_needed = False

if 'summary_button_clicked' not in st.session_state:
    st.session_state.summary_button_clicked = False

if 'saved_questions' not in st.session_state:
    st.session_state['saved_questions'] = []

if 'current_keyword_index' not in st.session_state:
    st.session_state.current_keyword_index = 0
if 'questions' not in st.session_state:
    st.session_state.questions = {}
if 'user_satisfaction' not in st.session_state:
    st.session_state.user_satisfaction = {}
if 'feedback' not in st.session_state:
    st.session_state.feedback = {}
if 'ready_to_generate' not in st.session_state:
    st.session_state.ready_to_generate = False
if 'saved_questions' not in st.session_state:
    st.session_state.saved_questions = []

PASSWORD = "thomaspassword"
# The code provides functions to validate a URL and generate a summary of the content from the specified URL if it is valid. It utilizes external libraries and APIs for URL validation and text
# summarization.






def validate_url(url):
    # Check if the URL already contains a scheme (http:// or https://)
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        # Try adding 'http://' and 'https://' to see if it forms a valid URL
        http_url = f"http://{url}"
        https_url = f"https://{url}"
        if validators.url(http_url):
            return http_url
        elif validators.url(https_url):
            return https_url
    elif validators.url(url):
        # URL is valid with its current scheme
        return url

    # URL is invalid
    return None

def website_summary(url):
    logging.info(f"Received URL: {url} and model_version: {model_version}")
    valid_url = validate_url(url)
    logging.info(f"Validated URL: {valid_url}")
    if valid_url:
        try:
            # Load and scrape the content from the valid URL
            loader = WebBaseLoader(valid_url)
            docs = loader.load()

            # model_name = "gpt-4" if model_version == 'gpt-4' else "gpt-3.5-turbo-16k"
            # llm = ChatOpenAI(temperature=0, model_name=model_name)
            # chain = load_summarize_chain(llm, chain_type="stuff")
            # Extract main text content
            page_content = docs[0].page_content
            cleaned_text = re.sub('<[^<]+?>', ' ', page_content)  # Remove HTML tags and replace them with a space
            cleaned_text = re.sub('[^A-Za-z0-9.,?!\s]', '', cleaned_text)  # Remove special characters and brackets
            cleaned_text = re.sub('\s+', ' ', cleaned_text)  # Replace multiple whitespace characters with a single space
            cleaned_text = cleaned_text.strip()  # Remove leading and trailing whitespaces

            # return testtmaker(cleaned_text)
            return testtmaker(cleaned_text)
        except Exception as e:
            print(f"Error occurred during website scraping: {e}")
    else:
        print("Invalid URL format. Please check the URL.")
    
    # Returning None to indicate that manual input is needed
    return None

def remove_quotes_and_special_characters(input_string):
    # Define a regular expression pattern to match quotes and special characters
    pattern = r'[\'"\[\]{}()!@#$%^&*.,;?/:<>\|_+=-]'
    
    # Use re.sub to remove all matches of the pattern in the input string
    cleaned_string = re.sub(pattern, '', input_string)
    
    return cleaned_string

def create_dictionary_from_response(response):
    pattern = r'"([^"]+)":\s*"([^"]+)"'
    matches = re.findall(pattern, response)
    result_dict = dict(matches)
    return result_dict

def skillsline(form_values):
    mainchat = ''
    if form_values['Hardskills']:
        mainchat += 'Hard skills,'
    if form_values['Softskills']:
        mainchat += 'Soft skills, '
    if form_values['Cultural Fit']:
        mainchat += 'Cultural Fit, '
    return mainchat


def reset_app():
    # Clear session state
    keys_to_clear = list(st.session_state.keys())
    for key in keys_to_clear:
        del st.session_state[key]
    hardskills=''
    # Rerun the app
    st.experimental_rerun()

def testtmaker(text):
    client = OpenAI(
        # Specify your OpenAI API key here
        # api_key='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'
    )
    model_name = "gpt-4-0613" if model_version == 'gpt-4-0613' else "gpt-3.5-turbo-16k"

    chat_completion = client.chat.completions.create(
        model=model_name,
        messages=[{
                "role": "user",
                "content": """
                The output/result must be in {test_language} language, make sure the result should not be any other language other than {test_language}.
                Your task is to meticulously extract and list all job-related information from the provided text: '{text}'. Focus exclusively on identifying exact
                 details pertaining to the job role. This includes the precise job title, verbatim job description, direct responsibilities, and specific duties as stated in the text. 
                 Additionally, capture any mentioned qualifications, required skills, and unique requirements or expectations associated with the position. It is essential to avoid summarizing or
                  interpreting the information; instead, present the job-related data exactly as it appears in the text, ensuring accuracy and fidelity to the original wording. If the text includes
                   specific terms or phrases related to the job, these should be noted verbatim. 
                The goal is to provide a direct transcription of all job-related elements from the text, offering a clear and unaltered representation of the job as described.
                if you did not find any text related to job you can only reply with: ' we dont have job  discreption and job related stuff on this link please add it mannauly

                The output/result must be in {test_language} language, make sure the result should not be any other language other than {test_language}.
               
                """.format(text= text, test_language=test_language)
            }
        ]
    )

    return chat_completion.choices[0].message.content

def promptmaker(form_values):
    client = OpenAI(
        # Specify your OpenAI API key here
    )
    model_name = "gpt-4-0613" if model_version == 'gpt-4-0613' else "gpt-3.5-turbo-16k"

    chat_completion = client.chat.completions.create(
        model=model_name,
        messages=[{
                "role": "user",
                "content": """
                The output/result must be in {test_language} language, make sure the result should not be any other language other than {test_language}.
                Skill Focus: {skills}

                Contexts for Analysis:

                Company Website Summary: {CompanyWebsiteSummary} Analyze the data about the job to identify keywords that showcase how the {skills} aligns with the company's culture, values, and operational focus.
                Job Description: {HRResourceRequirement}  Review the job description to extract keywords that highlight the importance and application of the {skills} in the job role.
                Intensity Level of the Role: {TestLevelIntensity}

                Assess the TestLevelIntensity, considering the following complexity levels:
                Basic: Tasks are straightforward and require minimal skill or experience.
                Intermediate: Tasks require moderate skill and understanding, with some complexity.
                Advanced: Tasks demand high expertise, involving complex problem-solving.
                Strategic: Tasks at the highest level, shaping the company's direction and impact.

                Task:
                
                From these sources, extract 15 keywords that are crucial in understanding the role of the {skills} within the context of the job,  the company, and across different complexity levels..
                Distribute these keywords evenly ensuring a balanced representation. Keywords look paractial because it is going to use for making test so keywords are going to be guinne.
                keyword should be in two-word phrasings 
                Present the keywords in a structured, dictionary-style format:
                {{ 
                  "keyword1": "source1", 
                  "keyword2": "source2", 
                  ...
                  "keyword15": "source15" 
                }}

                Each keyword should be accurately sourced, reflecting its origin from either the Company Website Summary or the Job Description.
                Guidelines:
                keyword should be in two-word phrasings (for example Sales Driving, Partnership Development, Material Development,Event Support)
                
                Focus solely on the skill {skills} and its relevance. and keyword should be long and proper 
                Maintain correct word casing and precision in keyword selection.
                Ensure that each keyword is impactful and directly related to either the job role or the company ethos.
                Limit the output to exactly 15 keywords, avoiding non-essential terms.




               
                """.format(skills = skillsline(form_values), CompanyWebsiteSummary = form_values['CompanyWebsiteSummary'], HRResourceRequirement=form_values['Job_description'], TestLevelIntensity = form_values['TestLevelIntensity'], test_language=test_language)
            }
        ]
    )

    return chat_completion.choices[0].message.content




def promptmaker_20_keywords(form_values):
    client = OpenAI(
    )
    model_name = "gpt-4-0613" if model_version == 'gpt-4-0613' else "gpt-3.5-turbo-16k"

    chat_completion = client.chat.completions.create(
        model=model_name,
        messages=[{
            "role": "user",
            "content": """
            The output/result must be in {test_language} language, make sure the result should not be any other language other than {test_language}.
            Skill Focus: {skills}

                Contexts for Analysis:

                Company Website Summary: {CompanyWebsiteSummary} Analyze the data about the job to identify keywords that showcase how the {skills} aligns with the company's culture, values, and operational focus.
                Job Description: {HRResourceRequirement}  Review the job description to extract keywords that highlight the importance and application of the {skills} in the job role.
                Intensity Level of the Role: {TestLevelIntensity}

                Assess the TestLevelIntensity, considering the following complexity levels:
                Basic: Tasks are straightforward and require minimal skill or experience.
                Intermediate: Tasks require moderate skill and understanding, with some complexity.
                Advanced: Tasks demand high expertise, involving complex problem-solving.
                Strategic: Tasks at the highest level, shaping the company's direction and impact.

                Task:
                
                From these sources, extract 20 keywords that are crucial in understanding the role of the {skills} within the context of the job,  the company, and across different complexity levels..
                Distribute these keywords evenly across the two categories (Company Website Summary and Job Description), ensuring a balanced representation.Keywords look paractial because it is going to use for making test so keywords are going to be guinne.
                keyword should be in two-word phrasings 
                Present the keywords in a structured, dictionary-style format:
                {{ 
                  "keyword1": "source1", 
                  "keyword2": "source2", 
                  ...
                  "keyword20": "source20" 
                }}

                Each keyword should be accurately sourced, reflecting its origin from either the Company Website Summary or the Job Description.
                Guidelines:
                keyword should be in two-word phrasings(for example Sales Driving, Partnership Development, Material Development,Event Support)
                
                Focus solely on the skill {skills} and its relevance.
                Maintain correct word casing and precision in keyword selection.
                Ensure that each keyword is impactful and directly related to either the job role or the company ethos.
                Limit the output to exactly 20 keywords, avoiding non-essential terms.
            """.format(skills=skillsline(form_values), CompanyWebsiteSummary=form_values['CompanyWebsiteSummary'], HRResourceRequirement=form_values['Job_description'], TestLevelIntensity=form_values['TestLevelIntensity'],test_language=test_language)
        }]
    )

    return chat_completion.choices[0].message.content







def promptmakerbydefault(keyword, rating, test_language ):
  client = OpenAI(
    # Defaults to os.environ.get("OPENAI_API_KEY")
    # Otherwise use: api_key="Your_API_Key",
   
)
#   time.sleep(2)
  model_name = "gpt-4-0613" 
  chat_completion = client.chat.completions.create(
    model= model_name,
    # messages=[{"role": "user", "content": 'Translate the following English text to French: "{text}"'}]
    messages=[{"role": "user", "content": """The output/result must be in {test_language} language, make sure the result should not be any other language other than {test_language}. 
        Formulate a scenario-based multiple-choice question designed to assess the application of a specific skill, 
        pertinent to the given keyword, within the context of the defined complexity scale. This question should probe the candidate's ability to navigate challenges at 
        a particular tier of complexity, as outlined below:
        Complexity Scale: {TestLevelIntensity}
        - Basic Complexity: Entails straightforward issues that follow well-established procedures without the need for special resources. Tasks at this level are straightforward and require minimal skill or experience. They can be completed quickly and without much effort.
        - Intermediate Complexity: Involves complex problems that require thorough analysis and coordination but are manageable with standard practices. Intermediate tasks require a moderate level of skill and understanding. They may involve some complexity but are generally well-defined and manageable with reasonable effort
        - Advanced Complexity: Consists of intricate challenges that necessitate additional resources, pushing beyond what the organization typically handles. Advanced tasks demand a high level of expertise and experience. They are often complex, requiring creative problem-solving and in-depth knowledge. Completing these tasks may take more time and effort.
        - Strategic Complexity: Comprises exceptionally complicated situations that demand expert intervention and innovative solutions, greatly surpassing the organization's usual capabilities with a high degree of uncertainty.Strategic tasks are at the highest level of complexity. They require a deep understanding of the organization's goals and long-term vision. These tasks involve shaping the direction of the company and have a profound impact on its success.

        The question must be structured to mimic a real-life situation where the skill associated with the {keyword} is crucial. Develop five well-considered answer choices that are all feasible and directly connected to the scenario, without any being misleading or incorrect. The aim is to craft options that thoughtfully test the candidate's grasp of the skill.
        
        and choice A is Applicable for choice B feasible and for choice C  Viable alternative and for d choice Practical solution and for e Strategic selection (please dont mention in asnwer about it is applicable or etc)
        Desired Response Format:
            
        {{
        "question": "Insert your comprehensive, scenario-based question here, ensuring it encapsulates the essence of the selected {keyword} and the complexity level.",
        "answers": [" I. _________________", "II. _________________", "III. _________________", "	IV. _________________", "V. _________________"]
        }}
        This tailored question will serve to thoroughly evaluate the candidate's adeptness in the relevant skill area, in alignment with the specified level of complexity. remember the genretad question and answers should be in {test_language} and not in any other language and dont make a trenslation of it 
    """.format(keyword=keyword ,  TestLevelIntensity = rating, test_language=test_language)}]
)

  return chat_completion.choices[0].message.content




def promptmakerwhenno(keyword, reason,rating, question, test_language ):
  client = OpenAI(
    # Defaults to os.environ.get("OPENAI_API_KEY")
    # Otherwise use: api_key="Your_API_Key",
)
  model_name = "gpt-4" if model_version == 'gpt-4' else "gpt-3.5-turbo-16k"
#   time.sleep(2)


  chat_completion = client.chat.completions.create(
    model=model_name,
    # messages=[{"role": "user", "content": 'Translate the following English text to French: "{text}"'}]
    messages=[{"role": "user", "content": """The output/result must be in {test_language} language, make sure the result should not be any other language other than {test_language}.
        Develop a detailed scenario-based multiple-choice question that skillfully assesses a specific ability linked to a provided keyword.
     This question should intelligently navigate the nuances of a complexity scale, harmonizing with the structure outlined in Prompt 1, and augmented with the following elements:
        All the answer is in danish language and written this in danish 
        Complexity Scale: {TestLevelIntensity}
        - Basic Complexity: Entails straightforward issues that follow well-established procedures without the need for special resources. Tasks at this level are straightforward and require minimal skill or experience. They can be completed quickly and without much effort.
        - Intermediate Complexity: Involves complex problems that require thorough analysis and coordination but are manageable with standard practices. Intermediate tasks require a moderate level of skill and understanding. They may involve some complexity but are generally well-defined and manageable with reasonable effort
        - Advanced Complexity: Consists of intricate challenges that necessitate additional resources, pushing beyond what the organization typically handles. Advanced tasks demand a high level of expertise and experience. They are often complex, requiring creative problem-solving and in-depth knowledge. Completing these tasks may take more time and effort.
        - Strategic Complexity: Comprises exceptionally complicated situations that demand expert intervention and innovative solutions, greatly surpassing the organization's usual capabilities with a high degree of uncertainty.Strategic tasks are at the highest level of complexity. They require a deep understanding of the organization's goals and long-term vision. These tasks involve shaping the direction of the company and have a profound impact on its success.

        Previous Question {previous_generated_question}: Reference the earlier formulated question, providing a basis for enhancement.
        Reason for Disapproval {reason_for_dislike}: Incorporate the user's feedback to avoid past pitfalls and better align with the intended assessment goals.
        The newly crafted question should be thoughtfully composed, mirroring real-world scenarios where the skill associated with the {keyword} is essential. It must strike a balance in length and complexity, aptly reflecting the chosen complexity level. 
        Additionally, it should feature five well-crafted answer options. Each option must be clear, plausible, and directly tied to the scenario, crafted to avoid any ambiguity or inaccuracy. These options should collectively challenge and evaluate the candidate's proficiency in the relevant skill area.

        Desired Response Format: 
        {{
        "question": "Insert your comprehensive, scenario-based question here, ensuring it encapsulates the essence of the selected {keyword} and the complexity level.",
        "answers": [" I. _________________", "II. _________________", "III. _________________", "	IV. _________________", "V. _________________"]
        }}
                    This tailored question will serve to thoroughly evaluate the candidate's adeptness in the relevant skill area, in alignment with the specified level of complexity and  remember the genretad question and answers should be in {test_language} and not in any other language and dont make a trenslation of it 
    """.format(keyword=keyword , reason_for_dislike=reason, TestLevelIntensity = rating, previous_generated_question=question, test_language=test_language )}]
)
  return chat_completion.choices[0].message.content








# Function to get a unique filename based on the current timestamp
def get_unique_filename(prefix):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.csv"

# Function to write accepted questions to a CSV file
def write_accepted_questions_to_csv(questions, filename):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Keyword', 'Question'])
        for keyword, question in questions.items():
            writer.writerow([keyword, question])

# Function to write rejected feedback to a CSV file
def write_rejected_feedback_to_csv(feedback, filename):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Keyword', 'Question', 'Reason'])
        for item in feedback:
            if len(item) == 3:  # Ensure each item has 3 elements
                writer.writerow(item)
            else:
                st.error(f"Invalid feedback format: {item}")

# Streamlit app layout with session state initialization
st.set_page_config(page_title='Case Development Tool', layout='wide')
if 'step' not in st.session_state:
    st.session_state.update({
        'step': 1,
        'keywords': {},
        'feedback': [],
        'questions': {},
        'test_level_intensity': 'Low',
        'job_description': ''
    })



# Custom CSS for the slider track and thumb
custom_css = """
<style>

    /* Custom style for the company title */
    .title-innoflow {
        font-size: 30px;
        font-weight: bold;
        color: #CC7655; /* Updated color for 'Innoflow' */
        padding: 10px;
        text-align: center;
        margin-top: 10px;
    }

    /* Slider thumb color */
    .stSlider .rc-slider-handle {
        background-color: #344E43 !important;
        border: 2px solid #344E43 !important;
    }

    /* Slider track color */
    .stSlider .rc-slider-track {
        background-color: #344E43 !important;
    }

    /* Slider rail color (the part not yet selected) */
    .stSlider .rc-slider-rail {
        background-color: #344E43 !important;
    }

    /* Hover effect for Streamlit buttons */
    .stButton > button:hover {
        background-color: #344E43;
        border-color: #344E43;
        color: #FFFFFF;
    }

    /* Rounded image style */
    .rounded-img {
        border-radius: 50%;
    }
</style>
"""


st.markdown(custom_css, unsafe_allow_html=True)
# Define your other functions like create_dictionary_from_response, skillsline, etc.



# Sidebar form for user input
# Sidebar form for user input

with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="{encoded_image_html}" class="rounded-img" style="width: 50px; height: 50px;"/>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        f"""
        <div class="title-innoflow">Case Development Tool</div>
        """,
        unsafe_allow_html=True
    )
    
    st.title('Foundation of Assessment')

  
    
    st.title('Access Control')
    password = st.text_input("Enter your password to access GPT-4", type="password")

    # Check if the password is correct
    # Check if the password is correct
    if password and password == PASSWORD:
        st.session_state['gpt4_access'] = True
        st.success("Access granted for GPT-4.")
    elif password:
        st.error("Incorrect password. Access denied for GPT-4.")
    else:
        st.session_state['gpt4_access'] = False

    # AI Model Version Selection
    model_options = ['gpt-3.5-turbo-16k']
    if st.session_state.get('gpt4_access', False):
        model_options.append('gpt-4')
    model_version = st.selectbox('Select AI Model Version', options=model_options)

    
    # model_version = st.selectbox(
    #     'Select AI Model Version',
    #     options=['gpt-3.5-turbo-16k', 'gpt-4-0613'],
    #     index=0  # Default to GPT-3.5
    # )
    test_language = st.selectbox(
        'Select Output Language',
        options=['English', 'Danish', 'German', 'French', 'urdu'],
        index=0  # Default to English
    )
    hardskills = st.checkbox('Hard skills', help='E.g., coding skills, mathematical skills.')
    softskills = st.checkbox('Soft skills', help='E.g., situational judgment, critical thinking, empathy.')
    cultural_fit = st.checkbox('Cultural Fit', help='E.g., Integrity, Adaptability, Innovation, Resilience.')
    
    st.title('Complexity Level Information')
    complexity_labels = ['Basic', 'Intermediate', 'Advanced', 'Strategic']

    complexity_tooltips = {
        'Basic': 'Tasks are straightforward and require minimal skill or experience.',
        'Intermediate': 'Tasks require moderate skill and understanding, with some complexity.',
        'Advanced': 'Tasks demand high expertise, involving complex problem-solving.',
        'Strategic': 'Tasks at the highest level, shaping the company’s direction and impact.'
    }

     # Display the complexity levels with tooltips
    for label in complexity_labels:
        st.write(f"{label}: ", complexity_tooltips[label])

    test_level_intensity = st.select_slider(
        'Complexity level',
        options=complexity_labels,
        help='Select the appropriate complexity level. Hover over the complexity levels above for more information.'
    )
    job_description = st.text_area('Job post or description', placeholder='Describe the job requirements and expectations.', help='Describe the job requirements and expectations.', height=220)
    
    

    website_url = st.text_input('Website URL', placeholder='https://abc.com', help='Enter the website URL here.')

    # Button to check website summary
    check_summary_button = st.button('Retrieve Website Information')

    # website_summary_text = st.session_state.get('CompanyWebsiteSummary', '')

    if check_summary_button:
        st.session_state.summary_button_clicked = True
        # Attempt to get website summary
        website_summary_result = website_summary(website_url)

        if website_summary_result is None:
            # Website cannot be scraped, prompt for manual input
            st.session_state.manual_summary_needed = True
            # st.warning("Website Data not available. Please enter it manually below.")
            st.session_state['CompanyWebsiteSummary'] = ''  # Clear previous summary if any
            # website_summary_text = st.text_area("Website Data", value=st.session_state.get('CompanyWebsiteSummary', ''), height=300)
            
        else:
            # Use the scraped website summary
            st.session_state['CompanyWebsiteSummary'] = website_summary_result
            st.session_state.manual_summary_needed = False
            #website_summary_text = website_summary_result
            # st.success("Website data retrieved successfully. You can now generate keywords.")
            # website_summary_text = st.text_area("Website Data", value=st.session_state.get('CompanyWebsiteSummary', ''), height=300)
            
   

 
    # Display the text area for website summary if the summary button has been clicked
    if st.session_state.summary_button_clicked:
        website_summary_text = st.text_area("Website Data", value=st.session_state.get('CompanyWebsiteSummary', ''), height=300)
        # Save the summary text to session state if the user changes it
        st.session_state['CompanyWebsiteSummary'] = website_summary_text
    
    # Button to generate keywords
    submit_button = st.button('Generate Keywords')
  

    # Proceed with generating keywords if summary is available
    if submit_button and (not st.session_state.manual_summary_needed or st.session_state.get('CompanyWebsiteSummary')):
        form_values = {
            "Hardskills": hardskills,
            "Softskills": softskills,
            "Cultural Fit": cultural_fit,
            "TestLevelIntensity": test_level_intensity,
            "Job_description": job_description,
            "CompanyWebsiteSummary": st.session_state.get('CompanyWebsiteSummary', ''),
            "ModelVersion": model_version
        }

        checkbox_count = sum([hardskills, softskills, cultural_fit])
        if checkbox_count >= 2:
            generated_keywords = promptmaker_20_keywords(form_values)
        else:
            generated_keywords = promptmaker(form_values)
        st.session_state.keywords = create_dictionary_from_response(generated_keywords)

    





st.header('Settings')
    # Reset button
if st.button('Reset App'):
    reset_app()
    # st.caption('Clicking this will delete all keywords and questions.')
    # Use HTML to style the caption text in red
st.markdown('<span style="color: red">Clicking this will delete all keywords and questions.</span>', unsafe_allow_html=True)




# Main page for keyword management
st.header('Keyword Management')
# st.button('Reset App', on_click=reset_app)


# Add new keyword
new_keyword = st.text_input('Enter a new keyword to add:')
if st.button('Add Keyword'):
    if new_keyword and new_keyword not in st.session_state.keywords:
        st.session_state.keywords[new_keyword] = 'source'  # Add a default source or other relevant information
        st.success(f"Keyword '{new_keyword}' added.")
    else:
        st.error("Please enter a unique keyword or ensure the keyword field is not empty.")




with st.form(key='delete_keywords_form'):
    st.subheader('Delete Keywords')

    # Determine the number of columns for the grid layout
    num_columns = 3  # Change this number based on your preference
    cols = st.columns(num_columns)

    # Create checkboxes in a grid layout
    keywords_to_delete = []
    for i, keyword in enumerate(list(st.session_state.keywords.keys())):
        # Use the column corresponding to the current index
        with cols[i % num_columns]:
            if st.checkbox(keyword, key=keyword):
                keywords_to_delete.append(keyword)

    submit_delete = st.form_submit_button('Delete Selected Keywords')

# Handle deletion outside the form
if submit_delete:
    for keyword in keywords_to_delete:
        if keyword in st.session_state.keywords:
            del st.session_state.keywords[keyword]
    st.success('Current Keywords List is updated.')
# st.subheader('Current Keywords List')
# st.write(st.session_state.keywords)

st.subheader('Current Keywords List')

# # Check if there are any keywords to display
if st.session_state.keywords:
    # Create a dataframe for better display
    import pandas as pd
    df = pd.DataFrame(list(st.session_state.keywords.items()), columns=['Keyword', 'Description'])
    st.table(df)
else:
    st.write("No keywords available.")







def remove_brackets_and_quotes(data):
    # Define the regex pattern to match brackets and quotes
    pattern = r"[\[\]\(\)\{\}\<\>\"\'\“\”\‘\’]"

    # Apply the regex to remove brackets and quotes
    cleaned_data = re.sub(pattern, "", data)

    return cleaned_data



    

def reformat_answers(answers):
    reformatted_answers = []
    for idx, answer in enumerate(answers, start=1):
        # First regex for "Choice" and "Option" formats
        answer = re.sub(r"^\s*((Choice|Option)\s*([1-5]|[A-E]))\s*:\s*", "", answer).strip()
        # Second regex for "A)" to "E)" and "A." to "E." formats
        answer = re.sub(r"^\s*([A-E]\)|[A-E]\.|[A-E]:)\s*", "", answer).strip()
        answer = re.sub(r"^\s*(I|II|III|IV|V)[.:)]\s*", "", answer).strip()

        # New regex for phrases like "Applicable choice A.", "Feasible option B.", etc.
        answer = re.sub(r"^(Applicable choice|Feasible option|Viable alternative|Practical solution|Strategic selection)\s[A-E]\.\s*", "", answer).strip()
        answer = re.sub(r"^(Strategically aligned choice|Logically sound option |Analytically strong alternative|Insightfully developed solution|Creatively conceived selection)\s[A-E]\.\s*", "", answer).strip()
        answer = re.sub(r"^(?:Mulighed | mulighed |Gennemførlig løsning |Gennemførlig option |Anvendelig valg| Gennemførlig mulighed| Mulig option |Levedygtig alternativ |Levedygtig alternativ | Mulig alternativ |Muligt valg|Anvendelig valgmulighed|Mulig løsning|Bæredygtigt alternativ|Mulig valg|Praktisk løsning|Strategisk valg|Mulig valgmulighed|Levedygtig mulighed|Levedygtig løsning|Vikle alternativ|Dygtig løsning|Gennemførligt løsning|En realistisk mulighed|Brugbar valgmulighed|Anvendelige choice | Levende alternativ)\s*[A-E]?\.?\s*", "", answer, flags=re.IGNORECASE | re.MULTILINE ).strip()
        

        reformatted_answers.append(f"{idx}. {answer}")
    return reformatted_answers

# Check if a session has started
# # Check if a session has started
# if st.session_state.session_started:
#     st.header('Generate Questions Based on Keywords')

#     for keyword in st.session_state.keywords:
#         with st.container():
#             st.subheader(f"Keyword: {keyword}")

#             # Initialize user satisfaction status for the keyword if not already done
#             if keyword not in st.session_state.user_satisfaction:
#                 st.session_state.user_satisfaction[keyword] = 'Yes'  # Default to 'Yes'

#             # Generate question button
#             if keyword not in st.session_state.questions:
#                 if st.button(f'Generate question for "{keyword}"', key=f'generate_{keyword}'):
#                     # print(test_level_intensity)
#                     response = promptmakerbydefault(keyword, test_level_intensity, test_language)
#                     st.session_state.questions[keyword] = response
#                     st.session_state.user_satisfaction[keyword] = 'Yes'  # Set satisfaction to 'Yes' for new question

#             col1, col2 = st.columns([3, 1])

          
#             if keyword in st.session_state.questions:
#                 question_response = st.session_state.questions[keyword]
#                 try:
#                     # Attempt to parse the JSON part
#                     question_data = json.loads(question_response)
#                     question = question_data.get("question", "")
#                     raw_answers = question_data.get("answers", [])
#                 except json.JSONDecodeError:
#                     # If JSON parsing fails, split the response to separate the question and the raw answers
#                     parts = question_response.split('\n\n', 1)
#                     json_part = parts[0]
#                     text_part = parts[1] if len(parts) > 1 else ""
            
#                     # Try parsing the JSON part to extract the question and answers
#                     try:
#                         parsed_json = json.loads(json_part)
#                         question = parsed_json.get("question")
#                         raw_answers = parsed_json.get("answers")
#                     except json.JSONDecodeError:
#                         # If the second parsing attempt fails, regenerate the question
#                         question_response = promptmakerbydefault(keyword, test_level_intensity, test_language)
#                         try:
#                             # Parse the regenerated JSON question
#                             question_data = json.loads(question_response)
#                             question = question_data.get("question", "")
#                             raw_answers = question_data.get("answers", [])
#                         except json.JSONDecodeError:
#                             # If regeneration also fails, handle the error appropriately
#                             question = "Error parsing the question even after regeneration."
#                             raw_answers = []


#                 with col1:
#                     st.markdown(f"**Question:** {question}")
#                     answers = reformat_answers(raw_answers)
#                     if answers:
#                         st.markdown("**Answers:**")
#                         for ans in answers:
#                             st.write(ans)

#             # Feedback options in col2
#             with col2:
#                 user_choice = st.radio("Do you like it?", ['Yes', 'No'], key=f'like_{keyword}')
#                 st.session_state.user_satisfaction[keyword] = user_choice

#                 if user_choice == 'No':
#                     reason = st.text_area(f"Enter reason:", key=f'reason_{keyword}', height=100)
#                     if st.button(f'Regenerate', key=f'regenerate_{keyword}'):
#                         # print(reason)
#                         # print(remove_brackets_and_quotes(question_response))
#                         new_question_json = promptmakerwhenno(keyword, reason, test_level_intensity, remove_brackets_and_quotes(question_response), test_language)
#                         st.session_state.questions[keyword] = new_question_json
#                         feedback_entry = (keyword, question_response, reason)
#                         st.session_state.feedback.append(feedback_entry)

#                         # Update col1 with the new question
#                         col1.empty()
#                         with col1:
#                             try:
#                                 # Parse the JSON structure of the regenerated question
#                                 new_question_data = json.loads(new_question_json)
#                                 new_question = new_question_data.get("question", "")
#                                 new_answers = new_question_data.get("answers", [])
#                             except json.JSONDecodeError:
#                                 new_question = new_question_json
#                                 new_answers = []

#                             st.markdown(f"**Regenerated Question:** {new_question}")
#                             if new_answers:
#                                 st.markdown("**Answers:**")
#                                 for ans in new_answers:
#                                     st.write(ans)
#                                     st.session_state.user_satisfaction[keyword] = 'Yes'


# Button to start a new session
# st.info("Click 'Start Question Generation Process' to begin generating questions. If you want to generate a question again for another user but have a similar tech stack, you can add keywords and click Start Question Generation Process.")

# Function to start a new session
def start_new_session():
    st.session_state.csv_filenames['accepted'] = get_unique_filename('accepted_questions')
    st.session_state.csv_filenames['rejected'] = get_unique_filename('rejected_feedback')
    st.session_state.questions = {}  # Clear previous session questions
    st.session_state.feedback = []  # Clear previous session feedback
    st.session_state.session_started = True  # Set session as started
    st.session_state.download_file_paths = {'accepted': None, 'rejected': None}
    st.session_state.ready_to_generate = True
    st.session_state.current_keyword_index = 0
    st.session_state.user_satisfaction = {}

            

# Dropdown to select a keyword
# selected_keyword = st.selectbox('Select a keyword to generate a question:', list(st.session_state.keywords.keys()))
# Initialize necessary session state variables if they are not already set

def next_keyword():
    if st.session_state.current_keyword_index < len(st.session_state.keywords) - 1:
        st.session_state.current_keyword_index += 1
    else:
        st.write("All keywords have been processed.")
    st.experimental_rerun()
# Main app logic
# st.title('Keyword Question Generation')
st.header('Generate Questions Based on Keywords')
# Button to start a new session
if st.button('Start Process'):
    start_new_session()


# if st.session_state.session_started:
    

#     if not st.session_state.keywords:
#         st.write("No keywords available. Please add keywords to proceed.")
#     else:
#         # Get the current keyword based on the index
#         keywords = list(st.session_state.keywords.keys())
#         if st.session_state.current_keyword_index < len(keywords):
#             current_keyword = keywords[st.session_state.current_keyword_index]
#             if st.session_state.current_keyword_index < len(keywords):
#                 current_keyword = keywords[st.session_state.current_keyword_index]
#                 st.write(f"Current Keyword: **{current_keyword}**")
#         else:
#             current_keyword = None

#         if current_keyword:
#             # Use columns to display the question and satisfaction check side by side
#             col1, col2 = st.columns([3, 1])

#             with col1:
#                 # Generate and display question for the current keyword
#                 if current_keyword not in st.session_state.questions:
#                     response = promptmakerbydefault(current_keyword, st.session_state.test_level_intensity, test_language)
#                     st.session_state.questions[current_keyword] = response

#                 question_response = st.session_state.questions[current_keyword]
#                 try:
#                     question_data = json.loads(question_response)
#                     question = question_data.get("question", "")
#                     raw_answers = question_data.get("answers", [])
#                 except json.JSONDecodeError:
#                     parts = question_response.split('\n\n', 1)
#                     json_part = parts[0]
#                     text_part = parts[1] if len(parts) > 1 else ""
            
#                     # Try parsing the JSON part to extract the question and answers
#                     try:
#                         parsed_json = json.loads(json_part)
#                         question = parsed_json.get("question")
#                         raw_answers = parsed_json.get("answers")
#                     except json.JSONDecodeError:
#                         # If the second parsing attempt fails, regenerate the question
#                         question_response = promptmakerbydefault(keyword, test_level_intensity, test_language)
#                         try:
#                             # Parse the regenerated JSON question
#                             question_data = json.loads(question_response)
#                             question = question_data.get("question", "")
#                             raw_answers = question_data.get("answers", [])
#                         except json.JSONDecodeError:
#                             # If regeneration also fails, handle the error appropriately
#                             question = "Error parsing the question even after regeneration."
#                             raw_answers = []
                
#                 st.markdown(f"**Question:** {question}")
#                 answers = reformat_answers(raw_answers)
#                 if answers:
#                     st.markdown("**Answers:**")
#                     for ans in answers:
#                         st.write(ans)

#             with col2:
#                 # User satisfaction check
#                 user_choice = st.radio("Are you satisfied with this question?", ['Yes', 'No'], key=f'satisfaction_{current_keyword}')
#                 if user_choice == 'No':
#                     reason = st.text_area("Enter reason:", key=f'reason_{current_keyword}', height=100)
#                     if st.button('Submit Feedback and Regenerate', key=f'feedback_{current_keyword}'):
#                         new_question_json = promptmakerwhenno(current_keyword, reason, st.session_state.test_level_intensity, remove_brackets_and_quotes(question_response), test_language)
#                         st.session_state.questions[current_keyword] = new_question_json
#                         feedback_entry = (current_keyword, question_response, reason)
#                         st.session_state.feedback.append(feedback_entry)
#                         st.experimental_rerun()

#             # Disable the 'Next Question' button on the last keyword
#             if st.session_state.current_keyword_index < len(keywords) - 1:
#                 if st.button('Next Question', key='next_question'):
#                     next_keyword()
#             else:
#                 st.success("You have reviewed all the keywords.")
                

#         else:
#             st.write("All keywords have been processed.")
            
#             st.session_state.ready_to_generate = False

if st.session_state.session_started:
    if not st.session_state.keywords:
        st.write("No keywords available. Please add keywords to proceed.")
    else:
        keywords = list(st.session_state.keywords.keys())
        if st.session_state.current_keyword_index < len(keywords):
            current_keyword = keywords[st.session_state.current_keyword_index]
            st.write(f"Current Keyword: **{current_keyword}**")

            col1, col2 = st.columns([3, 1])
            with col1:
                if current_keyword not in st.session_state.questions:
                    with st.spinner(f'Generating question for "{current_keyword}"...'):
                        response = promptmakerbydefault(current_keyword, st.session_state.test_level_intensity, test_language)
                        st.session_state.questions[current_keyword] = response

                question_response = st.session_state.questions[current_keyword]
                try:
                    question_data = json.loads(question_response)
                    question = question_data.get("question", "")
                    raw_answers = question_data.get("answers", [])
                except json.JSONDecodeError:
                    parts = question_response.split('\n\n', 1)
                    json_part = parts[0]
                    text_part = parts[1] if len(parts) > 1 else ""
            
                    try:
                        parsed_json = json.loads(json_part)
                        question = parsed_json.get("question")
                        raw_answers = parsed_json.get("answers")
                    except json.JSONDecodeError:
                        question_response = promptmakerbydefault(current_keyword, st.session_state.test_level_intensity, test_language)
                        try:
                            question_data = json.loads(question_response)
                            question = question_data.get("question", "")
                            raw_answers = question_data.get("answers", [])
                        except json.JSONDecodeError:
                            question = "Error parsing the question even after regeneration."
                            raw_answers = []
                
                st.markdown(f"**Question:** {question}")
                answers = reformat_answers(raw_answers)
                if answers:
                    st.markdown("**Answers:**")
                    for ans in answers:
                        st.write(ans)

            with col2:
                user_choice = st.radio("Are you satisfied with this question?", ['Yes', 'No'], key=f'satisfaction_{current_keyword}')
                if user_choice == 'No':
                    reason = st.text_area("Enter reason:", key=f'reason_{current_keyword}', height=100)
                    if st.button('Submit Feedback and Regenerate', key=f'feedback_{current_keyword}'):
                        new_question_json = promptmakerwhenno(current_keyword, reason, st.session_state.test_level_intensity, remove_brackets_and_quotes(question_response), test_language)
                        st.session_state.questions[current_keyword] = new_question_json
                        feedback_entry = (current_keyword, question_response, reason)
                        st.session_state.feedback.append(feedback_entry)
                        st.experimental_rerun()

            if st.session_state.current_keyword_index < len(keywords) - 1:
                if st.button('Save and Continue'):
                    next_keyword()
            else:
                st.success("You have reviewed all the keywords.")
        else:
            st.write("All keywords have been processed.")
            st.session_state.ready_to_generate = False
                            
# # Save the current question to the list
# if st.button('Save this question'):
#     if selected_keyword in st.session_state.questions:
#         st.session_state.saved_questions.append(st.session_state.questions[selected_keyword])
#         st.success('Question saved.')


def rename_and_move_csv(old_path, new_name):
    if new_name and os.path.exists(old_path):
        # Extract directory and file extension
        directory, _ = os.path.split(old_path)
        extension = os.path.splitext(old_path)[1]

        # Construct new file path
        new_path = os.path.join(directory, new_name + extension)

        # Rename and move the file
        shutil.move(old_path, new_path)
        return new_path
    return old_path

# When finalizing and saving to CSV
if st.button('Finalize and Save to CSV'):
    write_accepted_questions_to_csv(st.session_state.questions, st.session_state.csv_filenames['accepted'])
    write_rejected_feedback_to_csv(st.session_state.feedback, st.session_state.csv_filenames['rejected'])
    st.success('Data has been saved to CSV files.')

    # Update the download paths in the session state
    st.session_state.download_file_paths['accepted'] = st.session_state.csv_filenames['accepted']
    st.session_state.download_file_paths['rejected'] = st.session_state.csv_filenames['rejected']

    # Prepare renaming fields
    st.session_state.ready_to_rename = True

# if 'ready_to_rename' in st.session_state and st.session_state.ready_to_rename:
#     new_accepted_name = st.text_input('Rename accepted questions CSV:', value='accepted_questions')
#     # new_rejected_name = st.text_input('Rename rejected feedback CSV:', value='rejected_feedback')

#     if st.button('Rename and Prepare for Download'):
#         # Rename and update the file paths
#         st.session_state.download_file_paths['accepted'] = rename_and_move_csv(st.session_state.download_file_paths['accepted'], new_accepted_name)
#         # st.session_state.download_file_paths['rejected'] = rename_and_move_csv(st.session_state.download_file_paths['rejected'], new_rejected_name)
#         st.session_state.ready_to_rename = False
#         st.success('Files have been renamed and are ready for download.')

# Display download links for CSV files if they are available
if 'download_file_paths' in st.session_state:
    if st.session_state.download_file_paths['accepted']:
        with open(st.session_state.download_file_paths['accepted'], 'rb') as f:
            st.download_button('Download Accepted Questions CSV', f, file_name=os.path.basename(st.session_state.download_file_paths['accepted']), mime='text/csv')

    # if st.session_state.download_file_paths['rejected']:
    #     with open(st.session_state.download_file_paths['rejected'], 'rb') as f:
    #         st.download_button('Download Rejected Feedback CSV', f, file_name=os.path.basename(st.session_state.download_file_paths['rejected']), mime='text/csv')
# Function to run JavaScript
