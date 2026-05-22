import os
import re
import asyncio
import edge_tts

# Microsoft Edge TTS Thai female voice
VOICE = "th-TH-PremwadeeNeural"
# Microsoft Edge TTS speed (1.0 = +0%)
RATE = "+0%"

def filter_thai_and_numbers(text):
    """
    Keep only Thai characters, numbers, and whitespaces.
    Removes English letters, #, =, *, and all other punctuation.
    """
    # Regex explanation:
    # \u0E00-\u0E7F: Thai characters
    # 0-9: Numbers
    # \s: Whitespace characters (spaces, newlines, tabs)
    # ^: Negation (match anything that is NOT in the brackets)
    filtered_text = re.sub(r'[^\u0E00-\u0E7F0-9\s]', ' ', text)
    
    # Collapse multiple consecutive spaces/newlines into a single space
    filtered_text = re.sub(r'\s+', ' ', filtered_text).strip()
    return filtered_text

async def main():
    folder_path = r"C:\dev3\file_search69\_DESIGN_TH_"
    
    if not os.path.exists(folder_path):
        print(f"Error: Folder {folder_path} not found.")
        return

    # Process files starting with 01_ to 09_
    for i in range(1, 10):
        prefix = f"{i:02d}_"
        
        # Find matching markdown file in the folder
        for filename in os.listdir(folder_path):
            if filename.startswith(prefix) and filename.upper().endswith(".MD"):
                filepath = os.path.join(folder_path, filename)
                
                print(f"Reading file: {filename}")
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Filter the text to only Thai and numbers
                clean_text = filter_thai_and_numbers(content)
                
                if clean_text:
                    mp3_filename = filename.rsplit('.', 1)[0] + ".mp3"
                    mp3_filepath = os.path.join(folder_path, mp3_filename)
                    
                    print(f"Generating audio: {mp3_filename} ...")
                    try:
                        communicate = edge_tts.Communicate(clean_text, VOICE, rate=RATE)
                        await communicate.save(mp3_filepath)
                        print(f"Saved {mp3_filename} successfully.\n")
                    except Exception as e:
                        print(f"Error generating audio for {filename}: {e}\n")
                else:
                    print(f"No valid Thai text found in {filename}.\n")
                
                # Move to next file prefix
                break

if __name__ == "__main__":
    print("Starting audio generation...")
    asyncio.run(main())
    print("All done!")
