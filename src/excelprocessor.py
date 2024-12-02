import pandas as pd

def excel_to_html(input_file, sheet_name, headers, sort_columns, table_columns, output_file):
    """
    Converts an Excel sheet into an HTML file with hierarchical headers and tables.

    Parameters:
        input_file (str): Path to the input Excel file.
        sheet_name (str): Name of the sheet to read.
        headers (list): List of column names for hierarchical headers (e.g., ["A", "C", "D", "E"]).
        sort_columns (list): List of column names for sorting the data (e.g., ["A", "D"]).
        table_columns (list): List of column names to include in the tables (e.g., ["M", "N", "L"]).
        output_file (str): Path to save the generated HTML file.
    """
    # Load the Excel sheet
    df = pd.read_excel(input_file, sheet_name=sheet_name)
    
    # Sort the dataframe by the specified columns
    df = df.sort_values(by=sort_columns, ascending=True)
    
    # Start constructing the HTML
    html_content = "<html>\n<body>\n"
    
    # Create a recursive function to generate HTML structure
    def generate_html(group, remaining_headers):
        nonlocal html_content
        if not remaining_headers:
            # If no more headers, generate the table
            html_content += "<table border='1'>\n<tr>"
            for col in table_columns:
                html_content += f"<th>{col}</th>"
            html_content += "</tr>\n"
            
            for _, row in group.iterrows():
                html_content += "<tr>"
                for col in table_columns:
                    html_content += f"<td>{row[col]}</td>"
                html_content += "</tr>\n"
            html_content += "</table>\n"
            return
        
        current_header = remaining_headers[0]
        grouped = group.groupby(current_header)
        
        for key, subgroup in grouped:
            html_content += f"<h{len(headers) - len(remaining_headers) + 1}>{key}</h{len(headers) - len(remaining_headers) + 1}>\n"
            generate_html(subgroup, remaining_headers[1:])
    
    # Start the recursive generation
    generate_html(df, headers)
    
    # Close the HTML structure
    html_content += "</body>\n</html>"
    
    # Save the HTML to the specified output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

# Example usage
excel_to_html(
    input_file="data.xlsx",
    sheet_name="Sheet1",
    headers=["A", "C", "D", "E"],
    sort_columns=["A", "D"],
    table_columns=["M", "N", "L"],
    output_file="output.html"
)
