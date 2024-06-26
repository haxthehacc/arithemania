import pandas as pd
import google.generativeai as genai
from flask import Flask, render_template
import pandas as pd
from google.generativeai import configure, GenerativeModel
import gensim
from gensim.parsing.preprocessing import preprocess_string
import matplotlib.pyplot as plt

# Import libraries (assuming you have them installed)

from google.generativeai import configure, GenerativeModel

# Replace with your Gemini API key
GEMINI_API_KEY = 'your_API_key'

# Configure Gemini API with your key
configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-pro')

# Define functions to handle user requirements (same as before)
def print_column_content(data, column_name):
    return(data[column_name])

def search_by_keyword(data, keyword,studytitle):
    search_results = data[data[studytitle].str.contains(keyword, case=False, na=False)]
    return(search_results)

def gem_analysis(data):
  a = input("Prompt: ")
  question = f"""
  You are given a dataframe with name {data} with columns {data.columns}, and a prompt {a}.
  Your response should include only the factors mentioned in the prompt, unless the prompt is something like 'none' or 'summarize', in which case you must include all the factors in your response.
  Additionally, statistics of the prompt, like percentages or averages, should be included if possible.
  For example:
  Prompt:
  Give me the most common methods of intervention

  Response:
  The most common methods of intervention are:
  1. Chemotherapy (65.4%)
  2. Procedural medication (21.2%)
  etc.

  Notes:
  For sexes, there are two, Male and Female, and 'all' counts for both of these, unless the prompt mentions 'only female' or 'only male'; in that case, 'all' does not count for either.
  Usage of 'Male' or 'Female' refers to sexes.
  For average time of trials, find the number of days between completion date of the trial and start date of the trial.
  """
  response = model.generate_content(question)
  print(response.text)

def gem_analysis_col(data):
  a = input("Prompt: ")
  question = f"""
  You are given a dataframe with name {data}, and a prompt {a}.
  Your response should include only the factors mentioned in the prompt, unless the prompt is something like 'none' or 'summarize', in which case you must include all the factors in your response.
  Additionally, statistics of the prompt, like percentages or averages, should be included if possible.
  For example:
  Prompt:
  Give me number of study results being 'No'

  Response:
  There are 501 study results reporting 'No'.

  Notes:
  For sexes, there are two, Male and Female, and 'all' counts for both of these.
  """
  response = model.generate_content(question)
  print(response.text)

def get_title(data,title):
  cols = [x for x in data.columns]
  question = f"You are given a list of column names - {cols}. Find the column name that is the most similar to '{title}'. The response should simply be that column name."
  response = model.generate_content(question)
  return response.text

# Chatbot logic
def chatbot():
    print("Welcome to Metis!")
    data = pd.read_csv("cleaned_clinical_trials.csv")
    #data = pd.read_csv("cleaned_clinical_trials.csv")

    # Use Gemini model (choose "gemini-1.0-pro-latest" for text-only)
    model = GenerativeModel("gemini-1.0-pro-latest")  # Update for specific model
    studytitle = get_title(data,"Study Title")
    while True:
        user_intent = input("How can I assist you? ").strip().lower()
        # Determine user's intent (same logic as before)
        if "print column" in user_intent:
            column_name = user_intent.split("print column ")[1]
            column_name = get_title(data,column_name)
            gem_inp = print_column_content(data, column_name)
            gem_analysis_col(gem_inp)
        elif "search for keyword" in user_intent:
            keyword = user_intent.split("search for keyword ")[1]
            gem_inp = search_by_keyword(data, keyword,studytitle)
            gem_analysis(gem_inp)
        elif user_intent == "exit":
            print("Goodbye!")
            break
        else:
            print("Sorry, I didn't understand that.")


# Run the chatbot
chatbot()


# Ensure plots are displayed inline
%matplotlib inline

def visualize_distribution(data, column_name):
    """
    This function visualizes the distribution of a column in the data.

    Args:
        data (pd.DataFrame): The clinical trial data.
        column_name (str): The name of the column to visualize.
    """
    data[column_name].value_counts().plot(kind='bar')
    plt.xlabel(column_name)
    plt.ylabel("Count")
    plt.title(f"Distribution of {column_name}")
    plt.show() # Display the plot

def identify_topics(documents):
  """
  This function identifies topics within a list of clinical text documents.

  Args:
      documents (list): A list of strings containing the clinical text data.

  Returns:
      list: A list of dominant topics identified within the documents.
  """
  processed_docs = [preprocess_string(doc) for doc in documents]
  dictionary = gensim.corpora.Dictionary(processed_docs)
  corpus = [dictionary.doc2bow(doc) for doc in documents]
  lda_model = gensim.models.LdaModel(corpus, id2word=dictionary, num_topics=5)
  topics = lda_model.print_topics()
  return topics

import spacy

# Load a pre-trained spaCy model for clinical text processing (consider using a specialized model for better results)
nlp = spacy.load("en_core_web_sm")

def summarize_clinical_text(text):
  """
  This function performs basic NLP tasks to summarize clinical text data.

  Args:
      text (str): The clinical text data to be summarized.

  Returns:
      str: A summary of the text containing key entities and potential insights.
  """
  doc = nlp(text)

  # Extract named entities like medications and diagnoses
  entities = [str(ent.text) for ent in doc.ents]

  # Identify potential insights based on sentiment analysis (basic example)
  sentiment = "positive" if doc.sentiment > 0 else "negative"

  summary = f"The provided text mentions {', '.join(entities)} related to the patient's condition. The overall sentiment seems {sentiment}."

  return summary

# Example usage
text = "The patient reported feeling better after taking the new medication. They mentioned some initial side effects but overall felt the treatment was effective."
summary = summarize_clinical_text(text)
print(summary)
