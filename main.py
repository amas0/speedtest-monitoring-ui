import os

import altair as alt
import pandas as pd
import requests
import streamlit as st


def get_results():
    url = os.environ.get('SPEEDTEST_DATA_URL', 'http://192.168.0.102:7898')
    results = requests.get(f'{url}/get-all-results').json()
    return results['results']


def clean_results(results: list) -> pd.DataFrame:
    df = pd.DataFrame(results)
    df.timestamp = pd.to_datetime(df.timestamp, utc=True).dt.tz_convert(tz='US/Eastern')
    df.latency = df.latency.str.extract(r'([^\s]+)').astype(float)
    df.download = df.download.str.extract(r'([^\s]+)').astype(float)
    df.upload = df.upload.str.extract(r'([^\s]+)').astype(float)
    return df


def trigger_speedtest():
    url = os.environ.get('SPEEDTEST_DATA_URL', 'http://192.168.0.102:7898')
    requests.get(f'{url}/run-test')


res_df = clean_results(get_results())
speed_df = pd.melt(res_df, id_vars=['timestamp'], value_vars=['download', 'upload'])
speed_df.variable = speed_df.variable.str.capitalize()

st.title('Internet speedtest results')
st.write('Internet speed tests are run automatically on a semi-random basis. The below '
         'visualizations show collected data - upload and download speeds as well as latency. The '
         'most recent speedtest was performed at **' + str(res_df.timestamp.max().strftime('%c')) + '.**')

speed_chart = alt.Chart(speed_df).mark_point(tooltip=True).encode(
    x=alt.X('timestamp:T', title='Timestamp'),
    y=alt.Y('value:Q', title='Speed (Mbit/s)'),
    color=alt.Color('variable', title=None, legend=alt.Legend(orient='top', labelFontSize=16)))
speed_chart += speed_chart.mark_line()
speed_chart = speed_chart

latency = alt.Chart(res_df).mark_point(tooltip=True).encode(
    x=alt.X('timestamp:T', title='Timestamp'),
    y=alt.Y('latency:Q', title='Latency (ms)'))
latency += latency.mark_line()
latency = latency.properties(height=160)

download_hist = alt.Chart(res_df).mark_bar().encode(
    alt.X('download:Q', bin=True, title='Speed (Mbit/s)'),
    y=alt.Y('count()', axis=None)
).properties(title='Download', height=160)
upload_hist = alt.Chart(res_df).mark_bar().encode(
    alt.X('upload:Q', bin=True, title='Speed (Mbit/s)'),
    y=alt.Y('count()', axis=None)
).properties(title='Upload', height=160)
latency_hist = alt.Chart(res_df).mark_bar().encode(
    alt.X('latency:Q', bin=True, title='Latency (ms)'),
    y=alt.Y('count()', axis=None)
).properties(title='Latency', height=160)

st.altair_chart(speed_chart.configure_axis(labelFontSize=14, titleFontSize=16), use_container_width=True)
st.altair_chart(latency.configure_axis(labelFontSize=14, titleFontSize=16), use_container_width=True)

st.write('To see how these vary overall, we can take a look at the histograms of our data.')

st.altair_chart(download_hist.configure_axis(labelFontSize=16, titleFontSize=18).configure_title(fontSize=18),
                use_container_width=True)
st.altair_chart(upload_hist.configure_axis(labelFontSize=16, titleFontSize=18).configure_title(fontSize=18),
                use_container_width=True)
st.altair_chart(latency_hist.configure_axis(labelFontSize=16, titleFontSize=18).configure_title(fontSize=18),
                use_container_width=True)

st.button('Trigger Speedtest', on_click=trigger_speedtest)