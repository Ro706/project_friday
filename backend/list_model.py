import os

from dotenv import load_dotenv
from groq import Groq


def list_models() -> None:
	"""Print the models available to the configured Groq account."""
	load_dotenv()
	api_key = os.getenv("GROQ_API_KEY")
	if not api_key:
		raise RuntimeError("GROQ_API_KEY is not set in the environment or .env file.")

	client = Groq(api_key=api_key)
	models = client.models.list()

	for model in models.data:
		print(model.id)


if __name__ == "__main__":
	list_models()
