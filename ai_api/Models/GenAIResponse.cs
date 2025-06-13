namespace ai_api.Models;

public class GenAIResponse
{
    public string Text { get; set; } = string.Empty;
    public string Provider { get; set; } = string.Empty;
    public string Model { get; set; } = string.Empty;
}
