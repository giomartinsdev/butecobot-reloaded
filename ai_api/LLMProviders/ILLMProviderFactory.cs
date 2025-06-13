namespace ai_api.LLMProviders;

public interface ILLMProviderFactory
{
    ILLMProvider? GetProvider(string providerName);
}
