import json
from logging import getLogger
import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sentence_transformers import SentenceTransformer, util

from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        TextClassificationPipeline,
        pipeline
    )

diagnostic_logger = getLogger(__name__)

#Text Classification Models
_toxicity_model_path = "martin-ha/toxic-comment-model"
_sentiment_model_path = "distilbert-base-uncased-finetuned-sst-2-english"
_lexicon = "vader_lexicon"
_irony_model_path = "cardiffnlp/twitter-roberta-base-irony"
_topic_model_path = "cardiffnlp/tweet-topic-21-multi"
_emotion_model_path = "j-hartmann/emotion-english-distilroberta-base"
_emotion2_model_path = "SamLowe/roberta-base-go_emotions"
_injection_model_path = "JasperLS/gelectra-base-injection"
_coherence_model_path = "madhurjindal/autonlp-Gibberish-Detector-492513457"

#Zero-Shot Classification models
model_path_1 = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
classifier_1 = pipeline("zero-shot-classification", model=model_path_1)
model_path_2 = "facebook/bart-large-mnli"
classifier_2 = pipeline("zero-shot-classification", model=model_path_2)

_topics = [
            "law",
            "finance",
            "medical",
            "education",
            "politics",
            "support",
]

#Sentence Similarity Models
_theme_model_path = "sentence-transformers/all-MiniLM-L6-v2"


def init():
    """Main initialization function"""
    print("This is being run")

    global _toxicity_tokenizer, _toxicity_pipeline
    _toxicity_tokenizer, _toxicity_pipeline = init_pipeline(_toxicity_model_path)

    global _sentiment_tokenizer, _sentiment_pipeline
    _sentiment_tokenizer, _sentiment_pipeline = init_pipeline(_sentiment_model_path)

    global _sentiment_analyzer, _nltk_downloaded
    nltk.download(_lexicon)
    _sentiment_analyzer = SentimentIntensityAnalyzer()

    global _irony_tokenizer, _irony_pipeline
    _irony_tokenizer, _irony_pipeline = init_pipeline(_irony_model_path)

    global _topic_tokenizer, _topic_pipeline
    _topic_tokenizer, _topic_pipeline = init_pipeline(_topic_model_path)

    global _emotion_tokenizer, _emotion_pipeline
    _emotion_tokenizer, _emotion_pipeline = init_pipeline(_emotion_model_path)

    global _emotion2_tokenizer, _emotion2_pipeline
    _emotion2_tokenizer, _emotion2_pipeline = init_pipeline(_emotion2_model_path)

    global _injection_tokenizer, _injection_pipeline
    _injection_tokenizer, _injection_pipeline = init_pipeline(_injection_model_path)

    global _coherence_tokenizer, _coherence_pipeline
    _coherence_tokenizer, _coherence_pipeline = init_pipeline(_coherence_model_path)

    global _similarity_model, _theme_groups
    _similarity_model = SentenceTransformer(_theme_model_path)
    _theme_groups = load_themes("./memory.json")

def calculate_metrics(input_strings: list, with_memory = False):

    #Creates an iterable with all the pipelines we will pass the data through
    all_results = []
    pipelines = [_toxicity_pipeline, _sentiment_pipeline, _irony_pipeline, _topic_pipeline, _emotion_pipeline, 
                 _emotion2_pipeline, _injection_pipeline, _coherence_pipeline]
    tokenizers = [_toxicity_tokenizer, _sentiment_tokenizer, None, None, _emotion_tokenizer, 
                  _emotion2_tokenizer, _injection_tokenizer, _coherence_tokenizer]

    # Process all the data for each indivual pipeline
    for pipeline, tokenizer in zip(pipelines, tokenizers):

        #I dont like this model performance
        if pipeline == _emotion_pipeline:
            continue

        max_length = None if tokenizer is None else tokenizer.model_max_length
        #This will create a list of dictionaries in the form of { 'label_1': 'score', 'label_2': 'score', ...}
        results = pipeline(input_strings, truncation=True, max_length=max_length, top_k=None)
        print(".", end="")
        all_results.append(results)  #Append the results to the list

    # Process the results into a dataframe
    classifications_df = pd.concat([process_data(data) for i, data in enumerate(all_results)], axis=1)


    # These metrics do not have list comprehension, must iterate through each input through the pipeline
    sentiment_nltk = []
    zero_shot_list = []
    for input in input_strings:
        sentiment_score = _sentiment_analyzer.polarity_scores(input)
        sentiment_nltk.append(sentiment_score["compound"])

        zero_shot_output_1 = classifier_1(input, _topics, multi_label=True)
        temp = dict(zip(zero_shot_output_1['labels'], zero_shot_output_1['scores']))
        zero_shot_list.append(temp)

    # Add sentiment nltk as a new column in the dataframe
    classifications_df['sentiment_nltk'] = sentiment_nltk
    # Convert zero shot results into a dataframe
    zero_shot_df = pd.DataFrame(zero_shot_list)


    #Very expensive function: compares EVERY input against a repository of theme embeddings and returns the average similarity to each theme
    #Does not scale well, currently skipping this part
    if _theme_groups is not None and with_memory:
        # Perform similarity operations and append the results
        theme_results = []
        for theme in _theme_groups:
            theme_embeddings = _similarity_model.encode(_theme_groups[theme], convert_to_tensor=True)
            text_embeddings = _similarity_model.encode(input_strings, convert_to_tensor=True)

            # Compute cosine similarities in batch
            similarities = util.pytorch_cos_sim(text_embeddings, theme_embeddings)

            # Compute average similarity for each text embedding
            average_similarities = similarities.mean(dim=1)

            # Convert to a list
            average_similarities = average_similarities.tolist()

            theme_results.append({theme:average_similarities})

        similarity_df = pd.concat([pd.DataFrame(d) for d in theme_results], axis=1)
    else :
        similarity_df = pd.DataFrame()

    # Concatenate all dataframes into a single dataframe
    result_df = pd.concat([classifications_df, similarity_df, zero_shot_df], axis=1)

    return result_df



def init_pipeline(model_path):
    """Helper function to initialize a pipeline"""
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    pipeline = TextClassificationPipeline(model=model, tokenizer=tokenizer)
    return tokenizer, pipeline

def load_themes(json_path: str):
    try:
        skip = False
        with open(json_path, "r", encoding='utf-8') as myfile:
            theme_groups = json.load(myfile)
    except FileNotFoundError:
        skip = True
        diagnostic_logger.warning(f"Could not find {json_path}")
    except json.decoder.JSONDecodeError as json_error:
        skip = True
        diagnostic_logger.warning(f"Could not parse {json_path}: {json_error}")
    if not skip:
        return theme_groups
    return None

def process_data(data, index = 0):
    flattened_dicts = [{d['label']: d['score'] for d in sublist} for sublist in data]
    df = pd.DataFrame(flattened_dicts)
    #df.columns = [f"{col}_{index}" for col in df.columns]  # add suffix to column names
    return df

def sentence_similarity_model():
    return _similarity_model

init()