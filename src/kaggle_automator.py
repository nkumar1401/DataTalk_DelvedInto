import os
import json
import time
from kaggle.api.kaggle_api_extended import KaggleApi
import streamlit as st

def autonomous_kaggle_run(df, script_content):
    """
    Automates the full Kaggle lifecycle: Data Upload -> Script Push -> Execution.
    Handles 403 Forbidden errors via Safe-Buffer Failover.
    """
    try:
        # 1. Setup API and Authenticate
        api = KaggleApi()
        api.authenticate()
        
        user_id = api.get_config_value('username') or "your_username"
        folder_path = 'kaggle_staging'
        os.makedirs(folder_path, exist_ok=True)

        # 2. Prepare Dataset
        df.to_csv(f'{folder_path}/data.csv', index=False)
        
        ds_metadata = {
            "title": "DataTalk Auto-Generated Dataset",
            "id": f"{user_id}/datatalk-ds-{int(time.time())}",
            "licenses": [{"name": "CC0-1.0"}]
        }
        with open(f'{folder_path}/dataset-metadata.json', 'w') as f:
            json.dump(ds_metadata, f)

        # Upload Dataset
        st.write("📤 Uploading dataset to Kaggle...")
        api.dataset_create_new(folder_path, quiet=True)
        
        # ⚡ BYPASS 403: Instead of polling GetDatasetStatus (which triggers 403),
        # we use a Safe-Buffer wait to allow Kaggle servers to index the files.
        st.write("⏳ Cooling off for cloud indexing (20s)...")
        time.sleep(20) 

        # 3. Prepare and Push Kernel
        with open(f'{folder_path}/script.py', 'w') as f:
            f.write(script_content)
            
        unique_id = int(time.time())
        kernel_slug = f"datatalk-run-{unique_id}"    
        kernel_id = f"{user_id}/{kernel_slug}"

        kernel_metadata = {
            "id": kernel_id,
            "title": f"DataTalk Run {unique_id}",
            "code_file": "script.py",
            "language": "python",
            "kernel_type": "script",
            "is_private": "true",
            "enable_gpu": "true",
            "dataset_sources": [ds_metadata["id"]]
        }
        with open(f'{folder_path}/kernel-metadata.json', 'w') as f:
            json.dump(kernel_metadata, f)

        # Push the Kernel
        api.kernels_push(folder_path)
        st.success(f"🚀 Tournament Launched: {kernel_id}")
        
        # --- RESILIENT POLLING LOGIC ---
        max_wait = 600
        start_time = time.time()
        retry_exhausted = 0
        
        while time.time() - start_time < max_wait:
            try:
                response = api.kernels_status(kernel_id)
                current_state = getattr(response, 'status', 'unknown')
                
                if current_state == 'complete':
                    # Download outputs (logs) to extract the prediction
                    api.kernels_output(kernel_id, path=folder_path)
                    return f"🎯 Analysis Complete! View results on Kaggle or check logs. ID: {kernel_id}"
                    
                elif current_state == 'error':
                    return f"❌ Kernel Error. Check live: https://www.kaggle.com/code/{kernel_id}"
                
                retry_exhausted = 0 # Reset on success
            except Exception:
                retry_exhausted += 1
                if retry_exhausted >= 3:
                    # ⚡ FLASH ESCAPE: If 3 retries fail, give the user the direct link
                    return f"⚡ API Busy. Your model is training! Track it live: https://www.kaggle.com/code/{kernel_id}"
            
            time.sleep(20) 
            
        return f"⏳ Compute timeout. View live: https://www.kaggle.com/code/{kernel_id}"

    except Exception as e:
        if "403" in str(e):
            return "⚠️ Kaggle 403: Please ensure your account is phone-verified in Kaggle Settings."
        return f"⚠️ Cloud Orchestration Error: {str(e)}"