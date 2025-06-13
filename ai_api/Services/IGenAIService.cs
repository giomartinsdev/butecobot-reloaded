using ai_api.Models;

namespace ai_api.Services;

public interface IGenAIService
{
    Task<GenAIResponse> GenerateAsync(GenAIRequest request);
}
