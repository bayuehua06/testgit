import pandas as pd
import string


def excel_to_html(input_file, sheet_name, headers, sort_columns, table_columns, output_file):
    # Load the Excel sheet
    df = pd.read_excel(input_file, sheet_name=sheet_name, header=None)

    # Convert Excel-style column letters to zero-based indices
    def column_letter_to_index(letter):
        return string.ascii_uppercase.index(letter.upper())

    # Parse the headers into groups of indices
    header_groups = [
        [column_letter_to_index(col) for col in header.split(",")] for header in headers
    ]
    sort_indices = [column_letter_to_index(col) for col in sort_columns]
    table_indices = [column_letter_to_index(col) for col in table_columns]

    # Separate the last header group (for <p>)
    paragraph_group = header_groups.pop()

    # Precompute combined header values
    def compute_combined_values(df, group_indices):
        """Computes combined header values for a list of column indices."""
        combined = df[group_indices[0]].astype(str)
        for idx in group_indices[1:]:
            combined = combined.where(
                df[idx].isna() | df[idx].astype(str).eq("nan") | df[idx].eq(""),
                combined + " --- " + df[idx].astype(str),
            )
        return combined.replace("", "").replace(" --- nan", "").replace(" --- ", "")

    # Add columns for all header levels
    for i, group in enumerate(header_groups):
        df[f"header_{i + 1}"] = compute_combined_values(df, group)

    # Add paragraph column
    df["paragraph"] = compute_combined_values(df, paragraph_group)

    # Sort the dataframe
    header_row = df.iloc[:1]  # Keep the first row as is
    data_rows = df.iloc[1:]   # Sort only data rows
    data_rows = data_rows.sort_values(by=sort_indices, ignore_index=True)
    df = pd.concat([header_row, data_rows], ignore_index=True)

    # Start constructing the HTML
    html_parts = [
        "<html>\n<head>\n",
        '<link rel="stylesheet" type="text/css" href="output.css">\n',
        "</head>\n<body>\n"
    ]

    # Recursive HTML generation
    def generate_html(group, level, max_level):
        """Generates HTML content for a grouped dataframe."""
        if level > max_level:
            # Handle paragraph and table at the last level
            last_paragraph = None
            table_rows = []

            for index, row in group.iterrows():
                current_paragraph = row["paragraph"]

                # If the paragraph changes, flush the table rows
                if current_paragraph != last_paragraph:
                    if table_rows:
                        # Output the last paragraph and table
                        if last_paragraph and str(last_paragraph).strip() not in ["nan", ""]:
                            last_paragraph = last_paragraph.lstrip("nan --- ").strip()
                            html_parts.append(
                                f'<div class="description"><p>{last_paragraph}</p></div>\n'
                            )

                        html_parts.append("<table class='table' border='1'>\n<tr class='table-header'>")
                        html_parts.extend([f"<th class='table-header-cell'>{df.iloc[0, idx]}</th>" for idx in table_indices])
                        html_parts.append("</tr>\n")

                        for table_row in table_rows:
                            html_parts.append("<tr class='table-row'>")
                            html_parts.extend([f"<td class='table-cell'>{table_row[idx]}</td>" for idx in table_indices])
                            html_parts.append("</tr>\n")
                        html_parts.append("</table>\n")

                    # Reset table rows for the new paragraph
                    table_rows = []

                # Add the current row to the table rows
                table_rows.append(row)

                # Update the last paragraph
                last_paragraph = current_paragraph

            # Flush the remaining rows
            if table_rows:
                if last_paragraph and str(last_paragraph).strip() not in ["nan", ""]:
                    last_paragraph = last_paragraph.lstrip("nan --- ").strip()
                    html_parts.append(
                        f'<div class="description"><p>{last_paragraph}</p></div>\n'
                    )

                html_parts.append("<table class='table' border='1'>\n<tr class='table-header'>")
                html_parts.extend([f"<th class='table-header-cell'>{df.iloc[0, idx]}</th>" for idx in table_indices])
                html_parts.append("</tr>\n")

                for table_row in table_rows:
                    html_parts.append("<tr class='table-row'>")
                    html_parts.extend([f"<td class='table-cell'>{table_row[idx]}</td>" for idx in table_indices])
                    html_parts.append("</tr>\n")
                html_parts.append("</table>\n")
            return

        # Iterate over all rows in the current group
        for header_value, subgroup in group.groupby(f"header_{level}", dropna=False, sort=False):
            if header_value and str(header_value).strip() not in ["nan", ""]:
                header_value = header_value.lstrip("nan --- ").strip()
                html_parts.append(f"<h{level} class='header-{level}'>{header_value}</h{level}>\n")
            generate_html(subgroup, level + 1, max_level)

    # Start recursive generation
    generate_html(df.iloc[1:], 1, len(header_groups))

    # Add JavaScript before the closing </body> tag
    script = """
<script>
    document.querySelectorAll('h1, h2, h3, h4, h5, h6, h7').forEach((header, index) => {
        const level = header.tagName.substring(1);
        const generatedId = `header-${level}-${index + 1}`;
        header.id = generatedId;
    });
</script>
"""
    html_parts.append(script)
    html_parts.append("</body>\n</html>")

    # Save the HTML to the specified output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("".join(html_parts))


# Example usage
if __name__ == "__main__":
    excel_to_html(
        input_file="data/data.xlsx",
        sheet_name="All",
        headers=["B", "C", "D", "E,F", "G,H", "I,J"],  # Excel-style letters
        sort_columns=["B", "A"],       # Excel-style letters
        table_columns=["K", "L", "N", "O"], # Excel-style letters
        output_file="output.html"
    )
