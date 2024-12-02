import pandas as pd
import string

def excel_to_html(input_file, sheet_name, headers, sort_columns, table_columns, output_file):
    """
    Converts an Excel sheet into an HTML file with hierarchical headers and tables using Excel-style column letters.

    Parameters:
        input_file (str): Path to the input Excel file.
        sheet_name (str): Name of the sheet to read.
        headers (list): List of Excel-style column letters for hierarchical headers (e.g., ["A", "C", "D", "E"]).
        sort_columns (list): List of Excel-style column letters for sorting the data (e.g., ["A", "D"]).
        table_columns (list): List of Excel-style column letters to include in the tables (e.g., ["M", "N", "L"]).
        output_file (str): Path to save the generated HTML file.
    """
    # Load the Excel sheet
    df = pd.read_excel(input_file, sheet_name=sheet_name, header=None)
    
    # Convert Excel-style column letters to zero-based indices
    def column_letter_to_index(letter):
        return string.ascii_uppercase.index(letter.upper())
    
    header_indices = [column_letter_to_index(col) for col in headers]
    sort_indices = [column_letter_to_index(col) for col in sort_columns]
    table_indices = [column_letter_to_index(col) for col in table_columns]
    
    # Sort the dataframe excluding the first row
    header_row = df.iloc[:1]  # First row to preserve
    data_rows = df.iloc[1:]   # Data rows to sort
    data_rows = data_rows.sort_values(by=sort_indices)
    df = pd.concat([header_row, data_rows], ignore_index=True)  # Re-add the header row
    
    # Start constructing the HTML
    html_content = "<html>\n<body>\n"
    
    # Create a recursive function to generate HTML structure
    def generate_html(group, remaining_headers):
        nonlocal html_content
        if not remaining_headers:
            # If no more headers, generate the table
            html_content += "<table border='1'>\n<tr>"
            for idx in table_indices:
                html_content += f"<th>{df.iloc[0, idx]}</th>"
            html_content += "</tr>\n"
            
            for _, row in group.iterrows():
                html_content += "<tr>"
                for idx in table_indices:
                    html_content += f"<td>{row[idx]}</td>"
                html_content += "</tr>\n"
            html_content += "</table>\n"
            return
        
        current_header_index = remaining_headers[0]
        grouped = group.groupby(df.iloc[:, current_header_index], dropna=False)
        
        for key, subgroup in grouped:
            # Skip empty header values
            if pd.isna(key) or key == "":
                generate_html(subgroup, remaining_headers[1:])
                continue
            
            # Generate the header tag
            html_content += f"<h{len(headers) - len(remaining_headers) + 1}>{key}</h{len(headers) - len(remaining_headers) + 1}>\n"
            generate_html(subgroup, remaining_headers[1:])
    
    # Start the recursive generation
    generate_html(df.iloc[1:], header_indices)
    
    # Close the HTML structure
    html_content += "</body>\n</html>"
    
    # Save the HTML to the specified output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

# Example usage
excel_to_html(
    input_file="data/world-politician-all.xlsx",
    sheet_name="All",
    headers=["B", "C", "E", "G", "J"],  # Excel-style letters
    sort_columns=["B", "A"],       # Excel-style letters
    table_columns=["K", "L", "N", "O"], # Excel-style letters
    output_file="output.html"
)
