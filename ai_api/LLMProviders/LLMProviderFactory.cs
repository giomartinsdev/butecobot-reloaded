namespace ai_api.LLMProviders;

public class LLMProviderFactory : ILLMProviderFactory
{
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<LLMProviderFactory> _logger;
    private readonly IConfiguration _configuration;
    private readonly ILoggerFactory _loggerFactory;

    public LLMProviderFactory(
        IServiceProvider serviceProvider,
        ILogger<LLMProviderFactory> logger,
        IConfiguration configuration,
        ILoggerFactory loggerFactory)
    {
        _serviceProvider = serviceProvider;
        _logger = logger;
        _configuration = configuration;
        _loggerFactory = loggerFactory;
    }

    public ILLMProvider? GetProvider(string providerName)
    {
        providerName = providerName.ToLowerInvariant();
        
        try
        {
            return providerName switch
            {
                "openai" => new OpenAIProvider(_loggerFactory.CreateLogger<OpenAIProvider>(), _configuration),
                "gemini" => new GeminiProvider(_loggerFactory.CreateLogger<GeminiProvider>(), _configuration),
                _ => null
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating LLM provider {ProviderName}", providerName);
            return null;
        }
    }
}
