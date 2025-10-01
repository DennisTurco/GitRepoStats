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
            html_page = Dashboard.__build_and_get_html_page(data, data_table_files, data_table_branches, data_table_code_complexity)
            f.write(html_page)

    @staticmethod
    def open_result_website() -> None:
        webbrowser.open(FILE_PATH)

    @staticmethod
    def __list_to_html_table(data: list[str], table_id: str, delimiter=",") -> str:
        rows = [row.split(delimiter) for row in data]
        header, *body = rows
        col_count = len(header)

        normalized_body = [row + [""] * (col_count - len(row)) for row in body]

        table_html = f"<table id='{table_id}' class='display'>\n"
        table_html += "  <thead><tr>" + "".join(f"<th>{html.escape(str(col))}</th>" for col in header) + "</tr></thead>\n"
        table_html += "  <tbody>\n"
        for row in normalized_body:
            table_html += "    <tr>" + "".join(f"<td>{html.escape(str(col))}</td>" for col in row) + "</tr>\n"
        table_html += "  </tbody>\n</table>"

        return table_html

    @staticmethod
    def __build_and_get_html_page(data: Data, data_table_files: str, data_table_branches: str, data_table_code_complexity: str) -> str:
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
            }})
            $('#tableCodeComplexity').DataTable({{
                "pageLength": 20,
                "lengthMenu": [5, 10, 20, 50, 100],
                "order": []
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
        Data description:
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
        <h6>You can see Lizard documentation: <a href="https://github.com/terryyin/lizard" target="_blank">here</a></h6>
        <p></p>
        Status values:
        <ul>
            <li>✅: if all checks are passed (nloc <= 30 and ccn <= 10 and token <= 100 and param <= 4)</li>
            <li>⚠️: if something needs attentions (nloc <= 100 and ccn <= 20 and token <= 500 and param <= 7)</li>
            <li>❌: if something is at risk</li>
        </ul>
        you can filter by inserting the emoji in the table search bar.
        {data_table_code_complexity}

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
