import streamlit as st
import pandas as pd
from stats_can import StatsCan
import plotly.express as px
import datetime
import base64

def run_reg_app():
    # Load and clean Data
    @st.cache_data
    def load_and_clean_data():
        sc = StatsCan()
        dp = sc.table_to_df("36-10-0402-01")

        df = (dp.rename(columns={'REF_DATE': 'Date', 'GEO': 'Region', 'VALUE': 'value'})
                .loc[dp['Value'] == 'Chained (2012) dollars']
                .reset_index(drop=True))

        df = df[['Date','Region','value']].copy()
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df = df.groupby(['Date','Region']).sum().reset_index()

        return df

    def download_link(object_to_download, download_filename, download_link_text):
        if isinstance(object_to_download,pd.DataFrame):
            object_to_download = object_to_download.to_csv(index=False)

        b64 = base64.b64encode(object_to_download.encode()).decode()
        return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

    start_date = pd.Timestamp(st.sidebar.date_input("Start date", datetime.date(2000, 1, 1)))
    end_date = pd.Timestamp(st.sidebar.date_input("End date", datetime.date.today()))

    if start_date > end_date:
        st.sidebar.error("The end date must fall after the start date.")

    def filter_by_date(df, start_date, end_date):
        mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
        df_filtered = df.loc[mask]
        df_filtered['Date'] = pd.to_datetime(df_filtered['Date']).dt.date

        return df_filtered

    df = load_and_clean_data()
    df_filtered = filter_by_date(df, start_date, end_date)
    df_filtered=df_filtered.reset_index(drop=True)

    st.subheader("Regional GDP Exploration")

    data_exp = st.expander("Preview of Regional GDP Data.")
    data_exp.dataframe(df_filtered)

    # Download data
    if st.button('Download Dataframe as CSV'):
        tmp_download_link = download_link(df_filtered, 'YOUR_DF.csv', 'Click here to download your data!')
        st.markdown(tmp_download_link, unsafe_allow_html=True)

    df_filtered['Date'] = pd.to_datetime(df_filtered['Date'])
    df_filtered.set_index('Date', inplace=True)

    yearly_region_values = df_filtered.pivot_table(index=df_filtered.index, columns='Region', values='value')

    yearly_gdp_df = pd.DataFrame(yearly_region_values.sum(axis=1).values.repeat(yearly_region_values.shape[1]).reshape(yearly_region_values.shape), 
                                 columns=yearly_region_values.columns, 
                                 index=yearly_region_values.index)

    percentage_contribution = (yearly_region_values / yearly_gdp_df) * 100

    default_regions = ['Quebec','Alberta','British Columbia'] 
    regions = list(percentage_contribution.columns)
    selected_regions = st.multiselect('Choose regions to view their yearly contribution to GDP', regions, default=default_regions)

    if selected_regions:
        fig = px.line(percentage_contribution[selected_regions], x=percentage_contribution.index, y=selected_regions)
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig)
    else:
        st.write("Please select at least one region.")

    latest_year = percentage_contribution.iloc[-1]
    latest_year_df = pd.DataFrame(latest_year).reset_index()
    latest_year_df.columns = ['Region', 'Contribution']
    latest_year_df['Short Region'] = latest_year_df['Region'].str.split().str[-1]

    st.write("Percentage contribution to GDP for the latest year from the selected period.")

    fig2 = px.bar(latest_year_df, x='Short Region', y='Contribution')
    fig2.update_layout(autosize=False, height=400)
    st.plotly_chart(fig2)

    latest_values = yearly_region_values.iloc[-1]
    latest_values.name = 'value'
    latest_percentages = percentage_contribution.iloc[-1]
    latest_percentages.name = 'Percentage'
    latest_year_df = pd.concat([latest_values, latest_percentages], axis=1)

    st.write("Table of contribution and Percentage contribution to GDP for the most recent latest year from the selected period.")
    st.write(latest_year_df)
