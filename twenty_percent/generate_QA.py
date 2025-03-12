import json

def generate_qa_pairs(code_data):
    """
    Generates question-answer pairs from code analysis data.

    Args:
        code_data: A list of dictionaries, where each dictionary represents
                   a code chunk and contains keys like 'repo_name',
                   'filepath', 'function_name', 'code_chunk', 'variables',
                   and 'docstring'.

    Returns:
        A list of dictionaries, where each dictionary is a Q&A pair
        with keys 'question' and 'answer'.
    """

    qa_pairs = []

    for item in code_data:
        print('item', item)
        function_name = item['function_name']
        code_chunk = item['code_chunk']
        docstring = item['docstring']
        variables = item['variables']
        filepath = item['filepath']
        repo = item['repo_name']


        # --- Standard Questions ---

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
            'answer': "Based on the code, the output appears to be a DataFrame, `result_df`, but this is test code, so there is no return",  # Adapt based on code analysis
            'context': code_chunk
        })

        for var in variables:
            qa_pairs.append({
                'question': f"What is the purpose of the variable '{var}' in the function '{function_name}'?",
                'answer': f"Based on the code, '{var}' appears to be used for ...",  # Requires code analysis
                'context': code_chunk
            })

        # --- Docstring Accuracy ---

        qa_pairs.append({
            'question': f"Does the docstring '{docstring}' accurately describe the function '{function_name}'?",
            'answer': "Yes / No / Partially. Explanation...",  # Requires code analysis
            'context': code_chunk
        })

        # --- Additional Challenging Questions ---
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
            'answer': "Possible edge cases include...",  # Requires deeper code analysis
            'context': code_chunk
        })

        qa_pairs.append({
            'question': f"How could the function '{function_name}' be improved for readability or efficiency?",
            'answer': "Possible improvements include...", # Requires code analysis
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

#--- Example Usage ---
if __name__ == '__main__':
    # Load the JSON data (replace with your actual file)
    json_file_path = "/home/jonny/python/dictionary_output/rdsa-utils_code_dataset.json"
    with open(json_file_path, 'r') as f:
        code_data = json.load(f)

    # Generate Q&A pairs
    qa_data = generate_qa_pairs(code_data)

    # Print the generated Q&A pairs (or save to a file)
    for qa_pair in qa_data:
        print(f"Q: {qa_pair['question']}")
        print(f"A: {qa_pair['answer']}")
        print(f"Context: {qa_pair['context']}")
        print("-" * 20)

    # Example of saving to a JSONL file for fine-tuning:
    with open('/home/jonny/python/dictionary_output/qa_data.json', 'w') as outfile:
        for qa_pair in qa_data:
            print(qa_pair)
            json.dump(qa_pair, outfile)
            outfile.write('\n')