using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;

namespace ai_api.LLMProviders;

public class GeminiProvider : ILLMProvider
{
    private readonly ILogger<GeminiProvider> _logger;
    private readonly string _apiKey;
    private readonly HttpClient _httpClient;
    private readonly JsonSerializerOptions _jsonOptions;

    public GeminiProvider(ILogger<GeminiProvider> logger, IConfiguration configuration)
    {
        _logger = logger;
        _apiKey = configuration["GEMINI_API_KEY"] ?? throw new ArgumentNullException("GEMINI_API_KEY configuration is missing");
        _httpClient = new HttpClient();
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            WriteIndented = true
        };
    }

    public async Task<string> GenerateAsync(string prompt, string? systemPrompt = null, string? model = null)
    {
        try
        {
            var modelName = model ?? "gemini-1.5-flash";
            
            var apiUrl = $"https://generativelanguage.googleapis.com/v1/models/{modelName}:generateContent?key={_apiKey}";

            string combinedPrompt = prompt;
            if (!string.IsNullOrEmpty(systemPrompt))
            {
                combinedPrompt = $"{systemPrompt}\n\n{prompt}";
                _logger.LogInformation("Combined system and user prompts for Gemini compatibility");
            }

            var requestPayload = new Dictionary<string, object>
            {
                ["contents"] = new[]
                {
                    new Dictionary<string, object>
                    {
                        ["parts"] = new[]
                        {
                            new Dictionary<string, object>
                            {
                                ["text"] = combinedPrompt
                            }
                        }
                    }
                },
                ["generationConfig"] = new Dictionary<string, object>
                {
                    ["temperature"] = 0.7,
                    ["maxOutputTokens"] = 1024,
                    ["topP"] = 0.8,
                    ["topK"] = 40
                }
            };

            var jsonPayload = JsonSerializer.Serialize(requestPayload, _jsonOptions);
            _logger.LogInformation("Sending request to Gemini API: {JsonPayload}", jsonPayload);

            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");
            var request = new HttpRequestMessage(HttpMethod.Post, apiUrl)
            {
                Content = content
            };
            request.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));

            _logger.LogDebug("Making HTTP request to Gemini API at {Url}", apiUrl);

            var response = await _httpClient.SendAsync(request);
            var responseContent = await response.Content.ReadAsStringAsync();
            
            _logger.LogDebug("Received response from Gemini API: Status={StatusCode}, Content={ResponseContent}", 
                response.StatusCode, responseContent);

            if (!response.IsSuccessStatusCode)
            {
                _logger.LogError("Error response from Gemini API: {StatusCode}, {Response}", 
                    response.StatusCode, responseContent);
                throw new ApplicationException($"Gemini API error: {response.StatusCode}, {responseContent}");
            }

            using var responseJson = JsonDocument.Parse(responseContent);
            
            if (!responseJson.RootElement.TryGetProperty("candidates", out var candidates) || 
                candidates.GetArrayLength() == 0)
            {
                throw new ApplicationException("No candidates returned from Gemini API");
            }

            if (!candidates[0].TryGetProperty("content", out var content0) ||
                !content0.TryGetProperty("parts", out var parts) ||
                parts.GetArrayLength() == 0 ||
                !parts[0].TryGetProperty("text", out var textElement))
            {
                throw new ApplicationException("Unexpected response format from Gemini API");
            }

            var textResponse = textElement.GetString() ?? string.Empty;

            return textResponse;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating response from Gemini: {Message}", ex.Message);
            
            var errorDetails = ex is ApplicationException 
                ? ex.Message 
                : $"Unexpected error: {ex.Message}. See logs for details.";
                
            throw new ApplicationException($"GeminiProvider error: {errorDetails}", ex);
        }
    }
}
