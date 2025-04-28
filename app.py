import streamlit as st
import pandas as pd
import numpy as np
import base64
import csv
from io import StringIO
from datetime import datetime

# Set page title and configuration
st.set_page_config(
    page_title="Arc Inspirations - Stock Count",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Define global theme colors
THEME_PRIMARY = "#6a28e8"  # Main purple shade
THEME_SECONDARY = "#9161fd"  # Lighter purple
THEME_GRADIENT = f"linear-gradient(135deg, {THEME_PRIMARY} 0%, {THEME_SECONDARY} 100%)"
THEME_SUCCESS = "#34C759"  # Green
THEME_WARNING = "#FF9500"  # Orange
THEME_ERROR = "#FF3B30"  # Red

# Apply the purple theme to the app
st.markdown(f"""
<style>
/* Global Theme Styles */
:root {{
    --theme-primary: {THEME_PRIMARY};
    --theme-secondary: {THEME_SECONDARY};
    --theme-success: {THEME_SUCCESS};
    --theme-warning: {THEME_WARNING};
    --theme-error: {THEME_ERROR};
}}

/* Header styling */
h1, h2, h3, h4, h5, h6 {{
    color: {THEME_PRIMARY} !important;
}}

/* Change primary button color to purple */
.stButton > button[data-baseweb="button"] {{
    background-color: {THEME_PRIMARY};
    border-color: {THEME_PRIMARY};
}}

/* Change hover state */
.stButton > button[data-baseweb="button"]:hover {{
    background-color: {THEME_SECONDARY};
    border-color: {THEME_SECONDARY};
}}

/* Change links to purple */
a {{
    color: {THEME_PRIMARY} !important;
}}

/* Change selection color */
::selection {{
    background-color: {THEME_SECONDARY};
    color: white;
}}

/* Custom scrollbar */
::-webkit-scrollbar {{
    width: 10px;
}}

::-webkit-scrollbar-track {{
    background: #f1f1f1;
}}

::-webkit-scrollbar-thumb {{
    background: {THEME_SECONDARY};
    border-radius: 5px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: {THEME_PRIMARY};
}}

/* Streamlit progress bar */
.stProgress > div > div > div > div {{
    background-color: {THEME_PRIMARY};
}}

/* Sidebar */
.css-1d391kg {{
    background-color: #f5f0ff;
}}

/* Custom input fields */
.stTextInput > div > div > input {{
    border-color: #d0bfff !important;
}}
.stTextInput > div > div > input:focus {{
    border-color: {THEME_PRIMARY} !important;
    box-shadow: 0 0 0 1px {THEME_SECONDARY} !important;
}}

/* Change select box color */
.stSelectbox > div > div > div {{
    border-color: #d0bfff !important;
}}
.stSelectbox > div > div > div:focus {{
    border-color: {THEME_PRIMARY} !important;
    box-shadow: 0 0 0 1px {THEME_SECONDARY} !important;
}}

/* Number input */
.stNumberInput > div > div > input {{
    border-color: #d0bfff !important;
}}
.stNumberInput > div > div > input:focus {{
    border-color: {THEME_PRIMARY} !important;
    box-shadow: 0 0 0 1px {THEME_SECONDARY} !important;
}}

</style>
"""
, unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'stock_data' not in st.session_state:
    st.session_state.stock_data = None
if 'count_data' not in st.session_state:
    st.session_state.count_data = {}
if 'current_search' not in st.session_state:
    st.session_state.current_search = ""
if 'filtered_data' not in st.session_state:
    st.session_state.filtered_data = None
if 'sc_closed' not in st.session_state:
    st.session_state.sc_closed = {}
if 'view' not in st.session_state:
    st.session_state.view = "splash"  # "splash" or "main"
if 'raw_csv_content' not in st.session_state:
    st.session_state.raw_csv_content = None
# New session state for historical count data
if 'historical_counts' not in st.session_state:
    st.session_state.historical_counts = {}
# Session state for count batch/session tracking
if 'count_sessions' not in st.session_state:
    st.session_state.count_sessions = []
if 'current_count_session' not in st.session_state:
    st.session_state.current_count_session = {
        "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "timestamp": datetime.now(),
        "name": f"Count Session {datetime.now().strftime('%b %d, %Y %H:%M')}"
    }

# Function to validate CSV structure and map columns
def validate_csv(df):
    # Define column mappings (to handle different possible column names)
    possible_id_columns = ['product_id', 'id', 'item_id', 'sku', 'item_number', 'item#', 'product#', 'barcode', 'code', 'item code', 'product code', 'article number']
    possible_brand_columns = ['brand', 'Brand', 'manufacturer', 'supplier', 'vendor', 'make', 'producer', 'company', 'label', 'maker', 'source', 'Brand and Description', 'Brand & Description']
    possible_description_columns = ['description', 'Description', 'product_description', 'item_description', 'details', 'specs', 'product_name', 'name', 'title', 'item', 'product', 'desc', 'article', 'goods', 'merchandise', 'Brand and Description', 'Brand & Description']
    possible_location_columns = ['location', 'location_id', 'loc', 'warehouse', 'shelf', 'bin', 'storage', 'position', 'area', 'zone', 'aisle', 'section', 'dept', 'department', 'store']
    possible_count_columns = ['expected_count', 'count', 'quantity', 'qty', 'stock', 'inventory', 'on_hand', 'amount', 'units', 'expected', 'expected qty', 'on hand qty', 'stock level', 'current stock', 'stock count', 'current count', '[E]Close SC', 'quantity on hand', 'par', 'par level', 'total', 'balance', 'volume', 'number', 'num']
    
    # Check specifically for the [E]Close SC column since it's important
    close_sc_col = next((col for col in df.columns if col == '[E]Close SC'), None)
    
    # Try exact match first
    id_col = next((col for col in df.columns if col.lower() in [c.lower() for c in possible_id_columns]), None)
    brand_col = next((col for col in df.columns if col.lower() in [c.lower() for c in possible_brand_columns]), None)
    description_col = next((col for col in df.columns if col.lower() in [c.lower() for c in possible_description_columns]), None)
    location_col = next((col for col in df.columns if col.lower() in [c.lower() for c in possible_location_columns]), None)
    count_col = next((col for col in df.columns if col.lower() in [c.lower() for c in possible_count_columns]), None)
    
    # Check specifically for 'Brand & Description' column which combines brand and description
    brand_and_desc_col = next((col for col in df.columns if col in ['Brand & Description', 'Brand and Description']), None)
    
    # If not found, try partial match as a fallback
    if description_col is None:
        for col in df.columns:
            if any(term in col.lower() for term in ['desc', 'name', 'product', 'item', 'title', 'article']):
                description_col = col
                break
    
    if count_col is None:
        # First try partial name matching
        for col in df.columns:
            if any(term in col.lower() for term in ['count', 'qty', 'quant', 'stock', 'amount', 'unit', 'invent', 'par', 'level', 'number', 'vol']):
                count_col = col
                break
                
        # If still not found, try to find any numeric column as a last resort
        if count_col is None:
            for col in df.columns:
                try:
                    # Check if column has numeric values
                    if pd.to_numeric(df[col], errors='coerce').notna().any():
                        # Use the first mostly-numeric column we find
                        if pd.to_numeric(df[col], errors='coerce').notna().mean() > 0.5:  # More than 50% are numbers
                            count_col = col
                            st.info(f"Using '{col}' as the quantity column based on numeric content")
                            break
                except:
                    continue
    
    # Special handling for "Brand & Description" column
    # If we have this column, we should split it into brand and description
    # Look for any column containing both 'brand' and 'description' in any case
    brand_and_desc_cols = [col for col in df.columns if 'brand' in col.lower() and ('description' in col.lower() or 'desc' in col.lower())]
    brand_and_desc_col = None
    
    if brand_and_desc_cols:
        # Use the first matching column
        brand_and_desc_col = brand_and_desc_cols[0]
        st.info(f"Found '{brand_and_desc_col}' column - splitting into brand and description components")
        
        # First, keep the full text for searching (critical for our search function)
        df['combined_search_field'] = df[brand_and_desc_col].fillna("").astype(str)
        
        # Ensure Brand & Description is available for search
        df['Brand & Description'] = df[brand_and_desc_col].fillna("").astype(str)
        
        # Assuming format is "Brand - Description" or just the description
        try:
            # Try to split by dash with brand before the dash
            df['brand_extracted'] = df[brand_and_desc_col].str.split('-', n=1).str[0].str.strip()
            df['description_extracted'] = df[brand_and_desc_col].str.split('-', n=1).str[1].str.strip()
            
            # If we have null values in description, it means there was no dash
            # In that case, use the whole field as description
            mask = df['description_extracted'].isna()
            df.loc[mask, 'description_extracted'] = df.loc[mask, brand_and_desc_col]
            df.loc[mask, 'brand_extracted'] = "Unknown"
            
            # Set our columns
            brand_col = 'brand_extracted'
            description_col = 'description_extracted'
        except:
            # If split fails, just use the whole column as description
            df['description_extracted'] = df[brand_and_desc_col]
            df['brand_extracted'] = "Unknown"
            brand_col = 'brand_extracted'
            description_col = 'description_extracted'
    
    # Check if we have product_name or description - we can work with either
    has_product_name = False
    if 'product_name' in df.columns and description_col is None:
        description_col = 'product_name'
        has_product_name = True

    # Handle missing brand by using a default value
    if brand_col is None and description_col is not None:
        df['brand'] = "Unknown"
        brand_col = 'brand'
    
    # Check if we have sufficient columns to work with
    missing_types = []
    if id_col is None:
        # If no ID column, we'll create one using row numbers
        df['product_id'] = [f"P{i+1:03d}" for i in range(len(df))]
        id_col = 'product_id'
    
    # Description is required - we can't reasonably create this
    if description_col is None:
        missing_types.append("description or product name")
    
    # Location is optional, we can use "Unknown" as default
    if location_col is None:
        df['location'] = "Unknown"
        location_col = 'location'
    
    # Expected count is required
    if count_col is None:
        missing_types.append("expected count or quantity")
        
    # Make sure we preserve the [E]Close SC column if it exists
    if close_sc_col is not None and close_sc_col != count_col:
        # Keep it for export later
        df['[E]Close SC_preserved'] = df[close_sc_col]
    
    if missing_types:
        return False, f"Required column types missing: {', '.join(missing_types)}. At minimum, please include columns for description/name and expected count."
    
    # Map the found columns to our expected column names
    df_mapped = df.copy()
    rename_dict = {
        id_col: 'product_id',
        location_col: 'location',
        count_col: 'expected_count'
    }
    
    if not has_product_name:
        rename_dict[description_col] = 'description'
        if brand_col != 'brand':  # Don't remap if we created it above
            rename_dict[brand_col] = 'brand'
    else:
        # If we're using product_name as description, no need to rename
        df_mapped['description'] = df_mapped[description_col]
        
    df_mapped.rename(columns=rename_dict, inplace=True)
    
    # Create product_name field by combining brand and description if needed
    if 'product_name' not in df_mapped.columns:
        df_mapped['product_name'] = df_mapped['brand'] + ' - ' + df_mapped['description']
    
    # Make sure we preserve the combined search field if it exists
    if 'combined_search_field' in df.columns:
        df_mapped['combined_search_field'] = df['combined_search_field']
        
    # Always create or preserve Brand & Description field for searching
    if 'Brand & Description' in df.columns:
        df_mapped['Brand & Description'] = df['Brand & Description']
    elif 'combined_search_field' in df_mapped.columns:
        df_mapped['Brand & Description'] = df_mapped['combined_search_field']
    else:
        # Create a combined field for display and search
        df_mapped['Brand & Description'] = df_mapped['brand'] + ' - ' + df_mapped['description']
    
    # Check data types
    try:
        # Handle PID and other non-numeric headers in the count column
        # First try to detect header or comment rows if they exist
        if count_col:
            # Check for standard header terms
            if str(df_mapped['expected_count'].iloc[0]).strip().upper() in ['PID', 'QTY', 'COUNT', 'QUANTITY']:
                st.info(f"Detected header row. Removing first row containing '{df_mapped['expected_count'].iloc[0]}'")
                df_mapped = df_mapped.iloc[1:].reset_index(drop=True)
            
            # Check for comment row containing "Do not delete or edit"
            comment_rows = []
            for i, val in enumerate(df_mapped['expected_count']):
                if isinstance(val, str) and "do not delete" in val.lower():
                    comment_rows.append(i)
                    st.info(f"Found comment row at index {i}: '{val}'")
            
            # Remove any detected comment rows
            if comment_rows:
                df_mapped = df_mapped.drop(comment_rows).reset_index(drop=True)
                st.success(f"Removed {len(comment_rows)} comment row(s) from the data")
        
        # Now handle any remaining non-numeric values in the expected_count
        try:
            # Convert expected_count to numeric
            df_mapped['expected_count'] = pd.to_numeric(df_mapped['expected_count'], errors='coerce')
            
            # Check if we have NaN values after conversion
            if df_mapped['expected_count'].isna().any():
                # If some values couldn't be converted, drop those rows
                na_count = df_mapped['expected_count'].isna().sum()
                st.warning(f"Removed {na_count} rows with non-numeric expected counts")
                df_mapped = df_mapped.dropna(subset=['expected_count']).reset_index(drop=True)
                
                # If we dropped all rows, that's an error
                if len(df_mapped) == 0:
                    return False, "No valid rows remaining after removing non-numeric count values."
        except Exception as e:
            return False, f"Error converting expected counts to numbers: {str(e)}"
            
        # Ensure product_id is unique
        if df_mapped['product_id'].duplicated().any():
            return False, "Duplicate product IDs found. Each product ID must be unique."
        
        return True, df_mapped
    except Exception as e:
        return False, f"Error validating data: {str(e)}"

# Function to add a count entry with historical tracking
def add_count_entry(product_id, count_value, count_location, count_note):
    # Initialize product in count_data if it doesn't exist
    if product_id not in st.session_state.count_data:
        st.session_state.count_data[product_id] = []
    
    # Initialize product in historical_counts if it doesn't exist
    if product_id not in st.session_state.historical_counts:
        st.session_state.historical_counts[product_id] = []
    
    # Add timestamp to count entry
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    session_id = st.session_state.current_count_session["id"]
    
    # Create the count entry
    count_entry = {
        'count': count_value,
        'location': count_location,
        'timestamp': timestamp,
        'session_id': session_id
    }
    
    # Store entry in current count data
    st.session_state.count_data[product_id].append(count_entry.copy())
    
    # Add to historical counts 
    st.session_state.historical_counts[product_id].append({
        'count': count_value,
        'location': count_location,
        'timestamp': timestamp,
        'session_id': session_id,
        'session_name': st.session_state.current_count_session["name"]
    })
    
    # Keep track of which products have been counted in this session
    product_info = None
    
    # Find the product details in the stock data
    if st.session_state.stock_data is not None:
        product_row = st.session_state.stock_data[st.session_state.stock_data['product_id'] == product_id]
        if not product_row.empty:
            product_info = {
                'product_id': product_id,
                'name': product_row['Brand & Description'].iloc[0],
                'expected_count': product_row['expected_count'].iloc[0] if 'expected_count' in product_row else None
            }
    
    # Add product to the current session's counted items if not already there
    session_exists = False
    for session in st.session_state.count_sessions:
        if session['id'] == session_id:
            session_exists = True
            if product_info and product_id not in [p['product_id'] for p in session.get('products', [])]:
                if 'products' not in session:
                    session['products'] = []
                session['products'].append(product_info)
            break
    
    # If this is a new session, add it to the list
    if not session_exists:
        new_session = st.session_state.current_count_session.copy()
        new_session['products'] = [product_info] if product_info else []
        st.session_state.count_sessions.append(new_session)

# Function to download data as CSV
def get_csv_download_link(df_or_csv, filename="stock_count_results.csv"):
    if isinstance(df_or_csv, str):
        # If a CSV string is passed directly
        csv_string = df_or_csv
    else:
        # If a dataframe is passed
        csv_string = df_or_csv.to_csv(index=False)
    
    b64 = base64.b64encode(csv_string.encode()).decode()
    
    # Create an iOS-style button for the download
    href = f'''
    <a href="data:file/csv;base64,{b64}" download="{filename}" 
       style="display: block; width: 100%; text-align: center; 
              background-color: #007AFF; color: white; 
              padding: 12px 20px; border-radius: 25px;
              font-weight: bold; text-decoration: none;
              box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
              transition: all 0.3s ease;"
       onmouseover="this.style.backgroundColor='#0062CC'; this.style.boxShadow='0 6px 12px rgba(0, 0, 0, 0.15)';"
       onmouseout="this.style.backgroundColor='#007AFF'; this.style.boxShadow='0 4px 8px rgba(0, 0, 0, 0.1)';"
    >
        📥 Export Stock Data
    </a>
    '''
    return href

# Function to prepare final data for export
def prepare_export_data(report_type="standard"):
    """
    Raw CSV manipulation to ensure [E]Close SC in row 2 of the CSV gets updated
    with count values without adding any extra columns.
    """
    if st.session_state.stock_data is None or 'raw_csv_content' not in st.session_state:
        st.error("No stock data available for export.")
        return None
    
    try:
        # Get the raw CSV content
        csv_content = st.session_state.raw_csv_content
        
        # Split into lines
        lines = csv_content.strip().split('\n')
        
        # We need at least 3 lines (header, [E]Close SC row, and data)
        if len(lines) < 3:
            st.error("CSV file doesn't have the expected format.")
            return None
        
        # Parse each row to find product_id and [E]Close SC positions
        reader = csv.reader(lines)
        rows = list(reader)
        
        if len(rows) < 3:
            st.error("CSV file doesn't have enough rows.")
            return None
        
        # First row is the header (row 0)
        header_row = rows[0]
        
        # Second row (row 1) should contain [E]Close SC
        eclose_row = rows[1]
        
        # Find the cell containing [E]Close SC in the second row
        eclose_col = -1
        for i, cell in enumerate(eclose_row):
            if '[E]Close SC' in cell:
                eclose_col = i
                break
        
        if eclose_col == -1:
            st.error("Cannot find [E]Close SC in row 2 of the CSV file.")
            return None
        
        # Find the product_id column index in our processed DataFrame
        product_id_col = -1
        for col in st.session_state.stock_data.columns:
            if col == 'product_id':
                # Find the original column index
                product_id_col = list(st.session_state.stock_data.columns).index(col)
                break
        
        if product_id_col == -1:
            st.error("Cannot find product_id column.")
            return None
        
        # Find the column index for the count column (794438) for reference
        count_col = -1
        for i, cell in enumerate(header_row):
            if '794438' in cell:
                count_col = i
                break
                
        if count_col == -1:
            st.warning("Cannot find 794438 column in the CSV header. Using the same column as [E]Close SC.")
            # Fall back to using the same column as [E]Close SC
            count_col = eclose_col
        
        # Create a mapping of product_id to count value
        product_counts = {}
        for product_id, counts in st.session_state.count_data.items():
            if counts:
                total_count = sum(entry['count'] for entry in counts)
                product_counts[product_id] = str(total_count)
        
        # Create a new list of rows for the output CSV
        new_rows = [rows[0]]  # Keep header row unchanged
        
        # Keep the original [E]Close SC row completely unchanged
        new_eclose_row = rows[1]  # Use the exact original row
        
        # Process all data rows (starting from row 3, index 2)
        data_rows = []
        for i in range(2, len(rows)):
            row = rows[i]
            
            if len(row) <= max(product_id_col, count_col, eclose_col):
                # Skip malformed rows
                data_rows.append(row)
                continue
            
            # Get the product ID from our mapping in the session state
            data_index = i - 2  # Adjust for 0-based indexing and 2 header rows
            if data_index < len(st.session_state.stock_data):
                try:
                    product_id = st.session_state.stock_data.iloc[data_index]['product_id']
                    
                    # Set count value in the 794438 column to ensure data consistency 
                    if product_id in product_counts:
                        row[count_col] = product_counts[product_id]
                    else:
                        # Set to 0 if not counted
                        row[count_col] = "0"
                except:
                    # If we can't get the product_id or other error, leave row unchanged
                    pass
            
            data_rows.append(row)
        
        # In each data row, we need to update the count in the [E]Close SC column
        
        # First, find the [E]Close SC column in the row 2 (so we know which column to update in the data)
        eclose_col = -1
        for idx, cell in enumerate(new_eclose_row):
            if '[E]Close SC' in str(cell):
                eclose_col = idx
                break
        
        if eclose_col == -1:
            st.warning("[E]Close SC column not found in row 2, looking in header row instead.")
            # Try to find it in the header row as a fallback
            for idx, cell in enumerate(header_row):
                if '[E]Close SC' in str(cell):
                    eclose_col = idx
                    break
        
        # Update the count values in the [E]Close SC column of the data rows
        if eclose_col != -1:
            # For each data row, update the [E]Close SC column with count values
            for i, row in enumerate(data_rows):
                # Get the product ID for this row
                if i < len(st.session_state.stock_data):
                    try:
                        # Get the product ID for this row
                        product_id = st.session_state.stock_data.iloc[i]['product_id']
                        
                        # Make sure the row has enough cells
                        while len(row) <= eclose_col:
                            row.append("")
                        
                        # Update the [E]Close SC column with the count value
                        if product_id in product_counts:
                            row[eclose_col] = product_counts[product_id]
                        else:
                            # Set to 0 if no count found
                            row[eclose_col] = "0"
                    except Exception as e:
                        st.error(f"Error updating row {i}: {str(e)}")
        else:
            st.error("Could not find [E]Close SC column in row 2 or header. Count values not updated.")
        
        # Keep the row 2 itself unchanged - this is important
        # We're only updating the data rows (rows 3+), not row 2
        
        # Add the updated [E]Close SC row
        new_rows.append(new_eclose_row)
        
        # Add all data rows
        new_rows.extend(data_rows)
        
        # Handle filtered report for counted items only
        if report_type == "counted":
            filtered_rows = [rows[0], new_eclose_row]  # Keep header rows with updated values
            
            for i, row in enumerate(data_rows):
                if i < len(st.session_state.stock_data):
                    try:
                        product_id = st.session_state.stock_data.iloc[i]['product_id']
                        if product_id in product_counts:
                            filtered_rows.append(row)
                    except:
                        pass
            
            # Convert back to CSV
            output = StringIO()
            writer = csv.writer(output)
            writer.writerows(filtered_rows)
            
            return output.getvalue()
        
        # Convert back to CSV
        output = StringIO()
        writer = csv.writer(output)
        writer.writerows(new_rows)
        
        return output.getvalue()
    
    except Exception as e:
        st.error(f"Error preparing export data: {str(e)}")
        # Fall back to the original data if there's an error
        return st.session_state.stock_data

# Function to switch from splash screen to main application
def switch_to_main():
    st.session_state.view = "main"
    st.rerun()

# Apply global centering CSS for all text content
st.markdown("""
<style>
.stApp {
    text-align: center;
}
.stTextInput, .stNumberInput, .stSelectbox, .stTextArea {
    text-align: center;
    margin-left: auto;
    margin-right: auto;
    max-width: 600px;
}
div.row-widget.stButton {
    text-align: center;
    display: flex;
    justify-content: center;
}
.css-6qob1r {
    text-align: center !important;
}
.css-10trblm {
    text-align: center !important;
}
p, h1, h2, h3, h4, h5, h6 {
    text-align: center !important;
}
.stMarkdown {
    text-align: center !important;
}
/* Dropdown style changes */
.stSelectbox > div > div {
    background-color: white !important;
    color: black !important;
}
/* Dropdown options */
.stSelectbox ul {
    background-color: white !important;
}
.stSelectbox ul li {
    color: black !important;
}
/* Dropdown arrow */
.stSelectbox svg {
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

# Check which view to display (splash screen or main app)
if st.session_state.view == "splash":
    # ===== SPLASH SCREEN =====
    # Add a small logo at the top right
    col_logo_left, col_logo_right = st.columns([4, 1])
    with col_logo_right:
        try:
            # Use the actual logo image
            logo_path = "attached_assets/arc-inspirations-squareLogo-1644849585224.png"
            st.image(logo_path, width=100)  # Smaller logo positioned at top right
        except:
            # If no logo is found, show a text header
            st.markdown('<p style="text-align: right; font-size: 1rem;">Arc Inspirations</p>', unsafe_allow_html=True)
    
    # Add some spacing after the logo
    st.markdown("<div style='padding: 2% 0;'></div>", unsafe_allow_html=True)
    
    # Main application header (centered)
    st.markdown("<h1 style='text-align: center;'>📦 Stock Count</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; margin-bottom: 3rem;'>Upload your stock list to begin counting</p>", unsafe_allow_html=True)
    
    # Center-aligned container for the uploader
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # File uploader
        uploaded_file = st.file_uploader("Upload Stock CSV File", type=["csv"], key="splash_uploader")
        
        if uploaded_file is not None:
            # Add a spinner while processing
            with st.spinner("Processing your file..."):
                try:
                    # Try to get a preview of the raw file content
                    uploaded_file.seek(0)  # Reset file pointer to beginning
                    raw_content = uploaded_file.read().decode('utf-8')
                    
                    # Store the raw CSV content for later export
                    st.session_state.raw_csv_content = raw_content
                    
                    first_few_lines = raw_content.split('\n')[:5]  # Get first 5 lines
                    
                    # Display raw content preview to help diagnose the issue
                    st.write("Raw CSV content (first 5 lines):")
                    for i, line in enumerate(first_few_lines):
                        st.write(f"Line {i+1}: {line}")
                    
                    # Reset file pointer to beginning
                    uploaded_file.seek(0)
                    
                    # Try multiple approaches to parse the CSV
                    try:
                        # First attempt: Try standard parsing
                        df = pd.read_csv(uploaded_file)
                        st.success("Loaded CSV file with standard headers")
                    except Exception as e1:
                        st.warning(f"Standard header load failed: {str(e1)}")
                        uploaded_file.seek(0)  # Reset file pointer
                        try:
                            # Second attempt: Try with header in row 2 and skip row 1
                            df = pd.read_csv(uploaded_file, header=1, skiprows=[2])  # Skip row 1 after headers (row index 2)
                            st.success("Loaded CSV file with headers in row 2 and skipped row 1")
                        except Exception as e2:
                            st.warning(f"Row 2 header load failed: {str(e2)}")
                            uploaded_file.seek(0)  # Reset file pointer
                            try:
                                # Third attempt: Try with no headers
                                df = pd.read_csv(uploaded_file, header=None)
                                # Generate default column names (Col0, Col1, etc.)
                                st.warning("Loaded CSV with no headers, using auto-generated column names")
                            except Exception as e3:
                                # Try different separators
                                uploaded_file.seek(0)
                                for separator in [',', ';', '\t', '|']:
                                    try:
                                        uploaded_file.seek(0)
                                        df = pd.read_csv(uploaded_file, sep=separator)
                                        st.success(f"Successfully loaded CSV with '{separator}' as separator")
                                        break
                                    except Exception as sep_error:
                                        pass
                                else:
                                    # Last attempt: Try with the most flexible parsing
                                    uploaded_file.seek(0)
                                    df = pd.read_csv(uploaded_file, sep=None, engine='python')
                                    st.warning("Used automatic delimiter detection to load CSV")
                    
                    # Show the detected columns
                    st.write("Detected columns:", df.columns.tolist())
                    
                    # Explicitly check for Brand & Description column
                    has_brand_desc = False
                    for col in df.columns:
                        if col == 'Brand & Description' or ('brand' in col.lower() and 'description' in col.lower()):
                            st.success(f"Found Brand & Description column: '{col}'")
                            has_brand_desc = True
                            break
                    
                    if not has_brand_desc:
                        st.warning("No 'Brand & Description' column found in headers. Attempting row 2 parsing...")
                        # Try to load looking specifically at row 2
                        try:
                            uploaded_file.seek(0)
                            # Read the first few rows to check manually
                            df_check = pd.read_csv(uploaded_file, nrows=3)
                            
                            # Check the second row (index 1) to see if it contains Brand & Description
                            if len(df_check) > 1:
                                row2 = df_check.iloc[1]
                                st.write("Row 2 contents:", row2.tolist())
                                
                                # Manually check if any cell in row 2 contains "Brand & Description"
                                found_brand_desc = False
                                for val in row2:
                                    if isinstance(val, str) and "brand" in val.lower() and "description" in val.lower():
                                        st.success(f"Row 2 contains Brand & Description: '{val}'")
                                        found_brand_desc = True
                                        break
                                
                                if not found_brand_desc:
                                    st.warning("No Brand & Description found in row 2 either")
                        except Exception as e:
                            st.error(f"Error checking row 2: {str(e)}")
                    
                    # Show a preview of the data
                    st.write("Preview of loaded data:")
                    st.dataframe(df.head(3))
                    
                    # Try automatic validation
                    valid, result = validate_csv(df)
                    
                    if valid:
                        st.session_state.stock_data = result
                        # Success message and switch to main app
                        st.success("✅ Stock data successfully loaded!")
                        st.session_state.view = "main"
                        st.rerun()
                    else:
                        st.error(f"Error in file: {result}")
                        
                        # Show expected format help
                        st.markdown("""
                        ### CSV File Requirements
                        
                        Your CSV file should include at minimum:
                        - A column for product descriptions (like "description", "product_name", "name", etc.)
                        - A column for expected quantities (like "expected_count", "quantity", "count", "stock", etc.)
                        
                        Optional but recommended columns:
                        - Product ID
                        - Brand 
                        - Location
                        
                        Example format:
                        """)
                        
                        # Show example format
                        example_df = pd.DataFrame({
                            'product_id': ['P001', 'P002'],
                            'brand': ['Brand A', 'Brand B'],
                            'description': ['Product Description 1', 'Product Description 2'],
                            'location': ['Bar 1', 'Store Room'],
                            'expected_count': [10, 5]
                        })
                        st.dataframe(example_df)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # Options below the file uploader
        st.markdown("<p style='text-align: center; margin-top: 3rem;'>Advanced Options</p>", unsafe_allow_html=True)
        
        # Two columns for the buttons
        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button("CSV Templates"):
                st.session_state.view = "main"  # Go to main app but in template mode
                st.rerun()
                
        with bc2:
            if st.button("Continue to App"):
                st.session_state.view = "main"
                st.rerun()
else:
    # ===== MAIN APPLICATION =====
    
    # Sidebar content
    with st.sidebar:
        st.markdown("### Stock Count Tool")
        
        # File uploader
        uploaded_file = st.file_uploader("Upload Stock CSV", type=["csv"])
        
        if uploaded_file is not None:
            try:
                # Try to get a preview of the raw file content
                uploaded_file.seek(0)  # Reset file pointer to beginning
                raw_content = uploaded_file.read().decode('utf-8')
                
                # Store the raw CSV content for later export
                st.session_state.raw_csv_content = raw_content
                
                first_few_lines = raw_content.split('\n')[:5]  # Get first 5 lines
                
                # Display raw content preview to help diagnose the issue
                st.write("Raw CSV content (first 5 lines):")
                for i, line in enumerate(first_few_lines):
                    st.write(f"Line {i+1}: {line}")
                
                # Reset file pointer to beginning
                uploaded_file.seek(0)
                
                # Try multiple approaches to parse the CSV
                try:
                    # First priority: Try with header in row 2 (which is index 1) and skip row 1
                    # This is the format the user indicated works for their CSV
                    df = pd.read_csv(uploaded_file, header=1, skiprows=[2])  # Skip row 1 after headers (row index 2)
                    st.success("Loaded CSV file with headers in row 2 and skipped row 1")
                except Exception as e1:
                    st.warning(f"Row 2 header load failed: {str(e1)}")
                    uploaded_file.seek(0)  # Reset file pointer
                    try:
                        # Second attempt: Try with standard headers
                        df = pd.read_csv(uploaded_file)
                        st.success("Loaded CSV file with standard headers")
                    except Exception as e2:
                        st.warning(f"Standard header load failed: {str(e2)}")
                        uploaded_file.seek(0)  # Reset file pointer
                        try:
                            # Third attempt: Try with no headers
                            df = pd.read_csv(uploaded_file, header=None)
                            # Generate default column names (Col0, Col1, etc.)
                            st.warning("Loaded CSV with no headers, using auto-generated column names")
                        except Exception as e3:
                            # Try different separators
                            uploaded_file.seek(0)
                            for separator in [',', ';', '\t', '|']:
                                try:
                                    uploaded_file.seek(0)
                                    df = pd.read_csv(uploaded_file, sep=separator)
                                    st.success(f"Successfully loaded CSV with '{separator}' as separator")
                                    break
                                except Exception as sep_error:
                                    pass
                            else:
                                # Last attempt: Try with the most flexible parsing
                                uploaded_file.seek(0)
                                df = pd.read_csv(uploaded_file, sep=None, engine='python')
                                st.warning("Used automatic delimiter detection to load CSV")
                
                # Show the detected columns
                st.write("Detected columns:", df.columns.tolist())
                
                # Show a preview of the data
                st.write("Preview of loaded data:")
                st.dataframe(df.head(3))
                
                # Validate the data and map columns
                valid, result = validate_csv(df)
                
                if valid:
                    st.session_state.stock_data = result
                    st.success("CSV data loaded successfully!")
                else:
                    st.error(result)  # Display error message
                    st.info("Make sure your CSV has description and quantity columns. See splash screen for examples.")
            except Exception as e:
                st.error(f"Error loading CSV: {str(e)}")
        
        # Count Sessions Management
        if st.session_state.stock_data is not None:
            st.subheader("Count Sessions")
            
            # Display current session info
            current_session = st.session_state.current_count_session
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                <h4 style="margin: 0; font-size: 16px; color: #6a28e8;">Current Session</h4>
                <p style="margin: 5px 0; font-size: 14px;">{current_session['name']}</p>
                <p style="margin: 0; font-size: 12px; color: #666;">Started: {current_session['timestamp'].strftime('%b %d, %Y %H:%M')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Option to create a new count session
            new_session_name = st.text_input(
                "New Session Name", 
                value=f"Count Session {datetime.now().strftime('%b %d, %Y %H:%M')}",
                key="new_session_name"
            )
            
            if st.button("➕ Start New Count Session", use_container_width=True):
                # Save the current session first if it's not already saved
                session_exists = False
                for session in st.session_state.count_sessions:
                    if session['id'] == current_session['id']:
                        session_exists = True
                        break
                        
                if not session_exists and len(st.session_state.count_data) > 0:
                    # Ensure we save the current session if it has counts
                    st.session_state.count_sessions.append(current_session.copy())
                    
                # Create a new session
                new_session = {
                    "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
                    "timestamp": datetime.now(),
                    "name": new_session_name,
                    "products": []
                }
                
                st.session_state.current_count_session = new_session
                st.success(f"Started new count session: {new_session_name}")
                st.rerun()
            
            # Show existing sessions if we have any
            if st.session_state.count_sessions:
                st.markdown("### Past Sessions")
                
                # Sort sessions by timestamp (newest first)
                sorted_sessions = sorted(
                    st.session_state.count_sessions,
                    key=lambda x: x.get('timestamp', datetime.now()),
                    reverse=True
                )
                
                # Display each session as a card
                for i, session in enumerate(sorted_sessions):
                    session_name = session.get('name', 'Unnamed Session')
                    session_time = session.get('timestamp', '').strftime('%b %d, %Y %H:%M') if isinstance(session.get('timestamp'), datetime) else 'Unknown date'
                    product_count = len(session.get('products', []))
                    
                    st.markdown(f"""
                    <div style="background-color: white; padding: 10px; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        <h4 style="margin: 0; font-size: 15px;">{session_name}</h4>
                        <p style="margin: 2px 0; font-size: 12px; color: #666;">{session_time}</p>
                        <p style="margin: 0; font-size: 12px;">Products: {product_count}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Add a separator before the export section
            st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
        
        # Export and Share section in sidebar
        if st.session_state.stock_data is not None:
            st.subheader("Export & Share")
            
            # Quick export button with purple gradient styling
            if st.button("📊 Export Inventory Report", use_container_width=True):
                export_data = prepare_export_data()
                if export_data is not None:
                    st.success("Report generated successfully!")
                    if isinstance(export_data, str):
                        # Already CSV content
                        csv_content = export_data
                    else:
                        # DataFrame
                        csv_content = export_data.to_csv(index=False)
                    # Base64 encode for download
                    b64 = base64.b64encode(csv_content.encode()).decode()
                    # Create download link with purple gradient style
                    href = f'''
                    <a href="data:file/csv;base64,{b64}" download="stock_count_report.csv" 
                       style="display: block; width: 100%; text-align: center; 
                              background: linear-gradient(135deg, #6a28e8 0%, #9161fd 100%); 
                              color: white; 
                              padding: 12px 20px; border-radius: 25px;
                              font-weight: bold; text-decoration: none;
                              box-shadow: 0 4px 8px rgba(106, 40, 232, 0.3);
                              transition: all 0.3s ease;">
                        📥 Export Stock Data
                    </a>
                    '''
                    st.markdown(href, unsafe_allow_html=True)
            
            # Add a small expander for advanced export options (hidden by default)
            with st.expander("Advanced Export Options", expanded=False):
                report_type = st.selectbox(
                    "Report Type",
                    options=["Standard Report", "Detailed Count Log", "Location Summary", "Compliance Report"],
                    index=0
                )
                
                report_type_map = {
                    "Standard Report": "standard",
                    "Detailed Count Log": "detailed", 
                    "Location Summary": "location_summary",
                    "Compliance Report": "compliance"
                }
                
                if st.button("Generate Custom Report"):
                    export_data = prepare_export_data(report_type=report_type_map[report_type])
                    
                    if export_data is not None:
                        filename = f"{report_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
                        st.success(f"{report_type} generated!")
                        
                        if isinstance(export_data, str):
                            # Already CSV content
                            csv_content = export_data
                        else:
                            # DataFrame
                            csv_content = export_data.to_csv(index=False)
                            
                        # Base64 encode for download
                        b64 = base64.b64encode(csv_content.encode()).decode()
                        # Create download link with purple gradient style
                        href = f'''
                        <a href="data:file/csv;base64,{b64}" download="{filename}" 
                           style="display: block; width: 100%; text-align: center; 
                                  background: linear-gradient(135deg, #6a28e8 0%, #9161fd 100%); 
                                  color: white; 
                                  padding: 12px 20px; border-radius: 25px;
                                  font-weight: bold; text-decoration: none;
                                  box-shadow: 0 4px 8px rgba(106, 40, 232, 0.3);
                                  transition: all 0.3s ease;">
                            📥 Download {filename}
                        </a>
                        '''
                        st.markdown(href, unsafe_allow_html=True)
    
    # Only show the logo without title
    col_header_right = st.columns([1])[0]
    with col_header_right:
        try:
            # Use the actual logo image
            logo_path = "attached_assets/arc-inspirations-squareLogo-1644849585224.png"
            # Add custom margins for better spacing with the search box
            st.markdown('<div style="margin-bottom:25px;"></div>', unsafe_allow_html=True)
            st.image(logo_path, width=90)  # Slightly smaller logo with better proportions
            # Add space below the logo
            st.markdown('<div style="margin-bottom:35px;"></div>', unsafe_allow_html=True)
        except:
            # If no logo is found, show nothing
            pass
    
    # Main content
    if st.session_state.stock_data is not None:
        # Search functionality with enhanced UI (no heading)
        
        # Create custom CSS for the enhanced search bar
        st.markdown(f"""
        <style>
        /* Enhanced search bar container */
        .search-container {{
            margin: 15px 0;
            position: relative;
        }}
        
        /* Search icon styling */
        .search-icon {{
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: #6a28e8;
            font-size: 20px;
            z-index: 1;
        }}
        
        /* Clear button styling */
        .clear-button {{
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            background: #f1f1f1;
            border: none;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            color: #666;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
            z-index: 1;
        }}
        
        .clear-button:hover {{
            background: #e1e1e1;
            color: #333;
        }}
        
        /* Override Streamlit's default input styling */
        .stTextInput input {{
            padding-left: 45px !important;
            padding-right: 45px !important;
            height: 50px !important;
            font-size: 16px !important;
            border-radius: 25px !important;
            border: 2px solid #e1e1e6 !important;
            transition: all 0.3s !important;
            background-color: white !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }}
        
        /* Fix width issues with search containers */
        /* Target all container elements and their children to force full width */
        [data-testid="stVerticalBlock"], 
        [data-testid="column"],
        .element-container,
        .stTextInput,
        div[data-baseweb="input"],
        div[data-baseweb="input"] > div,
        div.row-widget.stTextInput,
        section[data-testid="stCaptionContainer"],
        .stTextInput > div,
        .stTextInput > div > div,
        div[data-baseweb="base-input"] {{
            width: 100% !important;
            max-width: 100% !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
            margin-left: 0 !important;
            margin-right: 0 !important;
        }}
        
        /* Ensure the input spans full width with proper padding inside the text field */
        div[data-baseweb="input"] input {{
            width: 100% !important;
            box-sizing: border-box !important;
        }}
        
        /* Remove Streamlit's default padding for better mobile layout */
        .main .block-container,
        .stApp {{
            padding-left: 15px !important;
            padding-right: 15px !important;
            padding-top: 30px !important;
            max-width: 100% !important;
        }}
        
        /* Target Streamlit container elements to ensure full width */
        .row-widget.stTextInput > div,
        div[data-testid="stFormSubmitButton"] > button,
        [data-testid="stFormSubmitButton"] {{
            width: 100% !important;
            box-sizing: border-box !important;
        }}
        
        /* Fix specific layout for mobile display */
        @media screen and (max-width: 768px) {{
            .stTextInput input {{
                width: 100% !important;
                padding-left: 40px !important;
                padding-right: 20px !important;
            }}
        }}
        
        .stTextInput input:focus {{
            border-color: {THEME_PRIMARY} !important;
            box-shadow: 0 3px 10px rgba({THEME_PRIMARY.replace('#', '')}, 0.1) !important;
        }}
        
        /* Hide the help text icon */
        .stTextInput .stTooltipIcon {{
            color: {THEME_PRIMARY} !important;
        }}
        
        /* Loading indicator */
        .loading-indicator {{
            display: none;
            position: absolute;
            right: 50px;
            top: 50%;
            transform: translateY(-50%);
            width: 20px;
            height: 20px;
            border: 2px solid rgba({THEME_PRIMARY.replace('#', '')}, 0.2);
            border-radius: 50%;
            border-top-color: {THEME_PRIMARY};
            animation: spin 1s ease-in-out infinite;
            z-index: 1;
        }}
        
        @keyframes spin {{
            to {{ transform: translateY(-50%) rotate(360deg); }}
        }}
        
        /* Search results count badge */
        .search-results-count {{
            display: inline-block;
            background: {THEME_PRIMARY};
            color: white;
            font-size: 14px;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 20px;
            margin-left: 10px;
            box-shadow: 0 2px 5px rgba({THEME_PRIMARY.replace('#', '')}, 0.2);
        }}
        </style>
        
        <!-- Replaced with custom search box implementation above -->
        """, unsafe_allow_html=True)
        
        # Initialize a key for the clear button state if it doesn't exist
        if 'search_cleared' not in st.session_state:
            st.session_state.search_cleared = False
        
        # Initialize session state for recent searches if it doesn't exist
        if 'recent_searches' not in st.session_state:
            st.session_state.recent_searches = []
            
        # Determine the search value based on cleared state
        search_value = "" if st.session_state.search_cleared else st.session_state.current_search
        st.session_state.search_cleared = False  # Reset the cleared state
        
        # Create search box exactly matching the screenshot
        search_placeholder = "Search by brand, description, or product ID"
        
        # Add some space before the search box
        st.markdown('<div style="margin: 30px 0 20px 0;"></div>', unsafe_allow_html=True)
        
        # Create a search box that exactly matches the screenshot with purple border
        # Custom CSS for search box with explicit iOS styling
        st.markdown("""
        <style>
        /* Hide default input container styles */
        .stTextInput > div > div[data-testid="stFormSubmitButton"] { 
            display: none !important; 
        }
        
        /* Hide default input border & background */
        div[data-baseweb="base-input"] {
            border: none !important;
            background: transparent !important;
        }
        
        /* Style the input field exactly like iOS */
        div[data-baseweb="input"] {
            border-radius: 20px !important;
            border: 1px solid rgba(159, 121, 242, 0.3) !important;
            padding: 0 !important; 
            overflow: hidden !important;
            background: white !important;
        }
        
        /* Input element styling */
        .stTextInput input {
            border: none !important;
            padding: 10px 10px 10px 40px !important;
            background-color: transparent !important;
            font-size: 15px !important;
            color: #333 !important;
        }
        
        /* Input placeholder */
        .stTextInput input::placeholder {
            color: #999 !important;
            font-size: 15px !important;
        }
        
        /* Magnifying glass icon */
        .stTextInput {
            position: relative !important;
        }
        .stTextInput::before {
            content: "🔍";
            position: absolute;
            left: 15px;
            top: 11px;
            font-size: 15px;
            z-index: 10;
            color: #777;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Use the standard search input
        search_term = st.text_input(
            "Search",
            value=search_value,
            placeholder=search_placeholder,
            key="search_box",
            label_visibility="collapsed"
        )
        
        # Update session state with current search
        st.session_state.current_search = search_term
        
        # Display recent searches if we have any and no current search
        if 'recent_searches' in st.session_state and not search_term:
            # Create a container for recent searches with styled tags
            st.markdown(f"""
            <style>
            .recent-searches-container {{
                margin: 25px 0 15px 0;
                padding: 10px 0;
            }}
            .recent-searches-title {{
                font-size: 14px;
                color: #666;
                margin-bottom: 8px;
                font-weight: 500;
            }}
            .recent-search-pills {{
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-top: 8px;
            }}
            </style>
            <div class="recent-searches-container">
                <div class="recent-searches-title">Recent Searches:</div>
                <div class="recent-search-pills">
            """, unsafe_allow_html=True)
            
            # Create a container with stylish buttons for recent searches
            col1, col2, col3, col4 = st.columns(4)
            
            # Create the button columns
            col_list = [col1, col2, col3, col4]
            
            # Display recent searches as stylish pills/tags
            for i, recent_search in enumerate(st.session_state.recent_searches):
                with col_list[i % 4]:
                    # Create a stylish button with custom CSS
                    st.markdown(f"""
                    <style>
                    .recent-search-{i} {{
                        display: block;
                        width: 100%;
                        padding: 8px 12px;
                        background: rgba(106, 40, 232, 0.08);
                        color: #6a28e8;
                        border-radius: 20px;
                        border: 1px solid rgba(106, 40, 232, 0.2);
                        font-size: 14px;
                        font-weight: 500;
                        text-align: center;
                        margin-bottom: 8px;
                        transition: all 0.3s;
                        text-overflow: ellipsis;
                        overflow: hidden;
                        white-space: nowrap;
                        cursor: pointer;
                    }}
                    .recent-search-{i}:hover {{
                        background: rgba(106, 40, 232, 0.12);
                        box-shadow: 0 2px 5px rgba(106, 40, 232, 0.15);
                    }}
                    </style>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"{recent_search}", key=f"recent_{i}", use_container_width=True):
                        st.session_state.current_search = recent_search
                        st.rerun()
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        # If search is entered, filter data
        if search_term:
            # Create a lowercase version of search term
            search_lower = search_term.lower()
            
            # Enhanced search function with improved matching algorithms
            def search_all_columns(df, search_term):
                """
                Advanced search function that intelligently searches across all columns
                with smart matching and prioritization
                """
                # Convert search term to lowercase for case-insensitive search
                search_term = search_term.lower().strip()
                
                # Create a mask of all False initially
                mask = pd.Series([False] * len(df))
                
                # Dictionary to store matches with scores for better ranking
                # Higher score = better match (exact match > starts with > contains)
                match_scores = {}
                
                # Debug info
                column_list = df.columns.tolist()
                print(f"DEBUG: Available columns for search: {column_list}")
                
                # Break search term into words for multi-word searching
                search_words = search_term.split()
                
                # FIRST PRIORITY: Product ID (exact match)
                if 'product_id' in df.columns:
                    # Try to match product ID (including partial matches)
                    prod_ids = df['product_id'].fillna('').astype(str).str.lower()
                    for idx, value in prod_ids.items():
                        # Exact product ID match gets highest priority
                        if search_term == value:
                            match_scores[idx] = 100
                            mask.iloc[idx] = True
                            print(f"DEBUG: Found exact product ID match: {value}")
                        # Partial product ID match (starts with)
                        elif value.startswith(search_term):
                            match_scores[idx] = 90
                            mask.iloc[idx] = True
                            print(f"DEBUG: Found product ID starts with match: {value}")
                        # Partial product ID match (contains)
                        elif search_term in value:
                            match_scores[idx] = 80
                            mask.iloc[idx] = True
                            print(f"DEBUG: Found product ID contains match: {value}")
                
                # SECOND PRIORITY: Unnamed columns (main product information)
                unnamed_columns = [col for col in df.columns if 'Unnamed:' in col]
                for col in unnamed_columns:
                    if col in df.columns:
                        col_values = df[col].fillna('').astype(str).str.lower()
                        print(f"DEBUG: Searching in unnamed column '{col}'")
                        for idx, value in col_values.items():
                            if value.strip() == "":
                                continue
                                
                            # Check for exact match
                            if search_term == value.strip():
                                match_scores[idx] = match_scores.get(idx, 0) + 70
                                mask.iloc[idx] = True
                                print(f"DEBUG: Found exact match in {col}: '{value}'")
                            # Check for starts with
                            elif value.strip().startswith(search_term):
                                match_scores[idx] = match_scores.get(idx, 0) + 60
                                mask.iloc[idx] = True
                                print(f"DEBUG: Found starts with match in {col}: '{value}'")
                            # Check for contains
                            elif search_term in value.strip():
                                match_scores[idx] = match_scores.get(idx, 0) + 50
                                mask.iloc[idx] = True
                                print(f"DEBUG: Found contains match in {col}: '{value}'")
                            # Check for multi-word match (all words present)
                            elif len(search_words) > 1 and all(word in value for word in search_words):
                                match_scores[idx] = match_scores.get(idx, 0) + 45
                                mask.iloc[idx] = True
                                print(f"DEBUG: Found multi-word match in {col}: '{value}'")
                            # Check if any word matches (partial match)
                            elif any(word in value for word in search_words):
                                match_scores[idx] = match_scores.get(idx, 0) + 40
                                mask.iloc[idx] = True
                                print(f"DEBUG: Found partial word match in {col}: '{value}'")
                
                # THIRD PRIORITY: Product name/Brand and name combinations
                # Check 'Brand & Description' field
                if 'Brand & Description' in df.columns:
                    col_values = df['Brand & Description'].fillna('').astype(str).str.lower()
                    print(f"DEBUG: Searching in 'Brand & Description'")
                    for idx, value in col_values.items():
                        if search_term == value.strip():
                            match_scores[idx] = match_scores.get(idx, 0) + 35
                            mask.iloc[idx] = True
                        elif value.strip().startswith(search_term):
                            match_scores[idx] = match_scores.get(idx, 0) + 30
                            mask.iloc[idx] = True
                        elif search_term in value.strip():
                            match_scores[idx] = match_scores.get(idx, 0) + 25
                            mask.iloc[idx] = True
                        elif len(search_words) > 1 and all(word in value for word in search_words):
                            match_scores[idx] = match_scores.get(idx, 0) + 20
                            mask.iloc[idx] = True
                
                # FOURTH PRIORITY: Individual fields
                priority_fields = ['brand', 'description', 'product_name']
                for col in priority_fields:
                    if col in df.columns:
                        col_values = df[col].fillna('').astype(str).str.lower()
                        print(f"DEBUG: Searching in '{col}'")
                        for idx, value in col_values.items():
                            if search_term == value.strip():
                                match_scores[idx] = match_scores.get(idx, 0) + 15
                                mask.iloc[idx] = True
                            elif value.strip().startswith(search_term):
                                match_scores[idx] = match_scores.get(idx, 0) + 10
                                mask.iloc[idx] = True
                            elif search_term in value.strip():
                                match_scores[idx] = match_scores.get(idx, 0) + 5
                                mask.iloc[idx] = True
                
                # Add column for sorting by match score
                if mask.sum() > 0:
                    df_temp = df[mask].copy()
                    df_temp['match_score'] = pd.Series(match_scores)
                
                print(f"DEBUG: Found {mask.sum()} matches in total")
                return mask, match_scores
            
            # Perform the search with improved matching algorithm
            mask, match_scores = search_all_columns(st.session_state.stock_data, search_lower)
            
            # Debug info (commented out for production)
            # st.write(f"DEBUG: Found {mask.sum()} matches for '{search_term}' out of {len(st.session_state.stock_data)} items")
            
            # Filter data using the mask
            st.session_state.filtered_data = st.session_state.stock_data[mask].copy()
            
            # Apply match scores for better ordering
            if not st.session_state.filtered_data.empty:
                # Create a match_score column based on the scores
                st.session_state.filtered_data['match_score'] = st.session_state.filtered_data.index.map(
                    lambda idx: match_scores.get(idx, 0)
                )
                
                # Sort by match score (descending - highest scores first)
                st.session_state.filtered_data = st.session_state.filtered_data.sort_values(
                    'match_score', ascending=False
                ).drop(columns=['match_score'])
            
            # Store this search term in recent searches if it's not already there (regardless of results)
            if search_term and search_term not in st.session_state.recent_searches:
                st.session_state.recent_searches.insert(0, search_term)
                # Keep only the latest 10 searches as requested
                st.session_state.recent_searches = st.session_state.recent_searches[:10]
            
            # If there are no results, display a friendly "no results" screen
            if st.session_state.filtered_data.empty:
                st.markdown(f"""
                <div style="background-color: #f8f9fa; 
                           border-radius: 12px; 
                           padding: 30px; 
                           text-align: center;
                           margin: 20px 0;
                           box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                    <img src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f50d.svg" 
                         width="50" style="margin-bottom: 15px;">
                    <h3 style="margin-bottom: 10px; color: #333; font-size: 18px;">No Results Found</h3>
                    <p style="color: #666; margin-bottom: 20px;">
                        We couldn't find any products matching "<strong>{search_term}</strong>".
                    </p>
                    <p style="color: #777; font-size: 14px;">
                        Try checking the spelling or using different search terms.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Suggest some popular searches if we have recent searches
                if st.session_state.recent_searches:
                    st.markdown(f"""
                    <div style="margin-top: 20px; text-align: center;">
                        <p style="color: #666; font-size: 14px; margin-bottom: 10px;">
                            Try one of your recent searches:
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display a few recent searches as suggestions
                    col1, col2, col3 = st.columns(3)
                    cols = [col1, col2, col3]
                    
                    for i, recent_search in enumerate(st.session_state.recent_searches[:3]):
                        with cols[i]:
                            if st.button(f"{recent_search}", key=f"suggestion_{i}", use_container_width=True):
                                st.session_state.current_search = recent_search
                                st.rerun()
            
            # No additional sorting needed - already sorted by match scores
            
            # Display search results with an enhanced count badge
            if not st.session_state.filtered_data.empty:
                
                # Display the search results count with an attractive badge
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin: 15px 0;">
                    <h4 style="margin: 0; font-size: 18px; font-weight: 600;">Search Results</h4>
                    <div style="display: inline-block;
                        background: linear-gradient(135deg, #6a28e8 0%, #9161fd 100%);
                        color: white;
                        font-size: 14px;
                        font-weight: 600;
                        padding: 4px 12px;
                        border-radius: 20px;
                        margin-left: 10px;
                        box-shadow: 0 2px 5px rgba(106, 40, 232, 0.2);">
                        {len(st.session_state.filtered_data)} items
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # For each product in the filtered data, create an expander
                for idx, row in st.session_state.filtered_data.iterrows():
                    product_id = row['product_id']
                    
                    # From the debugging output, we now know the actual product information is in the unnamed columns
                    # For the sample product, we want to construct a name using "Madri Draught 1 Gallon"
                    
                    # Get all the non-empty unnamed values
                    unnamed_values = []
                    for col in row.index:
                        if 'Unnamed:' in col:
                            value = row[col]
                            if pd.notna(value) and str(value).strip() != "":
                                unnamed_values.append(str(value).strip())
                    
                    # Construct a product name from the unnamed values in a sensible order
                    # For the sample, we want "Madri Draught 1 Gallon [1]"
                    # So we need Unnamed 5, then 4, then 6
                    # Focus on these specific fields we know contain the product information
                    product_parts = []
                    
                    # Try to get the brand/name (Madri)
                    if 'Unnamed: 5' in row and pd.notna(row['Unnamed: 5']):
                        product_parts.append(str(row['Unnamed: 5']).strip())
                        
                    # Try to get the type (Draught)
                    if 'Unnamed: 4' in row and pd.notna(row['Unnamed: 4']):
                        product_parts.append(str(row['Unnamed: 4']).strip())
                        
                    # Try to get the size (1 Gallon [1])
                    if 'Unnamed: 6' in row and pd.notna(row['Unnamed: 6']):
                        product_parts.append(str(row['Unnamed: 6']).strip())
                    
                    # Combine all parts into a single product name
                    if product_parts:
                        product_name = " ".join(product_parts)
                    else:
                        # Fallback: Just combine all unnamed values
                        if unnamed_values:
                            product_name = " ".join(unnamed_values)
                        else:
                            product_name = f"Product {row['product_id']}"
                    
                    # Create the expander title with product name and ID
                    expander_title = f"{product_name} (ID: {row['product_id']})"
                    
                    # Create the expander with the product name
                    with st.expander(expander_title):
                        # Add enhanced iOS-style CSS for the count screen
                        st.markdown("""
                        <style>
                        .product-info-card {
                            background-color: white;
                            border-radius: 12px;
                            padding: 20px;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                            margin-bottom: 20px;
                            transition: all 0.3s ease;
                        }
                        .product-info-card:hover {
                            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                        }
                        .count-form-card {
                            background-color: white;
                            border-radius: 12px;
                            padding: 20px;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                            margin-bottom: 20px;
                            transition: all 0.3s ease;
                        }
                        .count-form-card:hover {
                            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                        }
                        
                        /* Styles for multiple metrics */
                        .summary-metrics {
                            display: flex;
                            justify-content: space-between;
                            background-color: white;
                            border-radius: 12px;
                            padding: 16px 24px;
                            margin: 20px 0;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                        }
                        .metric-item {
                            text-align: center;
                            padding: 8px;
                            flex: 1;
                            border-right: 1px solid #f0f0f0;
                        }
                        .metric-item:last-child {
                            border-right: none;
                        }
                        
                        /* Styles for single metric (when hiding expected and variance) */
                        .summary-metrics-single {
                            background-color: white;
                            border-radius: 12px;
                            padding: 16px 24px;
                            margin: 20px 0;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                            text-align: center;
                        }
                        .metric-item-single {
                            padding: 12px;
                        }
                        
                        /* Shared metric styles */
                        .metric-value {
                            font-size: 28px;
                            font-weight: 600;
                            color: #007AFF;
                            margin-bottom: 5px;
                        }
                        .metric-label {
                            font-size: 13px;
                            font-weight: 500;
                            color: #666;
                            text-transform: uppercase;
                            letter-spacing: 0.5px;
                        }
                        .variance-positive {
                            color: #34C759;
                        }
                        .variance-negative {
                            color: #FF3B30;
                        }
                        .count-table {
                            margin-top: 15px;
                            margin-bottom: 15px;
                            background-color: white;
                            border-radius: 12px;
                            padding: 5px;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                        }
                        
                        /* Input field styling for iOS look */
                        div[data-testid="stNumberInput"] label, div[data-testid="stSelectbox"] label {
                            font-weight: 500;
                            color: #444;
                            font-size: 14px;
                        }
                        div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] > div > div {
                            border-radius: 8px !important;
                            border: 1px solid #e0e0e0 !important;
                            padding: 8px 12px !important;
                        }
                        div[data-testid="stNumberInput"] input:focus, div[data-testid="stSelectbox"] > div > div:focus {
                            border-color: #007AFF !important;
                            box-shadow: 0 0 0 1px #007AFF !important;
                        }
                        
                        /* Expander styling */
                        section[data-testid="stExpander"] {
                            border-radius: 12px;
                            border: none !important;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                            margin-bottom: 20px;
                        }
                        section[data-testid="stExpander"] > div:first-child {
                            border-radius: 12px 12px 0 0 !important;
                            border: none !important;
                            padding: 1rem !important;
                            background-color: #f8f9fa !important;
                        }
                        section[data-testid="stExpander"] > div:first-child p {
                            font-weight: 600 !important;
                            color: #333 !important;
                        }
                        section[data-testid="stExpander"] > div:nth-child(2) {
                            border: none !important;
                            border-top: 1px solid #f0f0f0 !important;
                            border-radius: 0 0 12px 12px !important;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([1, 1])
                        
                        # Product information column - with card-like styling
                        with col1:
                            st.markdown('<div class="product-info-card">', unsafe_allow_html=True)
                            
                            # Add enhanced styling for the product details section
                            st.markdown(f"<h3 style='margin-top:0; color:#333; font-size:20px; font-weight:600;'>Product Details</h3>", unsafe_allow_html=True)
                            
                            # Product information with enhanced iOS-style design - removed expected count as requested
                            product_info = f"""
                            <style>
                            .product-detail-table {{
                                width: 100%;
                                border-collapse: separate;
                                border-spacing: 0;
                                border-radius: 12px;
                                overflow: hidden;
                                box-shadow: 0 2px 8px rgba({THEME_PRIMARY.replace('#', '')}, 0.08);
                                background: white;
                                margin-bottom: 15px;
                                border: 1px solid rgba({THEME_PRIMARY.replace('#', '')}, 0.1);
                            }}
                            .product-detail-table tr {{
                                transition: background-color 0.2s;
                            }}
                            .product-detail-table tr:nth-child(even) {{
                                background-color: rgba({THEME_PRIMARY.replace('#', '')}, 0.03);
                            }}
                            .product-detail-table td {{
                                padding: 12px 15px;
                                border-bottom: 1px solid rgba({THEME_PRIMARY.replace('#', '')}, 0.1);
                            }}
                            .product-detail-table tr:last-child td {{
                                border-bottom: none;
                            }}
                            .product-detail-label {{
                                color: {THEME_PRIMARY};
                                font-weight: 600;
                                font-size: 14px;
                                width: 35%;
                            }}
                            .product-detail-value {{
                                color: #333;
                                font-size: 15px;
                            }}
                            </style>
                            
                            <table class="product-detail-table">
                            <tr>
                              <td class="product-detail-label">ID:</td>
                              <td class="product-detail-value">{row['product_id']}</td>
                            </tr>
                            <tr>
                              <td class="product-detail-label">Name/Brand:</td>
                              <td class="product-detail-value">{row['Unnamed: 5'] if 'Unnamed: 5' in row and pd.notna(row['Unnamed: 5']) else ''}</td>
                            </tr>
                            <tr>
                              <td class="product-detail-label">Type:</td>
                              <td class="product-detail-value">{row['Unnamed: 4'] if 'Unnamed: 4' in row and pd.notna(row['Unnamed: 4']) else ''}</td>
                            </tr>
                            <tr>
                              <td class="product-detail-label">Size/Details:</td>
                              <td class="product-detail-value">{row['Unnamed: 6'] if 'Unnamed: 6' in row and pd.notna(row['Unnamed: 6']) else ''}</td>
                            </tr>
                            <tr>
                              <td class="product-detail-value" colspan="2" style="font-weight: normal; display: {'none' if row['Unnamed: 7'] == '65' or not pd.notna(row['Unnamed: 7']) else 'table-cell'};">{row['Unnamed: 7'] if 'Unnamed: 7' in row and pd.notna(row['Unnamed: 7']) else ''}</td>
                            </tr>
                            <tr>
                              <td class="product-detail-value" colspan="2" style="font-weight: normal; display: {'none' if row['location'] == 'Unknown' or not pd.notna(row['location']) else 'table-cell'};">{row['location'] if 'location' in row and pd.notna(row['location']) else ''}</td>
                            </tr>
                            </table>
                            """
                                
                            # Close the table
                            product_info += "</table>"
                            
                            st.markdown(product_info, unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Count entry form - with card-like styling
                        with col2:
                            # Add custom CSS for number input styling
                            st.markdown(f"""
                            <style>
                            /* iOS-style number input styling */
                            div[data-testid="stNumberInput"] > div > div > div > input {{
                                border-radius: 10px !important;
                                border: 1px solid rgba({THEME_PRIMARY.replace('#', '')}, 0.2) !important;
                                padding: 10px 8px !important;
                                box-shadow: 0 2px 5px rgba({THEME_PRIMARY.replace('#', '')}, 0.05) !important;
                                font-size: 16px !important;
                                transition: all 0.2s ease;
                            }}
                            
                            div[data-testid="stNumberInput"] > div > div > div > input:focus {{
                                border: 1px solid {THEME_PRIMARY} !important;
                                box-shadow: 0 0 0 2px rgba({THEME_PRIMARY.replace('#', '')}, 0.1) !important;
                            }}
                            
                            /* Create nice count entry card with gradient border */
                            .count-form-card {{
                                border-radius: 16px;
                                padding: 20px;
                                margin-bottom: 20px;
                                box-shadow: 0 4px 12px rgba({THEME_PRIMARY.replace('#', '')}, 0.08);
                                background: white;
                                border: 1px solid rgba({THEME_PRIMARY.replace('#', '')}, 0.15);
                                background: linear-gradient(to bottom, white, rgba({THEME_PRIMARY.replace('#', '')}, 0.02));
                            }}
                            </style>
                            """, unsafe_allow_html=True)
                            
                            st.markdown('<div class="count-form-card">', unsafe_allow_html=True)
                            st.markdown(f"<h3 style='margin-top:0; color:{THEME_PRIMARY}; font-size:20px; font-weight:600;'>Add Count Entry</h3>", unsafe_allow_html=True)
                            
                            # Custom CSS for bigger number input
                            st.markdown(f"""
                            <style>
                            /* Make number input field larger and more prominent */
                            div[data-testid="stNumberInput"] {{
                                margin-bottom: 15px;
                            }}
                            div[data-testid="stNumberInput"] > div > div > input {{
                                border-radius: 12px !important;
                                border: 2px solid {THEME_PRIMARY} !important;
                                padding: 15px 20px !important;
                                box-shadow: 0 3px 10px rgba(0,0,0,0.08) !important;
                                font-size: 24px !important;
                                font-weight: 500 !important;
                                background-color: white !important;
                                height: 60px !important;
                                transition: all 0.2s ease !important;
                            }}
                            div[data-testid="stNumberInput"] > div > div > input:focus {{
                                border: 2px solid {THEME_PRIMARY} !important;
                                box-shadow: 0 3px 12px rgba({THEME_PRIMARY.replace('#', '')}, 0.3) !important;
                            }}
                            /* Style help text */
                            div[data-testid="stNumberInput"] .stTooltipIcon {{
                                color: {THEME_PRIMARY} !important;
                            }}
                            </style>
                            """, unsafe_allow_html=True)
                            
                            # Create a more attractive form layout with bigger input
                            count_value = st.number_input(
                                "Count Value", 
                                min_value=0.0, 
                                step=0.1, 
                                format="%.1f", 
                                key=f"count_{product_id}",
                                help="Enter the count value with decimal precision if needed"
                            )
                            
                            # Location selection using buttons
                            st.markdown("<p style='margin-bottom:8px; font-weight:500; color:#444; font-size:14px;'>Location</p>", unsafe_allow_html=True)
                            
                            # Define location options
                            location_options = ["Bar 1", "Bar 2", "Store Room 1", "Store Room 2", "Cellar"]
                            
                            # Try to set default based on product location if it matches one of our options
                            product_location = row['location']
                            default_location = location_options[0]  # Default to first option
                            for option in location_options:
                                if option.lower() == product_location.lower():
                                    default_location = option
                                    break
                            
                            # Create session state for storing selected location if it doesn't exist
                            if f"selected_loc_{product_id}" not in st.session_state:
                                st.session_state[f"selected_loc_{product_id}"] = default_location
                            
                            # Add custom CSS for iOS-style location buttons
                            st.markdown("""
                            <style>
                            /* iOS-style location buttons */
                            .location-buttons div[data-testid="stHorizontalBlock"] {
                                gap: 8px;
                                margin-bottom: 8px;
                            }
                            
                            /* All location buttons base style */
                            .location-buttons div[data-testid="stButton"] button {
                                border-radius: 10px;
                                font-size: 13px;
                                font-weight: 500;
                                padding: 8px 0;
                                width: 100%;
                                transition: all 0.2s;
                                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                                border: 1px solid #e4e4e4;
                                background-color: #f5f5f7;
                                color: #333;
                            }
                            
                            /* Hover effect for all buttons */
                            .location-buttons div[data-testid="stButton"] button:hover {
                                transform: translateY(-1px);
                                box-shadow: 0 3px 8px rgba(0,0,0,0.1);
                                filter: brightness(1.05);
                            }
                            
                            /* Selected location highlight with purple theme */
                            .location-selected {
                                font-size: 14px;
                                color: {THEME_PRIMARY};
                                margin: 12px 0 15px 0;
                                text-align: center;
                                padding: 10px;
                                border-radius: 10px;
                                background-color: rgba({THEME_PRIMARY.replace('#', '')}, 0.08);
                                border: 1px solid rgba({THEME_PRIMARY.replace('#', '')}, 0.2);
                                font-weight: 500;
                            }
                            </style>
                            """, unsafe_allow_html=True)
                            
                            # Create a div to contain all location buttons for styling
                            st.markdown('<div class="location-buttons">', unsafe_allow_html=True)
                            
                            # Create layout for location buttons
                            col1, col2 = st.columns(2)
                            
                            # First row of buttons
                            with col1:
                                if st.button("Bar 1", key=f"loc1_{product_id}", 
                                            use_container_width=True,
                                            help="Select Bar 1 as location"):
                                    st.session_state[f"selected_loc_{product_id}"] = "Bar 1"
                                    st.rerun()
                            
                            with col2:
                                if st.button("Bar 2", key=f"loc2_{product_id}", 
                                            use_container_width=True,
                                            help="Select Bar 2 as location"):
                                    st.session_state[f"selected_loc_{product_id}"] = "Bar 2"
                                    st.rerun()
                            
                            # Second row of buttons
                            col3, col4 = st.columns(2)
                            with col3:
                                if st.button("Store Room 1", key=f"loc3_{product_id}", 
                                            use_container_width=True,
                                            help="Select Store Room 1 as location"):
                                    st.session_state[f"selected_loc_{product_id}"] = "Store Room 1"
                                    st.rerun()
                            
                            with col4:
                                if st.button("Store Room 2", key=f"loc4_{product_id}", 
                                            use_container_width=True,
                                            help="Select Store Room 2 as location"):
                                    st.session_state[f"selected_loc_{product_id}"] = "Store Room 2"
                                    st.rerun()
                            
                            # Third row with Cellar 
                            if st.button("Cellar", key=f"loc5_{product_id}", 
                                        use_container_width=True,
                                        help="Select Cellar as location"):
                                st.session_state[f"selected_loc_{product_id}"] = "Cellar"
                                st.rerun()
                            
                            # Get the selected location
                            count_location = st.session_state[f"selected_loc_{product_id}"]
                            
                            # Display the selected location with styling
                            st.markdown(f'<div class="location-selected"><strong>📍 {count_location}</strong></div>', unsafe_allow_html=True)
                            
                            # Dynamic styling for active buttons using custom CSS classes with purple theme
                            active_style = f"""
                            <style>
                            /* Style for the selected button - applied dynamically */
                            [data-testid="stButton"] button[kind="secondary"] {{
                                background: {THEME_GRADIENT} !important;
                                color: white !important;
                                font-weight: 500 !important;
                                border: none !important;
                                box-shadow: 0 2px 5px rgba({THEME_PRIMARY.replace('#', '')}, 0.3) !important;
                            }}
                            </style>
                            """
                            
                            # Apply active styling to the selected location's button
                            if count_location == "Bar 1":
                                st.markdown(active_style.replace('button[kind="secondary"]', f'button[aria-label="Select Bar 1 as location"]'), unsafe_allow_html=True)
                            elif count_location == "Bar 2":
                                st.markdown(active_style.replace('button[kind="secondary"]', f'button[aria-label="Select Bar 2 as location"]'), unsafe_allow_html=True)
                            elif count_location == "Store Room 1":
                                st.markdown(active_style.replace('button[kind="secondary"]', f'button[aria-label="Select Store Room 1 as location"]'), unsafe_allow_html=True)
                            elif count_location == "Store Room 2":
                                st.markdown(active_style.replace('button[kind="secondary"]', f'button[aria-label="Select Store Room 2 as location"]'), unsafe_allow_html=True)
                            elif count_location == "Cellar":
                                st.markdown(active_style.replace('button[kind="secondary"]', f'button[aria-label="Select Cellar as location"]'), unsafe_allow_html=True)
                            
                            # Close the location-buttons div
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Add custom CSS for a more prominent Add Count Entry button
                            st.markdown(f"""
                            <style>
                            /* Style for the Add Count Entry button */
                            div[data-testid="stButton"] button:has(div:contains("Add Count Entry")) {{
                                background: {THEME_GRADIENT} !important;
                                color: white !important;
                                padding: 15px !important;
                                font-size: 16px !important;
                                font-weight: 600 !important;
                                border-radius: 12px !important;
                                border: none !important;
                                box-shadow: 0 4px 12px rgba({THEME_PRIMARY.replace('#', '')}, 0.25) !important;
                                margin-top: 5px !important;
                                height: auto !important;
                                transition: all 0.3s ease !important;
                            }}
                            
                            div[data-testid="stButton"] button:has(div:contains("Add Count Entry")):hover {{
                                transform: translateY(-2px) !important;
                                box-shadow: 0 6px 15px rgba({THEME_PRIMARY.replace('#', '')}, 0.3) !important;
                            }}
                            </style>
                            """, unsafe_allow_html=True)
                            
                            # iOS-style add count button
                            add_count_button = st.button(
                                "➕ Add Count Entry", 
                                key=f"btn_{product_id}",
                                use_container_width=True
                            )
                            
                            if add_count_button:
                                if count_value >= 0:
                                    # Pass empty string for notes
                                    add_count_entry(product_id, count_value, count_location, "")
                                    st.success("Count entry added successfully!")
                                    st.rerun()
                                else:
                                    st.error("Count value must be non-negative.")
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Display existing count entries
                        if product_id in st.session_state.count_data and st.session_state.count_data[product_id]:
                            # Calculate totals first for the summary metrics
                            total_count = sum(entry['count'] for entry in st.session_state.count_data[product_id])
                            expected = row['expected_count'] if pd.notna(row['expected_count']) else 0
                            variance = total_count - expected
                            
                            # Add summary metrics as an attractive bar
                            variance_class = "variance-positive" if variance >= 0 else "variance-negative"
                            variance_symbol = "+" if variance >= 0 else ""
                            
                            # Add metric styling
                            st.markdown(f"""
                            <style>
                            .summary-metrics-single {{
                                background: #f7f7f9;
                                color: #333;
                                border-radius: 12px;
                                padding: 15px 20px;
                                text-align: center;
                                margin: 15px 0;
                                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
                                border: 1px solid #e9e9ec;
                            }}
                            .metric-item-single {{
                                text-align: center;
                            }}
                            .metric-value {{
                                font-size: 36px;
                                font-weight: 700;
                                margin-bottom: 5px;
                                color: #333;
                            }}
                            .metric-label {{
                                font-size: 14px;
                                font-weight: 500;
                                letter-spacing: 1px;
                                color: #666;
                            }}
                            
                            /* Count history table styling */
                            .count-table {{
                                border-radius: 12px;
                                overflow: hidden;
                                box-shadow: 0 4px 12px rgba({THEME_PRIMARY.replace('#', '')}, 0.08);
                                margin-top: 15px;
                                margin-bottom: 20px;
                                border: 1px solid rgba({THEME_PRIMARY.replace('#', '')}, 0.1);
                            }}
                            div[data-testid="stDataFrame"] > div > div > div {{
                                border-radius: 12px !important;
                            }}
                            </style>
                            """, unsafe_allow_html=True)
                            
                            # Only show total count, hiding expected count and variance as requested
                            metrics_html = f"""
                            <div class="summary-metrics-single">
                                <div class="metric-item-single">
                                    <div class="metric-value">{total_count:.1f}</div>
                                    <div class="metric-label">TOTAL COUNTED</div>
                                </div>
                            </div>
                            """
                            
                            st.markdown(metrics_html, unsafe_allow_html=True)
                            
                            # Show entries table with enhanced styling
                            st.markdown(f"<h3 style='margin-top:20px; font-size:20px; font-weight:600; color:{THEME_PRIMARY};'>Count History</h3>", unsafe_allow_html=True)
                            
                            # Prepare the dataframe
                            counts_df = pd.DataFrame(st.session_state.count_data[product_id])
                            
                            # Format the timestamp column to be more readable
                            if 'timestamp' in counts_df.columns:
                                counts_df['timestamp'] = pd.to_datetime(counts_df['timestamp']).dt.strftime('%d-%b %H:%M')
                            
                            # Rename columns for better display
                            counts_df = counts_df.rename(columns={
                                'count': 'Count', 
                                'location': 'Location', 
                                'timestamp': 'Date/Time',
                                'session_id': 'Session'
                            })
                            
                            # Hide session_id if present in the display
                            display_columns = [col for col in counts_df.columns if col != 'Session']
                            
                            # Display the styled dataframe
                            st.markdown('<div class="count-table">', unsafe_allow_html=True)
                            st.dataframe(counts_df[display_columns], use_container_width=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Check if we have historical data for comparison
                            if product_id in st.session_state.historical_counts and len(st.session_state.historical_counts[product_id]) > 1:
                                # Add section for historical comparison
                                st.markdown("### 📊 Historical Count Comparison", unsafe_allow_html=True)
                                
                                st.markdown("""
                                <style>
                                .comparison-header {
                                    font-size: 18px;
                                    font-weight: 600;
                                    color: #6a28e8;
                                    margin: 15px 0 10px 0;
                                    text-align: left;
                                }
                                .history-table {
                                    margin-top: 5px;
                                    margin-bottom: 15px;
                                    background-color: white;
                                    border-radius: 12px;
                                    padding: 5px;
                                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                                }
                                .history-metrics {
                                    display: flex;
                                    justify-content: space-between;
                                    background-color: white;
                                    border-radius: 12px;
                                    padding: 15px;
                                    margin: 10px 0;
                                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                                }
                                .history-metric {
                                    text-align: center;
                                    flex: 1;
                                }
                                .history-metric-value {
                                    font-size: 20px;
                                    font-weight: 600;
                                    color: #6a28e8;
                                    margin-bottom: 5px;
                                }
                                .history-metric-label {
                                    font-size: 12px;
                                    color: #666;
                                    text-transform: uppercase;
                                }
                                .trend-up {
                                    color: #34C759;
                                }
                                .trend-down {
                                    color: #FF3B30;
                                }
                                .trend-stable {
                                    color: #007AFF;
                                }
                                </style>
                                """, unsafe_allow_html=True)
                                
                                # Group data by session
                                historical_data = st.session_state.historical_counts[product_id]
                                session_groups = {}
                                
                                for entry in historical_data:
                                    session_id = entry.get('session_id', 'unknown')
                                    session_name = entry.get('session_name', f"Session {session_id}")
                                    
                                    if session_id not in session_groups:
                                        session_groups[session_id] = {
                                            'name': session_name,
                                            'entries': [],
                                            'timestamp': entry.get('timestamp', '')
                                        }
                                    
                                    session_groups[session_id]['entries'].append(entry)
                                
                                # Calculate totals by session
                                session_totals = {}
                                for session_id, data in session_groups.items():
                                    total = sum(entry['count'] for entry in data['entries'])
                                    session_totals[session_id] = {
                                        'name': data['name'],
                                        'total': total,
                                        'timestamp': data['timestamp'],
                                        'count': len(data['entries'])
                                    }
                                
                                # Get sessions ordered by timestamp
                                sorted_sessions = sorted(
                                    [(sid, data) for sid, data in session_totals.items()],
                                    key=lambda x: x[1]['timestamp'],
                                    reverse=True
                                )
                                
                                # Show comparison metrics if we have at least 2 sessions
                                if len(sorted_sessions) >= 2:
                                    current_session = sorted_sessions[0][1]
                                    previous_session = sorted_sessions[1][1]
                                    
                                    current_total = current_session['total']
                                    previous_total = previous_session['total']
                                    
                                    # Calculate change
                                    change = current_total - previous_total
                                    percent_change = 0
                                    if previous_total > 0:
                                        percent_change = (change / previous_total) * 100
                                    
                                    # Determine trend
                                    if abs(change) < 0.001:  # Nearly equal
                                        trend_class = "trend-stable"
                                        trend_symbol = "◼"
                                        trend_text = "No Change"
                                    elif change > 0:
                                        trend_class = "trend-up"
                                        trend_symbol = "▲"
                                        trend_text = "Increase"
                                    else:
                                        trend_class = "trend-down"
                                        trend_symbol = "▼"
                                        trend_text = "Decrease"
                                    
                                    # Display comparison metrics
                                    st.markdown(f'<div class="comparison-header">Comparison: {current_session["name"]} vs {previous_session["name"]}</div>', unsafe_allow_html=True)
                                    
                                    metrics_html = f"""
                                    <div class="history-metrics">
                                        <div class="history-metric">
                                            <div class="history-metric-value">{current_total:.1f}</div>
                                            <div class="history-metric-label">CURRENT COUNT</div>
                                        </div>
                                        <div class="history-metric">
                                            <div class="history-metric-value">{previous_total:.1f}</div>
                                            <div class="history-metric-label">PREVIOUS COUNT</div>
                                        </div>
                                        <div class="history-metric">
                                            <div class="history-metric-value {trend_class}">{trend_symbol} {abs(change):.1f}</div>
                                            <div class="history-metric-label">{trend_text}</div>
                                        </div>
                                        <div class="history-metric">
                                            <div class="history-metric-value {trend_class}">{percent_change:.1f}%</div>
                                            <div class="history-metric-label">% CHANGE</div>
                                        </div>
                                    </div>
                                    """
                                    st.markdown(metrics_html, unsafe_allow_html=True)
                                
                                # Show table of session data
                                st.markdown('<div class="comparison-header">All Count Sessions</div>', unsafe_allow_html=True)
                                
                                # Create a DataFrame from session totals
                                sessions_df = pd.DataFrame([
                                    {
                                        'Session': data['name'], 
                                        'Total Count': data['total'],
                                        'Count Entries': data['count'],
                                        'Date/Time': data['timestamp']
                                    } 
                                    for _, data in sorted_sessions
                                ])
                                
                                # Display sessions table
                                st.markdown('<div class="history-table">', unsafe_allow_html=True)
                                st.dataframe(sessions_df, use_container_width=True)
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Add "Count Complete" button with purple gradient styling
                            sc_closed = product_id in st.session_state.sc_closed and st.session_state.sc_closed[product_id]
                            
                            # Show current status
                            if sc_closed:
                                status_color = "#34C759"  # Green for complete
                                status_text = "✓ Count is marked as Complete"
                            else:
                                status_color = "#FF9500"  # Orange for not complete
                                status_text = "⚠️ Count is not marked as Complete"
                                
                            st.markdown(f"""
                            <div style="background-color: white; 
                                        border-radius: 12px; 
                                        padding: 15px; 
                                        margin-top: 20px;
                                        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                                        border-left: 4px solid {status_color};">
                                <p style="margin: 0; color: {status_color}; font-weight: 500;">{status_text}</p>
                                <p style="margin: 5px 0 0 0; font-size: 12px; color: #666;">
                                    Marking as complete will update [E]Close SC in the export
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Button to toggle completion status
                            btn_label = "✓ Count Complete" if not sc_closed else "↺ Mark as Incomplete"
                            btn_help = "Click to mark this count as complete" if not sc_closed else "Click to mark this count as incomplete"
                            
                            # Create a column layout to center the button
                            col1, col2, col3 = st.columns([1.5, 2, 1.5])
                            with col2:
                                # Custom button with centered style
                                st.markdown(
                                    f"""
                                    <style>
                                    div[data-testid="stButton"] {{
                                        text-align: center;
                                        display: flex;
                                        justify-content: center;
                                    }}
                                    </style>
                                    """,
                                    unsafe_allow_html=True
                                )
                                complete_button = st.button(
                                    btn_label,
                                    key=f"complete_btn_{product_id}",
                                    help=btn_help,
                                    use_container_width=True,
                                    type="primary" if not sc_closed else "secondary"
                                )
                            
                            # If complete button clicked
                            if complete_button:
                                # Toggle the state
                                if not sc_closed:
                                    # Mark as complete
                                    st.session_state.sc_closed[product_id] = True
                                    st.success("Stock count marked as complete!")
                                    # Clear search to return to main page
                                    st.session_state.current_search = ""
                                    st.rerun()
                                else:
                                    # Mark as incomplete
                                    st.session_state.sc_closed[product_id] = False
                                    st.info("Stock count marked as incomplete.")
                                    st.rerun()
                        else:
                            # Enhanced empty state with iOS-style 
                            st.markdown("""
                            <style>
                            .ios-empty-state {
                                background-color: white;
                                border-radius: 12px;
                                padding: 25px 20px;
                                text-align: center;
                                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                                margin: 20px 0;
                            }
                            .ios-empty-icon {
                                font-size: 32px;
                                margin-bottom: 15px;
                            }
                            .ios-empty-title {
                                font-size: 16px;
                                font-weight: 600;
                                color: #333;
                                margin-bottom: 8px;
                            }
                            .ios-empty-message {
                                font-size: 14px;
                                color: #666;
                                line-height: 1.4;
                            }
                            </style>
                            <div class="ios-empty-state">
                                <div class="ios-empty-icon">📋</div>
                                <div class="ios-empty-title">No Count Entries</div>
                                <div class="ios-empty-message">Use the form above to add your first count for this product.</div>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                # Enhanced "No products found" message with iOS styling
                st.markdown("""
                <style>
                .ios-search-empty {
                    background-color: white;
                    border-radius: 12px;
                    padding: 30px 20px;
                    text-align: center;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                    margin: 30px 0;
                }
                .ios-search-icon {
                    font-size: 36px;
                    margin-bottom: 15px;
                }
                .ios-search-title {
                    font-size: 18px;
                    font-weight: 600;
                    color: #333;
                    margin-bottom: 10px;
                }
                .ios-search-message {
                    font-size: 15px;
                    color: #666;
                    line-height: 1.5;
                    max-width: 400px;
                    margin: 0 auto;
                }
                </style>
                <div class="ios-search-empty">
                    <div class="ios-search-icon">🔍</div>
                    <div class="ios-search-title">No Products Found</div>
                    <div class="ios-search-message">
                        We couldn't find any products matching your search terms. 
                        Try a different keyword, brand name, or product ID.
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Enhanced search prompt with iOS-style design
            st.markdown("""
            <style>
            .ios-search-prompt {
                background-color: white;
                border-radius: 12px;
                padding: 35px 20px;
                text-align: center;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                margin: 30px 0;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
            }
            .ios-prompt-icon {
                font-size: 42px;
                margin-bottom: 20px;
            }
            .ios-prompt-title {
                font-size: 22px;
                font-weight: 600;
                color: #333;
                margin-bottom: 15px;
            }
            .ios-prompt-message {
                font-size: 16px;
                color: #666;
                line-height: 1.5;
                max-width: 450px;
                margin: 0 auto;
            }
            .ios-prompt-hint {
                margin-top: 20px;
                font-size: 14px;
                color: #888;
                font-style: italic;
            }
            </style>
            <div class="ios-search-prompt">
                <div class="ios-prompt-icon">🔍</div>
                <div class="ios-prompt-title">Find Products to Count</div>
                <div class="ios-prompt-message">
                    Use the search bar above to find products by name, brand, ID or description.
                </div>
                <div class="ios-prompt-hint">
                    Pro Tip: You can use partial words - try "beer", "wine", or a specific brand name.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add a modern export section at the bottom of the main UI with iOS styling
            st.markdown("""
            <div style="margin: 40px auto 30px auto; max-width: 800px;">
                <h3 style="text-align: center; font-size: 28px; font-weight: 600; color: #333; margin-bottom: 15px;">Export Inventory Reports</h3>
                <p style="text-align: center; color: #666; margin-bottom: 25px; font-size: 16px; line-height: 1.5;">
                    Generate inventory reports with a single click. Download and share with your team.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Add iOS-style buttons with custom CSS using theme colors
            st.markdown(f"""
            <style>
                /* iOS style button for Generate Report */
                div.stButton > button {{
                    background-color: {THEME_PRIMARY}; /* Primary purple theme */
                    color: white !important; /* Force white text */
                    font-weight: 500;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px; /* Slightly rounded corners like iOS */
                    transition: all 0.2s ease;
                    box-shadow: 0 2px 5px rgba(106, 40, 232, 0.2);
                    font-size: 15px;
                    letter-spacing: 0.5px;
                }}
                
                /* Make sure button text is white */
                div.stButton > button p, 
                div.stButton > button span,
                div.stButton > button div {{
                    color: white !important;
                }}
                div.stButton > button:hover {{
                    box-shadow: 0 4px 10px rgba(106, 40, 232, 0.25);
                    transform: translateY(-1px);
                    filter: brightness(1.05);
                    background-color: {THEME_SECONDARY};
                }}
                
                /* Purple gradient style for Complete Inventory button */
                [data-testid="stButton"] button:has(> div:contains("Export Inventory Report")) {{
                    background: {THEME_GRADIENT} !important;
                    color: white !important; /* Force white text */
                    box-shadow: 0 4px 10px rgba(106, 40, 232, 0.3) !important;
                    transition: all 0.3s ease;
                }}
                /* Fallback selector in case the above doesn't work */
                [data-testid="stButton"] button[kind="secondary"][aria-label="📊 Export Inventory Report"] {{
                    background: {THEME_GRADIENT} !important;
                    color: white !important; /* Force white text */
                    box-shadow: 0 4px 10px rgba(106, 40, 232, 0.3) !important;
                    transition: all 0.3s ease;
                }}
                [data-testid="stButton"] button[kind="secondary"][aria-label="📊 Export Inventory Report"]:hover {{
                    background: linear-gradient(135deg, {THEME_SECONDARY}, {THEME_PRIMARY});
                    box-shadow: 0 6px 15px rgba(106, 40, 232, 0.4);
                    transform: translateY(-2px);
                }}
                div.stButton > button:active {{
                    transform: translateY(1px);
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                }}
                
                /* Global style for download links and buttons */
                a[download], a.download-link {{
                    color: white !important;
                    text-decoration: none !important;
                }}
                a[download] span, a.download-link span {{
                    color: white !important;
                }}
                
                /* iOS style download button */
                .ios-download-btn {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: {THEME_GRADIENT}; /* Theme gradient */
                    color: white !important; /* Force white text */
                    text-decoration: none;
                    padding: 12px 16px;
                    border-radius: 8px;
                    margin: 12px 0;
                    font-weight: 500;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen;
                    transition: all 0.2s ease;
                    box-shadow: 0 2px 5px rgba({THEME_PRIMARY.replace('#', '')}, 0.2);
                }}
                .ios-download-btn:hover {{
                    background: linear-gradient(135deg, {THEME_SECONDARY}, {THEME_PRIMARY});
                    box-shadow: 0 4px 10px rgba({THEME_PRIMARY.replace('#', '')}, 0.25);
                    transform: translateY(-1px);
                }}
                .ios-download-btn:active {{
                    transform: translateY(1px);
                    box-shadow: 0 1px 3px rgba({THEME_PRIMARY.replace('#', '')}, 0.1);
                }}
                .ios-download-icon {{
                    margin-right: 10px;
                    font-size: 18px;
                }}
                
                /* Report card styling */
                .report-cards {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 15px;
                    margin-top: 15px;
                    margin-bottom: 25px;
                }}
                .report-card {{
                    flex: 1;
                    min-width: 220px;
                    background-color: #f8f9fa;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                    transition: all 0.3s ease;
                }}
                .report-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }}
                .report-card-header {{
                    padding: 15px;
                    color: white;
                    font-weight: 600;
                    text-align: center;
                }}
                .report-card-body {{
                    padding: 15px;
                    min-height: 80px;
                    font-size: 14px;
                    color: #444;
                }}
                
                /* Report summary styling */
                .report-summary {{
                    background: linear-gradient(135deg, rgba({THEME_PRIMARY.replace('#', '')}, 0.03), rgba({THEME_SECONDARY.replace('#', '')}, 0.05));
                    border-radius: 10px;
                    padding: 20px;
                    margin-top: 20px;
                    box-shadow: 0 2px 8px rgba({THEME_PRIMARY.replace('#', '')}, 0.1);
                    border: 1px solid rgba({THEME_PRIMARY.replace('#', '')}, 0.1);
                }}
                .summary-header {{
                    font-size: 18px;
                    font-weight: 600;
                    margin-bottom: 15px;
                    color: {THEME_PRIMARY};
                }}
                .summary-metrics {{
                    display: flex;
                    gap: 25px;
                    margin-bottom: 15px;
                }}
                .summary-metric {{
                    flex: 1;
                }}
                .metric-value {{
                    font-size: 24px;
                    font-weight: 700;
                    color: {THEME_SECONDARY}; 
                    text-shadow: 0 1px 2px rgba({THEME_PRIMARY.replace('#', '')}, 0.2);
                }}
                .metric-label {{
                    font-size: 14px;
                    color: #666;
                    margin-top: 5px;
                }}
            </style>
            """, unsafe_allow_html=True)
            
            # Simplified to just one card for the complete inventory report
            col_space1, card_col1, col_space2 = st.columns([1, 4, 1])
            
            with card_col1:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba({THEME_PRIMARY.replace('#', '')}, 0.05), rgba({THEME_SECONDARY.replace('#', '')}, 0.1)); 
                            border-radius: 16px; 
                            border: 1px solid rgba({THEME_PRIMARY.replace('#', '')}, 0.2); 
                            box-shadow: 0 4px 12px rgba({THEME_PRIMARY.replace('#', '')}, 0.15); 
                            padding: 25px 20px; 
                            text-align: center;">
                    <div style="font-size: 36px; margin-bottom: 15px;">📊</div>
                    <div style="font-weight: 600; font-size: 18px; color: {THEME_PRIMARY}; margin-bottom: 12px;">Export Inventory Reports</div>
                    <div style="color: #666; font-size: 15px; line-height: 1.5;">
                        Generate inventory reports with a single click. Download CSV file.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Create the export button row with centered layout to match card
            col_space1, col1, col_space2 = st.columns([1, 4, 1])
            
            # Full inventory report - now using the entire width
            with col1:
                if st.button("📊 Export Inventory Report", key="complete_inv_btn", use_container_width=True):
                    # Get original data without adding columns
                    export_data = prepare_export_data("standard")
                    if export_data is not None:
                        filename = f"inventory_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                        
                        # Check if export_data is a string (CSV content) or DataFrame
                        if isinstance(export_data, str):
                            # Already a CSV string, use it directly
                            csv_content = export_data
                        else:
                            # It's a DataFrame, convert to CSV
                            csv_content = export_data.to_csv(index=False)
                        
                        # Encode for download
                        b64 = base64.b64encode(csv_content.encode()).decode()
                        
                        # Create a purple-themed download button with all text in white
                        download_link = f"""
                        <a class="download-link" href="data:file/csv;base64,{b64}" download="{filename}" style="display: flex; align-items: center; justify-content: center; background: {THEME_GRADIENT}; color: white !important; text-decoration: none !important; padding: 12px 16px; border-radius: 8px; margin: 12px 0; font-weight: 500; transition: all 0.2s ease; box-shadow: 0 4px 10px rgba(106, 40, 232, 0.3);">
                            <span style="margin-right: 10px; font-size: 18px; color: white !important;">📥</span> 
                            <span style="color: white !important;">Download Inventory Report</span>
                        </a>
                        """
                        
                        st.success("✅ Your complete inventory report is ready!")
                        st.markdown(download_link, unsafe_allow_html=True)
                        
                        # Calculate stats for display only
                        # Use stock_data for stats since export_data may be a string now
                        total_items = len(st.session_state.stock_data)
                        
                        # Count the items that have been counted
                        counted_products = set()
                        for product_id, counts in st.session_state.count_data.items():
                            if counts:  # If there are count entries for this product
                                counted_products.add(product_id)
                        counted_items = len(counted_products)
                        
                        completion_pct = round(counted_items/total_items*100, 1) if total_items > 0 else 0
                        
                        # Display a summary with styled metrics
                        st.markdown(f"""
                        <div class="report-summary">
                            <div class="summary-header">Report Summary</div>
                            <div class="summary-metrics">
                                <div class="summary-metric">
                                    <div class="metric-value">{total_items}</div>
                                    <div class="metric-label">Total Items</div>
                                </div>
                                <div class="summary-metric">
                                    <div class="metric-value">{counted_items}</div>
                                    <div class="metric-label">Items Counted</div>
                                </div>
                                <div class="summary-metric">
                                    <div class="metric-value">{completion_pct}%</div>
                                    <div class="metric-label">Completion Rate</div>
                                </div>
                            </div>
                            <div style="color:#666; font-size:14px;">Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Export section complete - removed second export option
    else:
        # Placeholder when no data is loaded
        st.info("👈 Please upload a CSV file from the sidebar to begin counting stock.")
        
        # Show example of the app functionality
        st.subheader("How to use this application:")
        st.markdown("""
        1. **Upload your stock CSV** using the uploader in the sidebar
        2. **Search for products** by Brand and Description
        3. **Add count entries** for each product, with location and notes
        4. **Export results** as a CSV file when finished
        """)
