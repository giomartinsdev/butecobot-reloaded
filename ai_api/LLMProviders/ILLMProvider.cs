namespace ai_api.LLMProviders;

public interface ILLMProvider
{
    Task<string> GenerateAsync(string prompt, string? systemPrompt = null, string? model = null);
}
