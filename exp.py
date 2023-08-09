import streamlit as st
from stats_can import StatsCan
import pandas as pd
import plotly.express as px
import datetime

def run_exp_app():
    @st.cache_data
    def load_and_clean_data():
        sc = StatsCan()
        dp = sc.table_to_df("36-10-0104-01")

        df = (dp.rename(columns={'REF_DATE': 'Date', 'Estimates': 'Item', 'VALUE': 'Value'})
                .loc[dp['Seasonal adjustment'] == 'Seasonally adjusted at annual rates']
                .loc[dp['Prices'] == 'Chained (2012) dollars']
                .loc[dp['UOM'] == 'Dollars']
                .reset_index(drop=True))

        df = df[['Date','Item','Value']].copy()

        df = df.loc[df['Item'].isin(['Final consumption expenditure',
                                        'Gross fixed capital formation',
                                        'Investment in inventories',
                                        'Exports of goods and services',
                                        'Less: imports of goods and services',
                                        'Statistical discrepancy',
                                        'Gross domestic product at market prices',
                                        'Final domestic demand'])].copy()

        df['Date'] = pd.to_datetime(df['Date'])
        df['Value'] = pd.to_numeric(df['Value'])
        df = df.sort_values(by='Date')

        return df

    start_date = pd.Timestamp(st.sidebar.date_input("Start date", datetime.date(2020, 1, 1)))
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

    @st.cache_data
    def convert_df_to_csv(df_filtered):
        return df_filtered.to_csv().encode("utf-8")

    st.subheader("National Expenditure Exploration")
    
    data_exp = st.expander("Preview of National Expenditure Data.")
    data_exp.dataframe(df_filtered)

    csv_file = convert_df_to_csv(df_filtered)
    data_exp.download_button(
        label="Download selected as CSV",
        data=csv_file,
        file_name="can_gdp_expenditure.csv",
        mime="text/csv",
    )

    df_filtered['Date'] = pd.to_datetime(df_filtered['Date'])
    df_filtered.set_index('Date', inplace=True)
    df_filtered['Value'] = pd.to_numeric(df_filtered['Value'])

    yearly_gdp = df_filtered[df_filtered['Item'] == 'Gross domestic product at market prices'].resample('Y').sum()
    yearly_item_values = df_filtered.pivot_table(index=df_filtered.index, columns='Item', values='Value').resample('Y').sum()

    yearly_gdp_df = yearly_item_values.copy()
    for col in yearly_gdp_df.columns:
        yearly_gdp_df[col] = yearly_gdp['Value'].values

    percentage_contribution = (yearly_item_values / yearly_gdp_df) * 100
    percentage_contribution = percentage_contribution.drop(columns=['Gross domestic product at market prices'])

    default_components = ['Final consumption expenditure']
    items = list(percentage_contribution.columns)
    selected_items = st.multiselect('Choose items to view their yearly contribution to GDP', items, default=default_components)

    if selected_items:
        fig = px.line(percentage_contribution[selected_items], x=percentage_contribution.index, y=selected_items)
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig)
    else:
        st.write("Please select at least one item.")

    latest_year = percentage_contribution.iloc[-1]
    latest_year_df = pd.DataFrame(latest_year).reset_index()
    latest_year_df.columns = ['Item', 'Contribution']
    latest_year_df['Short Item'] = latest_year_df['Item'] #.str.split().str[-1]

    st.write("Percentage contribution to GDP for the latest year from the selected period.")

    fig2 = px.bar(latest_year_df, x='Short Item', y='Contribution')
    fig2.update_layout(autosize=False, height=500)
    st.plotly_chart(fig2)

    latest_values = yearly_item_values.iloc[-1]
    latest_values.name = 'Value'
    latest_percentages = percentage_contribution.iloc[-1]
    latest_percentages.name = 'Percentage'
    latest_year_df = pd.concat([latest_values, latest_percentages], axis=1)
    
    st.write("Table of contribution and Percentage contribution to GDP for the most recent year from the selected period.")
    st.write(latest_year_df)

