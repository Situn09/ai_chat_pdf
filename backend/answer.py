import fitz # (pymupdf, found this is better than pypdf for our use case, note: licence is AGPL-3.0, keep that in mind if you want to use any code commercially)
from tqdm.auto import tqdm # for progress bars, requires !pip install tqdm
import sys
import random

import torch
import numpy as np
import pandas as pd
from sentence_transformers import util, SentenceTransformer
import textwrap
import re

def answer(query):

    pdf_path="backend/uploaded_files/Blind 75 notes.pdf"

    def text_formatter(text: str) -> str:
        """Performs minor formatting on text."""
        cleaned_text = text.replace("\n", " ").strip() # note: this might be different for each doc (best to experiment)

        # Other potential text formatting functions can go here
        return cleaned_text
    # Open PDF and get lines/pages
    # Note: this only focuses on text, rather than images/figures etc
    def open_and_read_pdf(pdf_path: str) -> list[dict]:
        """
        Opens a PDF file, reads its text content page by page, and collects statistics.

        Parameters:
            pdf_path (str): The file path to the PDF document to be opened and read.

        Returns:
            list[dict]: A list of dictionaries, each containing the page number
            (adjusted), character count, word count, sentence count, token count, and the extracted text
            for each page.
        """
        doc = fitz.open(pdf_path)  # open a document
        pages_and_texts = []
        for page_number, page in tqdm(enumerate(doc)):  # iterate the document pages
            text = page.get_text()  # get plain text encoded as UTF-8
            text = text_formatter(text)
            pages_and_texts.append({"page_number": page_number - 41,  # adjust page numbers since our PDF starts on page 42
                                    "page_char_count": len(text),
                                    "page_word_count": len(text.split(" ")),
                                    "page_sentence_count_raw": len(text.split(". ")),
                                    "page_token_count": len(text) / 4,  # 1 token = ~4 chars, see: https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them
                                    "text": text})
        return pages_and_texts

    pages_and_texts = open_and_read_pdf(pdf_path=pdf_path)
    pages_and_texts[:2]

    from spacy.lang.en import English # see https://spacy.io/usage for install instructions

    nlp = English()

    # Add a sentencizer pipeline, see https://spacy.io/api/sentencizer/
    nlp.add_pipe("sentencizer")

    for item in tqdm(pages_and_texts):
        item["sentences"] = list(nlp(item["text"]).sents)

        # Make sure all sentences are strings
        item["sentences"] = [str(sentence) for sentence in item["sentences"]]

        # Count the sentences
        item["page_sentence_count_spacy"] = len(item["sentences"])


    # Define split size to turn groups of sentences into chunks
    num_sentence_chunk_size = 10

    # Create a function that recursively splits a list into desired sizes
    def split_list(input_list: list,
                slice_size: int) -> list[list[str]]:
        """
        Splits the input_list into sublists of size slice_size (or as close as possible).

        For example, a list of 17 sentences would be split into two lists of [[10], [7]]
        """
        return [input_list[i:i + slice_size] for i in range(0, len(input_list), slice_size)]

    # Loop through pages and texts and split sentences into chunks
    for item in tqdm(pages_and_texts):
        item["sentence_chunks"] = split_list(input_list=item["sentences"],
                                            slice_size=num_sentence_chunk_size)
        item["num_chunks"] = len(item["sentence_chunks"])




    # Split each chunk into its own item
    pages_and_chunks = []
    for item in tqdm(pages_and_texts):
        for sentence_chunk in item["sentence_chunks"]:
            chunk_dict = {}
            chunk_dict["page_number"] = item["page_number"]

            # Join the sentences together into a paragraph-like structure, aka a chunk (so they are a single string)
            joined_sentence_chunk = "".join(sentence_chunk).replace("  ", " ").strip()
            joined_sentence_chunk = re.sub(r'\.([A-Z])', r'. \1', joined_sentence_chunk) # ".A" -> ". A" for any full-stop/capital letter combo
            chunk_dict["sentence_chunk"] = joined_sentence_chunk

            # Get stats about the chunk
            chunk_dict["chunk_char_count"] = len(joined_sentence_chunk)
            chunk_dict["chunk_word_count"] = len([word for word in joined_sentence_chunk.split(" ")])
            chunk_dict["chunk_token_count"] = len(joined_sentence_chunk) / 4 # 1 token = ~4 characters

            pages_and_chunks.append(chunk_dict)


    df = pd.DataFrame(pages_and_chunks)
    print(df.head())

    # Show random chunks with under 30 tokens in length
    min_token_length = 30

    pages_and_chunks_over_min_token_len = df[df["chunk_token_count"] > min_token_length].to_dict(orient="records")
    pages_and_chunks_over_min_token_len[:2]

    # Requires !pip install sentence-transformers
    from sentence_transformers import SentenceTransformer
    embedding_model = SentenceTransformer(model_name_or_path="all-mpnet-base-v2",
                                        device="cpu") # choose the device to load the model to (note: GPU will often be *much* faster than CPU)

    embedding_model.to("cpu")

    # # Embed each chunk one by one
    for item in tqdm(pages_and_chunks_over_min_token_len):
        item["embedding"] = embedding_model.encode(item["sentence_chunk"])


    # Turn text chunks into a single list
    text_chunks = [item["sentence_chunk"] for item in pages_and_chunks_over_min_token_len]


    # Embed all texts in batches
    text_chunk_embeddings = embedding_model.encode(text_chunks,
                                                batch_size=32, # you can use different batch sizes here for speed/performance, I found 32 works well for this use case
                                                convert_to_tensor=True) # optional to return embeddings as tensor instead of array



    # Save embeddings to file
    text_chunks_and_embeddings_df = pd.DataFrame(pages_and_chunks_over_min_token_len)
    embeddings_df_save_path = "text_chunks_and_embeddings_df.csv"
    text_chunks_and_embeddings_df.to_csv(embeddings_df_save_path, index=False)

    # Import saved file and view
    text_chunks_and_embedding_df_load = pd.read_csv(embeddings_df_save_path)


    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Import texts and embedding df
    text_chunks_and_embedding_df = pd.read_csv("text_chunks_and_embeddings_df.csv")

    # Convert embedding column back to np.array (it got converted to string when it got saved to CSV)
    text_chunks_and_embedding_df["embedding"] = text_chunks_and_embedding_df["embedding"].apply(lambda x: np.fromstring(x.strip("[]"), sep=" "))

    # Convert texts and embedding df to list of dicts
    pages_and_chunks = text_chunks_and_embedding_df.to_dict(orient="records")

    # Convert embeddings to torch tensor and send to device (note: NumPy arrays are float64, torch tensors are float32 by default)
    embeddings = torch.tensor(np.array(text_chunks_and_embedding_df["embedding"].tolist()), dtype=torch.float32).to(device)




    embedding_model = SentenceTransformer(model_name_or_path="all-mpnet-base-v2",
                                        device=device) # choose the device to load the model to

    # 1. Define the query
    # Note: This could be anything. But since we're working with a nutrition textbook, we'll stick with nutrition-based queries.
    # query = query

    query_embedding = embedding_model.encode(query, convert_to_tensor=True)


    dot_scores = util.dot_score(a=query_embedding, b=embeddings)[0]

    top_results_dot_product = torch.topk(dot_scores, k=5)
    top_results_dot_product

    larger_embeddings = torch.randn(100*embeddings.shape[0], 768).to(device)


    def print_wrapped(text, wrap_length=80):
        wrapped_text = textwrap.fill(text, wrap_length)
        print(wrapped_text)

    print(pages_and_chunks[0]["sentence_chunk"])

    return pages_and_chunks[0]["sentence_chunk"]

# answer("what is two sum")
sys.modules[__name__]=answer