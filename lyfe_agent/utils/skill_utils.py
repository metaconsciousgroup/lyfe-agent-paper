from pathlib import Path
import re
import logging

logger = logging.getLogger(__name__)


def load_js_files(folder_path):
    """
    Load JS files from a specified folder, extracting the entire JSDoc style comments,
    and using the first line of the docstring as the high-level description.

    Args:
        folder_path: Path to the folder containing the JS files.

    Returns:
        A list of dictionaries, where each dictionary contains the following keys:
            key: The name of the function.
            description: The first line of the docstring, serving as the high-level description of the function.
            docstring: The entire docstring of the function.
            code: The code of the function.
    """
    js_files_data = []
    folder = Path(folder_path)

    if not folder.exists() or not folder.is_dir():
        logger.info(f"The provided path '{folder_path}' does not exist or is not a directory.")
        return js_files_data
    
    for file_path in folder.glob('*.js'):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

                # Extracting the JSDoc docstring
                description_match = re.search(r'/\*\*[\s\S]*?\*/', content)
                if description_match:
                    docstring = description_match.group(0).strip()
                    
                    docstring_cleaned = re.sub(r'^/\*\*|\*/$', '', docstring)  # Remove the opening /** and closing */
                    docstring_lines = docstring_cleaned.split('\n')
                    
                    # Filter out empty lines and lines that only contain an asterisk
                    docstring_lines = [line.strip(' *') for line in docstring_lines if line.strip(' *\r')]
                    
                    # The first non-empty line after cleaning is the high-level description
                    high_level_description = docstring_lines[0] if docstring_lines else "No description"
                else:
                    docstring = "No docstring"
                    high_level_description = "No description"

                # Extracting the code (assuming code starts after the docstring)
                code = content[description_match.end():].strip() if description_match else content
                
                # Using file stem for the key
                key = file_path.stem

                js_files_data.append({
                    "key": key,
                    "description": high_level_description,
                    "docstring": docstring,
                    "code": code
                })
        except Exception as e:
            logger.error(f"An error occurred while processing '{file_path}': {e}")
    
    logger.info(f"Loaded {len(js_files_data)} functions from {folder_path}")

    return js_files_data

if __name__ == "__main__":
    # Usage example
    from pprint import pprint
    folder_path = Path(__file__).resolve().parent.parent / "skills" / "minecraft" / "verified"
    js_data = load_js_files(folder_path)
    for data in js_data:
        pass
        pprint(data)
