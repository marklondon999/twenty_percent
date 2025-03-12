import json
import requests

OLLAMA_API_ENDPOINT = "http://localhost:11434/api/generate"  # Ollama API
OLLAMA_MODEL = "llama3.2:3b"  # Replace with your desired Ollama model
PLACEHOLDER = "TO_BE_FILLED_BY_LLM"

def generate_qa_pairs(code_data):
    """Generates question-answer pairs, marking those needing LLM completion."""
    qa_pairs = []

    for item in code_data:
        function_name = item['function_name']
        code_chunk = item['code_chunk']
        docstring = item['docstring']
        variables = item['variables']
        filepath = item['filepath']
        repo = item['repo_name']

        qa_pairs.append({
            'question': f"What does the function '{function_name}' do?",
            'answer': docstring,
            'context': code_chunk
        })

        qa_pairs.append({
            'question': f"What are the input parameters for the function '{function_name}'?",
            'answer': "Based on the code, the input parameters appear to be: " + ", ".join([v for v in variables if v != 'self']),
            'context': code_chunk
        })

        qa_pairs.append({
            'question': f"What is the output of the function '{function_name}'?",
            'answer': "Based on the code, the output appears to be a DataFrame, `result_df`, but this is test code, so there is no return",
            'context': code_chunk
        })

        for var in variables:
            qa_pairs.append({
                'question': f"What is the purpose of the variable '{var}' in the function '{function_name}'?",
                'answer': PLACEHOLDER,  # Mark for LLM completion
                'context': code_chunk
            })
        qa_pairs.append({
            'question': f"Does the docstring '{docstring}' accurately describe the function '{function_name}'?",
            'answer': PLACEHOLDER,
            'context': code_chunk
        })

        qa_pairs.append({
            'question': f"What external functions or methods are called within the function '{function_name}'?",
            'answer': "Based on the code, the external calls are: " + ", ".join([call for call in ['create_spark_df', 'union_mismatched_dfs', 'assert_df_equality']]),
            'context': code_chunk
          })
        qa_pairs.append({
            "question": f"What is the purpose of the function {function_name}?",
            "answer": docstring,
            'context': code_chunk
        })

        qa_pairs.append({
            'question': f"Identify any potential errors or edge cases in the function '{function_name}'.",
            'answer': PLACEHOLDER,
            'context': code_chunk
        })

        qa_pairs.append({
            'question': f"How could the function '{function_name}' be improved for readability or efficiency?",
            'answer': PLACEHOLDER,
            'context': code_chunk
        })

        qa_pairs.append({
            'question': f"In which file can the function '{function_name}' be found?",
            'answer': f"The function is in the file: {filepath}",
            'context': code_chunk
          })

        qa_pairs.append({
            'question': f"In which repository and file can the function '{function_name}' be found?",
            'answer': f"The function is in repo: {repo} and file: {filepath}",
            'context': code_chunk
          })

        qa_pairs.append({
            'question': f"Write example usage for the function: {function_name}",
            'answer': code_chunk,
            'context': code_chunk
          })

        qa_pairs.append({
            'question': f"Summarise the code: {code_chunk}",
            'answer': docstring,
            'context': code_chunk
          })

        qa_pairs.append({
            'question': f"What are the key variables in function: {function_name}",
            'answer': "The key variables are: "+", ".join(variables),
            'context': code_chunk
          })

    return qa_pairs

def get_ollama_response(prompt, model=OLLAMA_MODEL, stream=False):
    """Gets a response from the Ollama API."""
    print('--------------------------------------------')
    print(prompt)
    try:
        response = requests.post(
            OLLAMA_API_ENDPOINT,
            headers={"Content-Type": "application/json"},
            json={
                "prompt": prompt,
                "model": model,
                "stream": stream,
                "format": "json"
            },
            stream=stream,
        )
        print('xxxxxx')

        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        if stream:
            #not implemented here.
            pass
        else:
            json_data = json.loads(response.text)
            print(response.text)
            return json_data['response']

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama API: {e}")
        return None

def process_qa_data(input_json_file, output_jsonl_file):
    """Loads data, generates Q&A, gets Ollama responses, and saves to JSONL."""
    with open(input_json_file, 'r') as f:
        code_data = json.load(f)

    qa_pairs = generate_qa_pairs(code_data)

    with open(output_jsonl_file, 'w') as outfile:
        for qa_pair in qa_pairs[0:1]:
            print(qa_pair)
            if qa_pair['answer'] == PLACEHOLDER:
                prompt = f"""{qa_pair['context']}

Question: {qa_pair['question']}
Answer:
"""
                answer = get_ollama_response(prompt)
                if answer:
                    qa_pair['answer'] = answer
                else:
                    print(f"Skipping question due to Ollama error: {qa_pair['question']}")
                    continue  # Skip to the next question if there's an error

            json.dump(qa_pair, outfile)
            outfile.write('\n')

    print(f"Processed Q&A data saved to {output_jsonl_file}")

if __name__ == '__main__':
    #input_file = '/home/jonny/python/dictionary_output/qa_data.json'  # Replace with your input JSON file
    input_file = '/home/jonny/python/dictionary_output/test.json'  
    output_file = '/home/jonny/python/dictionary_output/qa_data_with_answers.jsonl'  # Output JSONL file
    process_qa_data(input_file, output_file)