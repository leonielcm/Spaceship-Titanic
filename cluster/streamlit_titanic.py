import pandas as pd
import dataikuapi
import streamlit as st

st.header("Predict if the passengers survive")

# File uploader : user can chose any csv file
file_uploaded = st.file_uploader("Choose a dataset", type=["csv"])

# If a file is uploaded :
if file_uploaded is not None:

    # Reading the dataframe
    df = pd.read_csv(file_uploaded)

    # Display dataframe
    st.dataframe(df)

    client = dataikuapi.APINodeClient("https://api-19e29f81-beff558f-dku.eu-west-3.app.dataiku.io/", "api_titanic")

    # Drop NAs and the column Transported if there is one
    df=df.drop(columns="Transported")
    df=df.dropna()

    # Define a function which takes one row and returns the correct format for the API call
    def build_records(row):
        record = {}
        for col in df.columns:
            record[col] = row[col]
        return(record)

    # Applying the function to the dataframe
    records = df.apply(build_records,axis=1)

    predictions = []

    # Making the predictions
    for record in records:
        prediction = client.predict_record("predict", record)
        predictions.append(prediction["result"])

    # Turning the predictions into a dataframe
    df_pred=pd.DataFrame(predictions)

    # Adding the predictions to our first dataframe
    df.insert(13,"prediction",df_pred["prediction"])
    df.insert(14,"probaPercentile",df_pred["probaPercentile"])
    df.insert(15,"probas",df_pred["probas"])

    st.write("Here are your predictions :")
    st.dataframe(df)
