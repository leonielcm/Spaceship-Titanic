import json
import os
from time import sleep
import pandas as pd
import dataikuapi
import requests
import streamlit as st
from confluent_kafka import Producer
from confluent_kafka import Consumer


def read_ccloud_config(config_file):
    omitted_fields = set(['schema.registry.url', 'basic.auth.credentials.source', 'basic.auth.user.info'])
    conf = {}
    with open(config_file) as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                if parameter not in omitted_fields:
                    conf[parameter] = value.strip()


    # On cherche les données d'environnement USERNAME et PASSWORD de l'API
    sasl_username = os.environ.get('CLOUDKARAFKA_USERNAME')
    sasl_password = os.environ.get('CLOUDKARAFKA_PASSWORD')
    # On ajoute ces données au dictionnaire conf
    conf['sasl.username'] = sasl_username
    conf['sasl.password'] = sasl_password
    return conf

# PRODUCER
def produce_data():
    producer = Producer(read_ccloud_config("./client.properties"))

    # Fetch response from https://api-56ce4d5f-779f448b-dku.eu-west-3.app.dataiku.io/public/api/v1/titanic_passengers/passenger/run
    response = requests.get("https://api-56ce4d5f-779f448b-dku.eu-west-3.app.dataiku.io/public/api/v1/titanic_passengers/passenger/run")
    data = response.json()

    data_keyed = data['response']
    json_data = json.dumps(data_keyed)
    producer.produce(TOPIC, key="key", value=json_data)
    producer.flush()
    


# CONSUMER
def consume_data():
    props = read_ccloud_config("./client.properties")
    props["group.id"] = "python-group-1"
    props["auto.offset.reset"] = "earliest"

    consumer = Consumer(props)
    consumer.subscribe([TOPIC])
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is not None and msg.error() is None:
                print("key = {key:12} value = {value:12}".format(key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))
                consumer.close()
                return msg.value().decode('utf-8')
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
    

# API/FUNCTION CALLS

prediction_df = pd.DataFrame()

st.header("We predict if the last 10 passengers of the Spaceship Titanic survived or got transported !")

client_ml = dataikuapi.APINodeClient("https://api-19e29f81-beff558f-dku.eu-west-3.app.dataiku.io/", "api_titanic")

TOPIC = "Titanic"

st.write("Here are your predictions :")

placeholder = st.empty()
container = st.container()





while True:
    #Si predictions_df contient 10 lignes, on retire le premier élément
    if len(prediction_df) == 10:
        prediction_df = prediction_df.iloc[1:]

    # On produit des données
    produce_data()
    cons_data = consume_data()
    # data revient en json
    cons_data = json.loads(cons_data)
    # On envoie ces données à l'API de Dataiku pour prédire si les passagers ont survécu ou non
    prediction = client_ml.predict_record("predict", cons_data)
    

    # On créé un json avec le les informations du passager et la prédiction
    # On prend les données suivantes :
    # - PassengerId
    # - Pclass
    # - Name
    # - Surname

    fate = "Survived" if prediction["result"]["prediction"] == "true" else "Transported to another dimension"

    data_to_display = {
        "Passenger ID": cons_data["PassengerId"],
        "Name": cons_data["Name"],
        "Cabin": cons_data["Cabin"],
        "Fate": fate
    }

    # On transforme ce json en dataframe
    new_df = pd.json_normalize(data_to_display)

    # On ajoute ce dataframe à notre dataframe de prédiction
    prediction_df = pd.concat([prediction_df, new_df])


    # On affiche les prédictions
    with placeholder.container():
        st.write(prediction_df)

    sleep(2)





# # File uploader : user can chose any csv file
# file_uploaded = st.file_uploader("Choose a dataset", type=["csv"])

# # If a file is uploaded :
# if file_uploaded is not None:

#     # Reading the dataframe
#     df = pd.read_csv(file_uploaded)

#     # Display dataframe
#     st.dataframe(df)

#     client = dataikuapi.APINodeClient("https://api-19e29f81-beff558f-dku.eu-west-3.app.dataiku.io/", "api_titanic")

#     # Drop NAs and the column Transported if there is one
#     df=df.drop(columns="Transported")
#     df=df.dropna()

#     # Define a function which takes one row and returns the correct format for the API call
#     def build_records(row):
#         record = {}
#         for col in df.columns:
#             record[col] = row[col]
#         return(record)

#     # Applying the function to the dataframe
#     records = df.apply(build_records,axis=1)

#     predictions = []

#     # Making the predictions
#     for record in records:
#         prediction = client.predict_record("predict", record)
#         predictions.append(prediction["result"])

#     # Turning the predictions into a dataframe
#     df_pred=pd.DataFrame(predictions)

#     # Adding the predictions to our first dataframe
#     df.insert(13,"prediction",df_pred["prediction"])
#     df.insert(14,"probaPercentile",df_pred["probaPercentile"])
#     df.insert(15,"probas",df_pred["probas"])

#     st.write("Here are your predictions :")
#     st.dataframe(df)


# DONNEES DE CONNEXION AU CLOUD KAFKA



