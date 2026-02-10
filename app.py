x.import streamlit as st
from risk_analyzer import run_analysis

# Page configuration
st.set_page_config(
    page_title="Factor Beta Exposure Tool",
    layout="centered"
)

# Title and description
st.title("Factor Beta Exposure Analyzer")

st.markdown("""
This tool estimates Market, Value, and Momentum factor exposures for stocks
using daily returns and factor portfolio data from Kenneth French's library.

Enter one or more ticker symbols (comma-separated) and click **Run Analysis**.
If it doesn't work at first, click it again. If the issue persists, email 
andy.li@stern.nyu.edu.
""")

# Ticker input
ticker_input = st.text_input(
    "Ticker symbol(s) (comma-separated):",
    value="ex. 'AAPL'",
    max_chars=100
)

# Run analysis button
if st.button("Run Analysis"):

    ticker_input_clean = ticker_input.strip().upper()

    if ticker_input_clean == "":
        st.warning("Please enter a valid ticker.")
    else:

        # Parse comma-separated tickers
        tickers = [t.strip() for t in ticker_input_clean.split(',') if t.strip()]

        with st.spinner(f"Running analysis for {', '.join(tickers)}..."):

            try:
                # Run your analysis function
                result = run_analysis(tickers)

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
st.markdown("""Factor data loaded locally, sourced from Kenneth French's data library:
https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
\n Price data sourced from Yahoo Finance.""")
