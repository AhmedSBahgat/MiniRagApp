from .LLMEnums import LLMEnums
from .llm.providers import CohereProvider, OpenAIProvider


class LLMProviderFactory:
    def __init__(self, config: dict):
        self.config = config

    def create_provider(self, provider: str):
        if provider == LLMEnums.OPENAI.value:
            return OpenAIProvider(
                api_key=self.config.OPEN_AI_KEY,
                api_url=self.config.OPENAI_API_URL,
                default_input_max_characters=self.config.DEFAULT_INPUT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.config.DEFAULT_GENERATION_MAX_OUTPUT_TOKENS,
                default_generation_temperature=self.config.DEFAULT_GENERATION_TEMPERATURE,
            )
        if provider == LLMEnums.COHERE.value:
            return CohereProvider(
                api_key=self.config.COHERE_AI_KEY,
                default_input_max_characters=self.config.DEFAULT_INPUT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.config.DEFAULT_GENERATION_MAX_OUTPUT_TOKENS,
                default_generation_temperature=self.config.DEFAULT_GENERATION_TEMPERATURE,
            )

        return None
