import click
import os
from transformers import AutoModel, AutoTokenizer

MODEL_PATH = 'storage/models'
MODEL_IDENTIFIER='myselfronin/cso_ner'

@click.command("download:cso_ner_model", help="This command downloads the CSO NER MOdel from hugging face to local storage")
def download_cso_ner_model():
    click.echo("Downloading the model files...")

    model_dir = os.path.join(MODEL_PATH, "cso_ner_distilbert")

    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    model_files_exist = os.path.exists(os.path.join(model_dir, "config.json")) and \
                        os.path.exists(os.path.join(model_dir, "model.safetensors"))

    if model_files_exist:
        print(f"Model '{MODEL_IDENTIFIER}' already exists in '{model_dir}'. No download necessary.")
    
    try:
        # Load the CSO NER model and tokenizer from Hugging Face
        model = AutoModel.from_pretrained(MODEL_IDENTIFIER)
        tokenizer = AutoTokenizer.from_pretrained(MODEL_IDENTIFIER)

        # Save the model and tokenizer locally in the specified directory
        model.save_pretrained(model_dir)
        tokenizer.save_pretrained(model_dir)

        print("CSO NER model and tokenizer have been downloaded and saved to '{model_dir}'.")
    except Exception as e:

        return f"An error occurred: {str(e)}"