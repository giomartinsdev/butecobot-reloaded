using ai_api.Models;
using ai_api.Services;
using Microsoft.AspNetCore.Mvc;
using System.Text.Json;

namespace ai_api.Controllers;

[ApiController]
[Route("[controller]")]
public class GenAIController : ControllerBase
{
    private readonly IGenAIService _genAIService;
    private readonly ILogger<GenAIController> _logger;

    public GenAIController(
        IGenAIService genAIService,
        ILogger<GenAIController> logger)
    {
        _genAIService = genAIService;
        _logger = logger;
    }

    [HttpPost("generate")]
    public async Task<ActionResult<GenAIResponse>> GenerateText([FromBody] GenAIRequest request)
    {
        if (string.IsNullOrEmpty(request.Prompt))
        {
            _logger.LogWarning("Request received with empty prompt");
            return BadRequest(new { error = "Prompt cannot be empty." });
        }

        try
        {
            var response = await _genAIService.GenerateAsync(request);
            return Ok(response);
        }
        catch (ArgumentException ex)
        {
            _logger.LogWarning(ex, "Invalid request: {Message}", ex.Message);
            return BadRequest(new { error = ex.Message });
        }
        catch (ApplicationException ex) when (ex.Message.Contains("API key"))
        {
            _logger.LogError(ex, "API key configuration error");
            return StatusCode(500, new { error = "API configuration error", details = ex.Message });
        }
        catch (ApplicationException ex) when (ex.Message.Contains("API error"))
        {
            if (ex.Message.Contains("401") || ex.Message.Contains("Unauthorized"))
            {
                return StatusCode(401, new { error = "Provider authentication failed", details = ex.Message });
            }
            else if (ex.Message.Contains("429") || ex.Message.Contains("Too Many Requests"))
            {
                return StatusCode(429, new { error = "Provider rate limit exceeded", details = ex.Message });
            }
            
            _logger.LogError(ex, "LLM provider API error");
            return StatusCode(502, new { error = "Provider service error", details = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unhandled error while generating response");
            return StatusCode(500, new { error = "Internal server error", details = "An unexpected error occurred." });
        }
    }

    [HttpGet("/health")]
    public IActionResult RootHealthCheck()
    {
        _logger.LogInformation("Root health check requested");
        return Ok(new { status = "healthy", service = "ai-api" });
    }

    [HttpGet("health")]
    public IActionResult HealthCheck()
    {
        _logger.LogInformation("Health check requested");
        return Ok(new { status = "healthy", service = "ai-api" });
    }
}
