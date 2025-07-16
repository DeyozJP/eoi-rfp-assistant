
import re

def inject_mathjax_index(app):
    """
    Inject MathJax into the HTML template of the Dash app.
    """
    app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
            <script type="text/javascript"
                async
                src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
            </script>
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    '''

def convert_brackets_to_mathjax(text):
    r"""
    Converts LaTeX in square brackets to MathJax format.
    E.g., [ x = y ] → \( x = y \)
    """
    return re.sub(r"\[\s*(.*?)\s*\]", r"\\( \1 \\)", text)


import re

def simplify_latex_math(text):
    # Replace \frac{A}{B} → (A / B)
    text = re.sub(r"\\frac\{(.*?)\}\{(.*?)\}", r"(\1 / \2)", text)

    # Replace \text{...} → just the content
    text = re.sub(r"\\text\{(.*?)\}", r"\1", text)

    # Replace \left( and \right) → just (
    text = text.replace(r"\left(", "(").replace(r"\right)", ")")

    # Replace \times → ×
    text = text.replace(r"\times", "×")

    # Remove any remaining LaTeX \( \) wrappers or brackets
    text = text.replace(r"\(", "").replace(r"\)", "")
    text = re.sub(r"\[|\]", "", text)

    # Remove remaining slashes
    text = text.replace("\\", "")

    return text.strip()
