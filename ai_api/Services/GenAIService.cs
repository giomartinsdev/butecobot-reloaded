using ai_api.LLMProviders;
using ai_api.Models;
using System.Text.Json;

namespace ai_api.Services;

public class GenAIService : IGenAIService
{
    private readonly ILLMProviderFactory _llmProviderFactory;
    private readonly ILogger<GenAIService> _logger;
    private readonly IConfiguration _configuration;
    private readonly JsonSerializerOptions _jsonOptions;

    public GenAIService(
        ILLMProviderFactory llmProviderFactory,
        ILogger<GenAIService> logger,
        IConfiguration configuration)
    {
        _llmProviderFactory = llmProviderFactory;
        _logger = logger;
        _configuration = configuration;
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            WriteIndented = true
        };
    }

    public async Task<GenAIResponse> GenerateAsync(GenAIRequest request)
    {
        var sanitizedRequest = new 
        {
            Prompt = SanitizeForLogging(request.Prompt),
            Provider = request.Provider,
            Model = request.Model,
            HasSystemPrompt = !string.IsNullOrEmpty(request.SystemPrompt)
        };
        _logger.LogInformation("Processing GenAI request: {Request}", 
            JsonSerializer.Serialize(sanitizedRequest, _jsonOptions));
        
        var providerName = request.Provider ?? _configuration["GENAI_DEFAULT_PROVIDER"] ?? "openai";
        _logger.LogInformation("Using provider: {ProviderName}", providerName);
        
        var provider = _llmProviderFactory.GetProvider(providerName);
        if (provider == null)
        {
            _logger.LogError("Provider {ProviderName} not supported", providerName);
            throw new ArgumentException($"Provider {providerName} not supported.");
        }

        try
        {
            var startTime = DateTime.UtcNow;
            
            var response = await provider.GenerateAsync(
                prompt: request.Prompt,
                systemPrompt: request.SystemPrompt,
                model: request.Model
            );

            var duration = DateTime.UtcNow - startTime;
            
            _logger.LogInformation("Generated response from {ProviderName} in {Duration}ms. Preview: {ResponsePreview}", 
                providerName, 
                duration.TotalMilliseconds, 
                response.Length > 100 ? response.Substring(0, 100) + "..." : response);

            return new GenAIResponse { 
                Text = response,
                Provider = providerName,
                Model = request.Model ?? "default"
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating response from provider {ProviderName}: {ErrorMessage}", 
                providerName, ex.Message);
            throw;
        }
    }
    
    private string SanitizeForLogging(string text)
    {
        if (string.IsNullOrEmpty(text)) return string.Empty;
        
        const int maxLength = 150;
        if (text.Length > maxLength)
        {
            return text.Substring(0, maxLength) + "...";
        }
        
        return text;
    }
}
