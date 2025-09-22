import webbrowser


FILE_PATH: str = "repo_stats.html"

class Dashboard():

    @staticmethod
    def generate_html_page(repo_name, authors_html, files_html, last_update_per_file: list[str]):
        with open(FILE_PATH, "w") as f:
            data_list = Dashboard.__manage_list_for_html_page(last_update_per_file)
            html_page = Dashboard.__build_and_get_html_page(repo_name, authors_html, files_html, data_list)
            f.write(html_page)

    @staticmethod
    def open_result_website():
        webbrowser.open(FILE_PATH)

    @staticmethod
    def __manage_list_for_html_page(data_lines: list[str]):
        data = ""
        for line in data_lines:
            data += f"{line}<br>"
        return data

    @staticmethod
    def __build_and_get_html_page(repo_name, authors_html, files_html, data_list):
        html_page = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Repo Stats</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
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
    <h1>Repo Statistics - {repo_name}</h1>
    <div class="tab">
        <button class="tablinks" onclick="openTab(event, 'Authors')" id="defaultOpen">Authors</button>
        <button class="tablinks" onclick="openTab(event, 'Files')">Files</button>
    </div>

    <div id="Authors" class="tabcontent">
        <h2> General stats per author </h2>
        {authors_html}

        <h2> Stats per author over time </h2>
    </div>

    <div id="Files" class="tabcontent">
        <h2> Stats per file </h2>
        {files_html}

        <h2> Last update per file </h2>
        {data_list}
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
