namespace ai_api.Models;

public class GenAIRequest
{
    public required string Prompt { get; set; }
    public string? Provider { get; set; }
    public string? SystemPrompt { get; set; }
    public string? Model { get; set; }
}
