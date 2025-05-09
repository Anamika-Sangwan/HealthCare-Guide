from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
# from generation.generation_template import GenerationModel
from dotenv import load_dotenv
import os
import json
import argparse
import logging

from langchain_core.prompts import ChatPromptTemplate
from typing import List
from pydantic import BaseModel, Field

# Load dotenv
load_dotenv()

os.getenv('GENERATOR_MODEL')

data_path = os.path.join(os.path.dirname(
    os.path.abspath('.env')), os.getenv('DATA_PATH'))
out_path = os.path.join(os.path.dirname(
    os.path.abspath('.env')), os.getenv('OUT_PATH'))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

data_path, out_path


def is_json_serializable(obj):
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False
    
transcript_file = 'CAR0001.txt'

os.path.join(data_path,transcript_file )

with open(os.path.join(data_path, transcript_file), 'r') as f:
  lines = f.readlines()
    # print(lines)
  query = "Based on the history session transcript, summarize the patient's  history following the below instructions. Note that `P: ` means the patient and `D: ` means doctor in the transcript.\n\n{lines}".format(lines=lines)
    # print(query)

    # pydantic_parser = PydanticOutputParser(
    #     pydantic_object=GenerationModel.CognitiveConceptualizationDiagram)

    # _input = GenerationModel.prompt_template.invoke({
    #     "query": query,
    #     "format_instructions": pydantic_parser.get_format_instructions()
    # })
    # llm = ChatOpenAI(
    #     model=os.getenv('GENERATOR_MODEL'),
    #     temperature=os.getenv('GENERATOR_MODEL_TEMP'),
    #     max_retries=2,
    # )

lines

len(lines),lines[0:3]

type(query)

query

print(query)

class GenerationModel_2:
    prompt_template = ChatPromptTemplate.from_messages([
        ('system', 'You are a third year medical student. You have just ended a interaction session with a patient. Your goal is to reconstruct a structured medical hisory presentation format based on your patient conversation to present to your professor for discussing about the patient'),
        ('user', '{query}\n\nFormat instructions:\n{format_instructions}You should follow the concepts of history taking in medical domain for aiding a comprehensive diagnosis')
    ])

    class PatientHistoryStructuredFormat(BaseModel):
      personal_details: str = Field(
        ...,
        description="This field is intended to get only personal details such as age, sex, residential city or town, marital status etc. The field is not intended to include any medical history details and only personal demogrpahics details.")
      chief_complaints: str = Field(
        ...,
        description="This field is intended to capture only the major complaint or initial complaint that made him to seek doctor consulatation such as chest pain, headcahe etc")
      family_history: str = Field(
        ...,
        description="This field is intended to capture the family history to know about diseases that might run in the family such as heart ache, diabetes etc).")
      
pydantic_parser = PydanticOutputParser(
    pydantic_object=GenerationModel_2.PatientHistoryStructuredFormat)

pydantic_parser

print(pydantic_parser.get_format_instructions())

_input = GenerationModel_2.prompt_template.invoke({
    "query": query,
    "format_instructions": pydantic_parser.get_format_instructions()
})

_input

print(_input.messages[0].content)

print(_input.messages[1].content)

llm = ChatOpenAI(
    model=os.getenv('GENERATOR_MODEL'),
    temperature=os.getenv('GENERATOR_MODEL_TEMP'),
    max_retries=2,
)

_output = pydantic_parser.parse(
    llm.invoke(_input).content).model_dump()
print(_output)

_output.keys()

out_file = "Structured_PatientHistory_Format_from_transcript.json"
os.path.join(out_path, out_file)

if is_json_serializable(_output):
    with open(os.path.join(out_path, out_file), 'w') as f:
        f.write(json.dumps(_output, indent=4))
    logger.info(f"Output successfully written to {out_file}")

# prompt: reading example_CCD_from_transcript.json file

import json
import os

# Assuming 'example_CCD_from_transcript.json' is in the current working directory or you provide the correct path
file_path =os.path.join(out_path, out_file)  # Replace with the actual path if needed

try:
    with open(file_path, 'r') as f:
        data = json.load(f)
        print(data)  # Print the entire JSON data
        # Access specific elements
        # Example: If the JSON contains a "summary" key:
        # if "summary" in data:
            # print(data["summary"])
except FileNotFoundError:
    print(f"Error: File '{file_path}' not found.")
except json.JSONDecodeError:
    print(f"Error: Invalid JSON format in '{file_path}'.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

type(data)

data.keys()

import pandas as pd

pd.set_option('display.max_colwidth', None) # set to None to display the full string