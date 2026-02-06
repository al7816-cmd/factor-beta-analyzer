import streamlit as st
from risk_analyzer import run_analysis

# Page configuration
st.set_page_config(
    page_title="Factor Beta Exposure Tool",
    layout="centered"
)

# Title and description
st.title("Factor Beta Exposure Analyzer")

st.markdown("""
This tool estimates Market, Value, and Momentum factor exposures for a given stock
using trailing daily returns and locally stored factor portfolio data.

Enter a ticker symbol and click **Run Analysis**. If an error occurs when you 
click the button the first time, try it again. If it persists after that, please 
email andy.li@stern.nyu.edu.
""")

# Ticker input
ticker_input = st.text_input(
    "Ticker symbol:",
    value="ex. 'AAPL'",
    max_chars=10
)

# Run analysis button
if st.button("Run Analysis"):

    ticker = ticker_input.strip().upper()

    if ticker == "":
        st.warning("Please enter a valid ticker.")
    else:

        with st.spinner(f"Running analysis for {ticker}..."):

            try:
                # Run your analysis function
                result = run_analysis([ticker])

                # Display success message
                st.success("Analysis complete.")

                # Display results
                st.subheader("Factor Exposure Results")

                # Format numeric columns for readability
                numeric_cols = result.select_dtypes(include="number").columns
                result[numeric_cols] = result[numeric_cols].round(4)

                st.dataframe(
                    result,
                    use_container_width=True
                )

            except Exception as e:

                st.error("An error occurred while running the analysis.")
                st.error(str(e))


# Footer
st.markdown("---")
st.markdown("Factor data loaded locally. Price data sourced from Yahoo Finance.")
st.markdown("The regression is based on Adj. Close Price data from Jan 1 - Dec 31, 2025.")
