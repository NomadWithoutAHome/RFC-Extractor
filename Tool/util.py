import os
import UnityPy
from pathlib import Path

class RFCExtractor:
    def __init__(self):
        pass

    def extract_files(self, input_file, output_dir, progress_callback=None):
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Load the .rfc file
            env = UnityPy.load(input_file)
            
            # Get total number of TextAssets
            total_assets = sum(1 for obj in env.objects if obj.type.name == "TextAsset")
            if total_assets == 0:
                return False, "No .bytes files found in the selected RFC file."
            
            # Initial progress update
            if progress_callback:
                progress_callback(0, total_assets, "Starting extraction...")
                
            # Extract files
            extracted_count = 0
            
            for obj in env.objects:
                if obj.type.name == "TextAsset":
                    data = obj.read()
                    
                    # Get the raw bytes from the TextAsset
                    raw_data = data.m_Script
                    if raw_data is not None:
                        # Convert to bytes if it's not already
                        if isinstance(raw_data, str):
                            raw_data = raw_data.encode('utf-8')
                        elif not isinstance(raw_data, bytes):
                            raw_data = bytes(raw_data)
                            
                        # Use the original file name from m_Name
                        file_name = f"{data.m_Name}.bytes"
                        output_path = os.path.join(output_dir, file_name)
                        
                        with open(output_path, "wb") as f:
                            f.write(raw_data)
                        
                        extracted_count += 1
                        
                        # Update progress if callback provided
                        if progress_callback:
                            progress_callback(extracted_count, total_assets, file_name)
            
            # Final progress update
            if progress_callback:
                progress_callback(total_assets, total_assets, "Extraction complete!")
            
            return True, extracted_count
            
        except Exception as e:
            if progress_callback:
                progress_callback(0, 100, f"Error: {str(e)}")
            return False, str(e) 