excel_to_html(
    input_file="data/world-politician-all.xlsx",
    sheet_name="All",
    headers=["B", "C", "E", "G", "J"],  # Excel-style letters
    sort_columns=["B", "A"],       # Excel-style letters
    table_columns=["K", "L", "N", "O"], # Excel-style letters
    output_file="output.html"
)