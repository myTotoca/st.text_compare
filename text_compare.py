import pandas as pd
import streamlit as st
from io import StringIO
from bs4 import BeautifulSoup
from pandas_text_comparer import TextComparer
from jiwer import wer, cer

st.set_page_config(layout="wide")
# st.title('Text Compare')
# st.write("This is a web application for comparing text data.")

def calculate_metrics(df, origin_col, target_col):
    comparer = TextComparer(df, column_a=origin_col, column_b=target_col)
    comparer.run()
    result_df = comparer.result
    mean_ratio = round(result_df['ratio'].mean(),3)
    cer_value = round(result_df.apply(lambda row: cer(row[origin_col], row[target_col]), axis=1).mean(),3)
    wer_value = round(result_df.apply(lambda row: wer(row[origin_col], row[target_col]), axis=1).mean(),3)
    return mean_ratio, cer_value, wer_value, comparer

def compare_from_file():
    uploaded_file = st.file_uploader("Upload a file", type=['csv', 'xlsx'])
    if uploaded_file is not None:
        # 파일을 데이터프레임으로 읽기
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        else:
            df = pd.read_excel(uploaded_file)

        # 컬럼명을 동적으로 가져오기
        columns = df.columns.tolist()
        if len(columns) >= 2:
            origin_col = columns[0]
            target1_col = columns[1]
            target2_col = columns[2] if len(columns) > 2 else None
            
            tab_titles = ["Overview", f"Comparison: {origin_col}-{target1_col}"]
            if target2_col:
                tab_titles.append(f"Comparison: {origin_col}-{target2_col}")
            
            tabs = st.tabs(tab_titles)

            with tabs[0]:
                st.subheader("Metrics Overview")
                mean_ratio1, cer_value1, wer_value1, comparer1 = calculate_metrics(df, origin_col, target1_col)
                metrics_data = {
                    'Comparison': [f"{origin_col}-{target1_col}"],
                    'Ratio': [mean_ratio1],
                    'CER': [cer_value1],
                    'WER': [wer_value1]
                }
                
                if target2_col:
                    mean_ratio2, cer_value2, wer_value2, comparer2 = calculate_metrics(df, origin_col, target2_col)
                    metrics_data['Comparison'].append(f"{origin_col}-{target2_col}")
                    metrics_data['Ratio'].append(mean_ratio2)
                    metrics_data['CER'].append(cer_value2)
                    metrics_data['WER'].append(wer_value2)

                metrics_df = pd.DataFrame(metrics_data)
                metrics_df = metrics_df.set_index('Comparison')
                st.dataframe(metrics_df)
                st.caption("""
                            :blue[Ratio]
                            원본 텍스트와 비교 텍스트 간의 일치율

                            :blue[CER(Character Error Rate)]
                            원본 텍스트와 비교 텍스트 간의 문자(한 글자) 오류율
                            
                            :blue[WER(Word Error Rate)]
                            원본 텍스트와 비교 텍스트 간의 단어(한 단어) 오류율
                            """)

            with tabs[1]:
                st.subheader(f"{origin_col}-{target1_col}")
                st.caption("""
                    :red-background[red]: deleted,
                    :green-background[green]: added, 
                    :orange-background[yellow]: changed
                    """)
                html_code1 = comparer1.get_html()
                soup1 = BeautifulSoup(html_code1, 'html.parser')
                st.markdown(soup1.prettify(), unsafe_allow_html=True)
            
            if target2_col:
                with tabs[2]:
                    st.subheader(f"{origin_col}-{target2_col}")
                    st.caption("""
                    :red-background[red]: deleted,
                    :green-background[green]: added, 
                    :orange-background[yellow]: changed
                    """)
                    html_code2 = comparer2.get_html()
                    soup2 = BeautifulSoup(html_code2, 'html.parser')
                    st.markdown(soup2.prettify(), unsafe_allow_html=True)

def compare_by_entering_text():
    origin, col1, col2 = st.columns(3)
    with origin:
        original_text = st.text_area("Enter original text:")
    with col1:
        target_text1 = st.text_area("Enter target text 1:")
    with col2:
        target_text2 = st.text_area("Enter target text 2:")

    target_texts = [target_text1]
    if target_text2:
        target_texts.append(target_text2)

    if st.button("Compare"):
        data = {"origin": [original_text]}
        for i, target_text in enumerate(target_texts):
            data[f"target{i+1}"] = [target_text]

        df = pd.DataFrame(data)

        columns = df.columns.tolist()
        origin_col = columns[0]
        target1_col = columns[1]
        target2_col = columns[2] if len(columns) > 2 else None

        tab_titles = ["Overview", f"Comparison: {origin_col}-{target1_col}"]
        if target2_col:
            tab_titles.append(f"Comparison: {origin_col}-{target2_col}")

        tabs = st.tabs(tab_titles)

        with tabs[0]:
            st.subheader("Metrics Overview")
            mean_ratio1, cer_value1, wer_value1, comparer1 = calculate_metrics(df, origin_col, target1_col)
            metrics_data = {
                'Comparison': [f"{origin_col}-{target1_col}"],
                'Ratio': [mean_ratio1],
                'CER': [cer_value1],
                'WER': [wer_value1]
            }

            if target2_col:
                mean_ratio2, cer_value2, wer_value2, comparer2 = calculate_metrics(df, origin_col, target2_col)
                metrics_data['Comparison'].append(f"{origin_col}-{target2_col}")
                metrics_data['Ratio'].append(mean_ratio2)
                metrics_data['CER'].append(cer_value2)
                metrics_data['WER'].append(wer_value2)

            metrics_df = pd.DataFrame(metrics_data)
            metrics_df = metrics_df.set_index('Comparison')
            st.dataframe(metrics_df)
            st.caption("""
                            :blue[Ratio]
                            원본 텍스트와 비교 텍스트 간의 일치율

                            :blue[CER(Character Error Rate)]
                            원본 텍스트와 비교 텍스트 간의 문자(한 글자) 오류율
                            
                            :blue[WER(Word Error Rate)]
                            원본 텍스트와 비교 텍스트 간의 단어(한 단어) 오류율
                            """)

        with tabs[1]:
            st.subheader(f"Comparison: {origin_col}-{target1_col}")
            st.caption("""
                    :red-background[red]: deleted,
                    :green-background[green]: added, 
                    :orange-background[yellow]: changed
                    """)
            html_code1 = comparer1.get_html()
            soup1 = BeautifulSoup(html_code1, 'html.parser')
            st.markdown(soup1.prettify(), unsafe_allow_html=True)

        if target2_col:
            with tabs[2]:
                st.subheader(f"Comparison: {origin_col}-{target2_col}")
                st.caption("""
                    :red-background[red]: deleted,
                    :green-background[green]: added, 
                    :orange-background[yellow]: changed
                    """)
                html_code2 = comparer2.get_html()
                soup2 = BeautifulSoup(html_code2, 'html.parser')
                st.markdown(soup2.prettify(), unsafe_allow_html=True)

# 메인 페이지 설정
page = st.sidebar.selectbox("Choose a page:",["Compare from uploaded file", "Compare by entering text"])

if page == "Compare from uploaded file":
    st.title('Text Compare')
    with st.expander("description:"):
        desc = '''업로드 파일은 아래의 내용을 참고해 주시기 바랍니다.
1. 파일 형식: csv
2. 파일 내용: 
    - 열의 이름을 담는 header 가 있어야 합니다. 
    - 반드시 두 개 또는 세 개의 열만을 포함해야 합니다.
    - 첫 번째 열의 값으로는 '기준'될 스크립트, 
      두 번째 열의 값으로는 '비교'할 스크립트를 작성해 주세요.'''
        st.code(desc, language='text')
        st.caption('file example')
        st.dataframe(
            {
            "origin":['liver 내에 small low attenuated lesion 들이 보임', 'spleen 에 특이 소견은 보이지 않음'],
            "comp_A":['liver 내에 low attenuated lesion 들이 보임', 'spleen 에 특이 소견 보이지 않음'],
            "comp_B":['river 내에 small low attenuated lesion 보임', 'spline 에 특이 소견은 보이지 않음']
            })
#    st.markdown("---")
    compare_from_file()
else:
    st.title('Text Compare')
    st.write("")
#    st.markdown("---")
    compare_by_entering_text()
