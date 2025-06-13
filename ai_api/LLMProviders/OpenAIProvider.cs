using Azure.AI.OpenAI;

namespace ai_api.LLMProviders;

public class OpenAIProvider : ILLMProvider
{
    private readonly ILogger<OpenAIProvider> _logger;
    private readonly string _apiKey;

   //TODO: GIO: NAO SEI SE ISSO TA FUNCIONANDO, NO GEMINI QUE É O UNICO QUE TENHO KEY USEI INTEGRACAO VIA HTTP NAO CLIENT DA AZURE
    public OpenAIProvider(ILogger<OpenAIProvider> logger, IConfiguration configuration)
    {
        _logger = logger;
        _apiKey = configuration["OPENAI_API_KEY"] ?? throw new ArgumentNullException("OPENAI_API_KEY configuration is missing");
    }

    public async Task<string> GenerateAsync(string prompt, string? systemPrompt = null, string? model = null)
    {
        try
        {
            var client = new OpenAIClient(_apiKey);
            
            var options = new ChatCompletionsOptions
            {
                DeploymentName = model ?? "gpt-3.5-turbo"
            };

            if (!string.IsNullOrEmpty(systemPrompt))
            {
                options.Messages.Add(new ChatRequestSystemMessage(systemPrompt));
            }
            
            options.Messages.Add(new ChatRequestUserMessage(prompt));

            var response = await client.GetChatCompletionsAsync(options);
            return response.Value.Choices[0].Message.Content;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating response from OpenAI");
            throw new ApplicationException($"OpenAIProvider error: {ex.Message}", ex);
        }
    }
}
