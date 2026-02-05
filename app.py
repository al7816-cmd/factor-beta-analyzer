import streamlit as st
from analysis import load_factor_data, load_prices, compute_correlations

st.set_page_config(page_title="Factor Exposure Tool")

st.title("Factor Exposure Analyzer")

ticker = st.text_input("Enter a ticker:", "AAPL")

if st.button("Run Analysis"):
    try:
        factors = load_factor_data()
        prices = load_prices(ticker.upper())

        results = compute_correlations(prices, factors)

        st.subheader("Correlation with Factor Portfolios")
        st.dataframe(results)

    except Exception as e:
        st.error("Something went wrong. Check the ticker or data.")
