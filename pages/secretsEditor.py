import streamlit as st
import yaml
import os
from datetime import datetime
import shutil

# Custom CSS to mimic VSCode style
st.markdown("""
    <style>
    .main {
        background-color: #1e1e1e;
        color: #d4d4d4;
    }
    .stTextInput, .stNumberInput, .stCheckbox {
        background-color: #252526;
        color: #d4d4d4;
        border: 1px solid #3c3c3c;
    }
    .stButton button {
        background-color: #007acc;
        color: white;
        border: none;
    }
    .stButton button:hover {
        background-color: #005a9e;
    }
    .stForm {
        border: 1px solid #3c3c3c;
        padding: 20px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

def load_secrets():
    try:
        with open(r"D:\ai-assistant\FAM\conf\secrets.yaml", 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        st.error(f"Error loading secrets file: {str(e)}")
        return None

def save_secrets(data):
    try:
        # Create backup
        backup_path = f"D:\\ai-assistant\\FAM\\conf\\secrets.yaml.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(r"D:\ai-assistant\FAM\conf\secrets.yaml", backup_path)
        
        # Save new content
        with open(r"D:\ai-assistant\FAM\conf\secrets.yaml", 'w') as file:
            yaml.safe_dump(data, file, default_flow_style=False)
        return True
    except Exception as e:
        st.error(f"Error saving secrets file: {str(e)}")
        return False

def render_dict_editor(data, parent_key=""):
    updates = {}
    
    for key, value in data.items():
        full_key = f"{parent_key}.{key}" if parent_key else key
        
        if isinstance(value, dict):
            st.subheader(key)
            nested_updates = render_dict_editor(value, full_key)
            if nested_updates:
                updates[key] = nested_updates
        else:
            if isinstance(value, (int, float)):
                new_value = st.number_input(key, value=value, key=full_key)
            elif isinstance(value, bool):
                new_value = st.checkbox(key, value=value, key=full_key)
            else:
                new_value = st.text_input(key, value=str(value), key=full_key)
            
            if new_value != value:
                updates[key] = new_value
    
    return updates

def main():
    st.title("Secrets Configuration Editor")
    
    secrets = load_secrets()
    if not secrets:
        return

    st.write("Edit your secrets configuration below:")
    
    with st.form("secrets_editor"):
        updates = render_dict_editor(secrets)
        
        if st.form_submit_button("Save Changes"):
            if updates:
                # Update the original data structure
                def update_dict(original, updates):
                    for key, value in updates.items():
                        if isinstance(value, dict) and key in original:
                            update_dict(original[key], value)
                        else:
                            original[key] = value
                
                update_dict(secrets, updates)
                
                if save_secrets(secrets):
                    st.success("Secrets file updated successfully!")
                    st.rerun()

if __name__ == "__main__":
    main()
