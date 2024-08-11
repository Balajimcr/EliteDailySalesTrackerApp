import streamlit as st

def Text(text, font_size='large'):
    latex_text = rf"$\textsf{{\{font_size} {text}}}$"
    return latex_text

tabs_font_css = """
<style>
div[class*="stNumberInput"] label {
  font-size: 26px;
  color: black;
}
</style>
"""

def custom_table_style():
    # CSS to inject contained in a triple-quoted string
    table_style = """
    <style>
    /* Adds styling to the table headers */
    thead tr th {
        background-color: #f0f0f0;  /* Light grey background */
        color: black;               /* Black text */
        font-size: 22pt;           /* Larger font size */
    }
    /* Style for the table data cells */
    tbody tr td {
        color: black;               /* Black text */
        font-size: 20pt;           /* Slightly smaller font size than headers */
    }
    </style>
    """

    # Display the CSS style
    st.markdown(table_style, unsafe_allow_html=True)
    
def display_text(text, color="blue", font_size="24px", font_weight="bold"):
  """
  This function displays a formatted text string in Streamlit.

  Args:
      text: The text to be displayed.
      color: The text color (default: blue).
      font_size: The font size (default: 24px).
      font_weight: The font weight (default: bold).

  Returns:
      None
  """
  # Escape user input to prevent XSS vulnerabilities
  st.markdown(f'<div style="color: {color}; font-size: {font_size}; font-weight: {font_weight};">'\
              f'{text}</div>', unsafe_allow_html=True)

def display_data(dataframe, title):
    """Display a dataframe with a title."""
    st.markdown(f'<div style="color: black; font-size: 24px; font-weight: bold;">{title}:</div>', unsafe_allow_html=True)
    st.dataframe(dataframe)
    
def displayhtml_data(data, title):
    # Applying the style to the dataframe
    """Display a dataframe with a title."""
    st.markdown(f'<div style="color: black; font-size: 24px; font-weight: bold;">{title}:</div>', unsafe_allow_html=True)
    styled_data = data
    html = styled_data.to_html(escape=False)
    st.write(html, unsafe_allow_html=True)  # Display the styled DataFrame as HTML
