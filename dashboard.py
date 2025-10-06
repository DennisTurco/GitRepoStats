import html
import webbrowser

from entities.data import Data

FILE_PATH: str = "repo_stats.html"

class Dashboard():

    @staticmethod
    def generate_html_page(data: Data) -> None:
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            data_table_files = Dashboard.__list_to_html_table(data.csv_file_stats, "tableFiles")
            data_table_branches = Dashboard.__list_to_html_table(data.csv_branches_stats, "tableBranches")
            data_table_code_complexity = Dashboard.__list_to_html_table(data.csv_code_complexity, "tableCodeComplexity", "|")
            data_table_code_duplication = Dashboard.__list_to_html_table(data.csv_code_duplication, "tableCodeDuplication", "|")
            data_table_bus_factor = Dashboard.__list_to_html_table(data.csv_bus_factor, "tableBusFactor")
            html_page = Dashboard.__build_and_get_html_page(data, data_table_files, data_table_branches, data_table_code_complexity, data_table_code_duplication, data_table_bus_factor)
            f.write(html_page)

    @staticmethod
    def open_result_website() -> None:
        webbrowser.open(FILE_PATH)

    @staticmethod
    def __list_to_html_table(data: list[str], table_id: str, delimiter=",") -> str:
        # parsing CSV
        rows = [row.split(delimiter) for row in data]
        if not rows:
            return "<p>No data available</p>"

        header, *body = rows
        col_count = len(header)
        normalized_body = [row + [""] * (col_count - len(row)) for row in body]

        # --- special case
        if table_id == "tableBusFactor":
            table_html = f"<table id='{table_id}' class='display'>\n"
            table_html += "  <thead><tr>" + "".join(f"<th>{html.escape(str(col))}</th>" for col in header) + "</tr></thead>\n"
            table_html += "  <tbody>\n"
            for row in normalized_body:
                table_html += "    <tr>" + "".join(f"<td>{str(Dashboard.__truncate_with_tooltip(col))}</td>" for col in row) + "</tr>\n"
            table_html += "  </tbody>\n</table>"
            return table_html

        # --- default table ---
        table_html = f"<table id='{table_id}' class='display'>\n"
        table_html += "  <thead><tr>" + "".join(f"<th>{html.escape(str(col))}</th>" for col in header) + "</tr></thead>\n"
        table_html += "  <tbody>\n"
        for row in normalized_body:
            table_html += "    <tr>" + "".join(f"<td>{str(Dashboard.__truncate_with_tooltip(col))}</td>" for col in row) + "</tr>\n"
        table_html += "  </tbody>\n</table>"

        return table_html

    @staticmethod
    def __truncate_with_tooltip(text: str, max_length: int = 50) -> str:
        """
        Truncate the text if it's too long, adding a tooltip with the full text.
        """
        text = html.escape(str(text))
        if len(text) <= max_length:
            return text
        truncated = "..." + text[len(text)-max_length:len(text)]
        return truncated


    @staticmethod
    def __build_and_get_html_page(data: Data, data_table_files: str, data_table_branches: str, data_table_code_complexity: str, data_table_code_duplication: str, data_table_bus_factor: str) -> str:
        html_page = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Git Repo Stats</title>
    <meta charset="UTF-8">

    <!-- DataTables CSS + JS -->
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.4/css/jquery.dataTables.min.css">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
    <link rel="stylesheet" href="https://cdn.datatables.net/rowgroup/1.3.1/css/rowGroup.dataTables.min.css">
    <script src="https://cdn.datatables.net/rowgroup/1.3.1/js/dataTables.rowGroup.min.js"></script>
    <link rel="shortcut icon" type="image/x-icon" href="https://github.com/DennisTurco/GitRepoStats/raw/master/imgs/logo64x64.ico" />

    <script>
        $(document).ready(function() {{
            $('#tableFiles').DataTable({{
                "pageLength": 20,
                "lengthMenu": [5, 10, 20, 50, 100],
                "order": []
            }});
            $('#tableBranches').DataTable({{
                "pageLength": 20,
                "lengthMenu": [5, 10, 20, 50, 100],
                "order": []
            }});
            $('#tableCodeComplexity').DataTable({{
                "pageLength": 20,
                "lengthMenu": [5, 10, 20, 50, 100],
                "order": []
            }});
            $('#tableCodeDuplication').DataTable({{
                "pageLength": 20,
                "lengthMenu": [5, 10, 20, 50, 100],
                "order": []
            }});
            $('#tableBusFactor').DataTable({{
                "pageLength": 20,
                "lengthMenu": [5, 10, 20, 50, 100],
                "order": [],
                "rowGroup": {{
                    dataSrc: 0
                }}
            }});
        }});
    </script>

    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .tab {{
            overflow: hidden;
            border-bottom: 1px solid #ccc;
        }}
        .tab button {{
            background-color: #f1f1f1;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 14px 16px;
            transition: 0.3s;
            font-size: 16px;
        }}
        .tab button:hover {{ background-color: #ddd; }}
        .tab button.active {{ background-color: #ccc; }}
        .tabcontent {{ display: none; padding: 20px 0; }}
        .chart-info summary {{
            cursor: pointer;
            font-weight: bold;
            font-size: 0.95em;
            color: #444;
            list-style: none;
            margin: 10px;
            margin-bottom: 20px;
            margin-left: 20px;
        }}
        .chart-info summary::marker {{
            content: "▶ ";
            color: #666;
        }}
        .chart-info[open] summary::marker {{
            content: "▼ ";
        }}
        .chart-info aside {{
            background: #f9f9f9;
            border-left: 3px solid #007acc;
            padding: 15px 20px;
            margin-top: 8px;
            margin-left: 20px;
            margin-bottom: 20px;
            font-size: 0.9em;
            line-height: 1.5;
            border-radius: 6px;
        }}
    </style>
</head>
<body>
    <h1 style="display: flex; align-items: center; gap: 10px;">
        <img src="https://raw.githubusercontent.com/DennisTurco/GitRepoStats/master/imgs/logo64x64.ico"
            alt="Logo" width="64" height="64">
        Repo Statistics - {data.repo_name}
    </h1>
    <h3>Period: {data.period}</h3>
    <div class="tab">
        <button class="tablinks" onclick="openTab(event, 'Authors')" id="defaultOpen">Authors</button>
        <button class="tablinks" onclick="openTab(event, 'Files')">Files</button>
        <button class="tablinks" onclick="openTab(event, 'CodeAnalysis')">Code Analysis</button>
    </div>

    <div id="Authors" class="tabcontent">
        <h2> General stats per author </h2>
        {data.chart_authors_html}

        <h2> Stats per author over time </h2>
        {data.chart_commits_html}
        {data.chart_cumulative_commits_html}
        {data.chart_branches_html}
        {data.chart_cumulative_branches_html}

        <h3> Branches List </h3>
        {data_table_branches}
    </div>

    <div id="Files" class="tabcontent">
        <h2> Stats per file </h2>
        {data.chart_files_html}
        {data.chart_languages_html}

        <h2> Last update per file </h2>
        {data_table_files}
    </div>

    <div id="CodeAnalysis" class="tabcontent">
        <h2> Code Complexity </h2>
        <details class="chart-info">
            <summary>ℹ️ Data description</summary>
            <aside>
                <p>
                    <ul>
                        <li><b>NLOC</b>: effective lines of code (excluding comments/blank)</li>
                        <li><b>CCN</b>: cyclomatic Complexity Number.(complex if > 10)</li>
                        <li><b>Token</b>: number of tokens in the function</li>
                        <li><b>Param</b>: number of function parameters</li>
                        <li><b>Length</b>: total function length in lines (similar to nloc but including also declarations, exc...)</li>
                        <li><b>Function</b>: function or method name</li>
                        <li><b>Lines</b>: line range in the source file</li>
                        <li><b>File</b>: file path containing the function</li>
                    </ul>
                </p>
                <p>
                    <h6>You can see Lizard documentation: <a href="https://github.com/terryyin/lizard" target="_blank">here</a></h6>
                </p>
                <p>
                    Status values:
                    <ul>
                        <li>✅: if all checks are passed (nloc <= 30 and ccn <= 10 and token <= 100 and param <= 4)</li>
                        <li>⚠️: if something needs attentions (nloc <= 100 and ccn <= 20 and token <= 500 and param <= 7)</li>
                        <li>❌: if something is at risk</li>
                    </ul>
                    you can filter by inserting the emoji in the table search bar.
                </p>
            </aside>
        </details>
        {data_table_code_complexity}

        <h2> Code Duplication Detection </h2>

        <details class="chart-info">
            <summary>ℹ️ Data description</summary>
            <aside>
                <p>
                    This section shows detected duplicated code blocks in the repository, helping identify redundancy and maintainability issues.
                </p>

                <h4>How to read it</h4>
                <ul>
                    <li><strong>Similarity Score</strong>: a numeric score measuring how similar two code blocks are.
                        Lower values mean higher similarity (0 = identical code).
                        This score is calculated from both structural metrics (lines of code, cyclomatic complexity, parameters, tokens, etc.)
                        and text similarity between code blocks.
                    </li>
                    <li><strong>File A / File B</strong>: file paths containing the duplicated code.</li>
                    <li><strong>Function</strong>: the function or method where duplication was found.</li>
                    <li><strong>Lines</strong>: line ranges of duplicated sections.</li>
                </ul>

                <h4>Why this matters</h4>
                <p>
                    Code duplication increases maintenance cost and can lead to inconsistencies. Detecting duplication allows refactoring,
                    improves readability, and reduces bugs by centralizing logic.
                </p>
                <p>
                    Consider addressing duplication especially when similarity scores are high and occur in critical parts of the system.
                </p>
            </aside>
        </details>

        {data_table_code_duplication}


        <h2>Code ownership by file</h2>

        <details class="chart-info">
            <summary>ℹ️ About this report</summary>
            <aside>
                <p>
                    This chart shows how <strong>code ownership</strong> is distributed among authors for each file in the repository.
                </p>

                <h4>How to read it</h4>
                <ul>
                    <li><strong>Lines</strong>: the number of lines currently attributed to an author in the file.</li>
                    <li><strong>Percentage</strong>: the proportion of ownership relative to the total file size.</li>
                </ul>

                <h4>Why this matters</h4>
                <p>
                    Understanding code ownership helps assess the <em>bus factor</em> — the risk that knowledge about a
                    file or component is concentrated in too few people.
                </p>
                <p>
                    Ideally, ownership should be shared among multiple authors.
                    If a single author controls more than ~20-30% of a file, it could indicate a potential knowledge concentration risk,
                    depending on project size and complexity, making the project more vulnerable if that person leaves the team.
                </p>
            </aside>
        </details>

        {data_table_bus_factor}


    </div>

    <script>
        function openTab(evt, tabName) {{
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {{
                tabcontent[i].style.display = "none";
            }}
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {{
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }}
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }}
        document.getElementById("defaultOpen").click();
    </script>
</body>
</html>
        """
        return html_page
