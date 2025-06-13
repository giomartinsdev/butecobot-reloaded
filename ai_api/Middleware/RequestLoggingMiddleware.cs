using System.Diagnostics;
using System.Text;
using System.Text.RegularExpressions;

namespace ai_api.Middleware;

public class RequestLoggingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<RequestLoggingMiddleware> _logger;

    public RequestLoggingMiddleware(RequestDelegate next, ILogger<RequestLoggingMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        var stopwatch = Stopwatch.StartNew();
        
        var originalResponseBodyStream = context.Response.Body;
        
        using var responseBodyStream = new MemoryStream();
        context.Response.Body = responseBodyStream;

        try
        {
            string requestBody = await GetRequestBodyAsync(context.Request);
            _logger.LogInformation(
                "HTTP {Method} {Path} received - {ContentType} {ContentLength} bytes",
                context.Request.Method,
                context.Request.Path,
                context.Request.ContentType,
                context.Request.ContentLength);

            if (!string.IsNullOrEmpty(requestBody))
            {
                var sanitizedBody = SanitizeRequestBody(requestBody);
                _logger.LogDebug("Request Body: {RequestBody}", sanitizedBody);
            }

            await _next(context);

            stopwatch.Stop();
            responseBodyStream.Seek(0, SeekOrigin.Begin);
            string responseBody = await new StreamReader(responseBodyStream).ReadToEndAsync();
            
            _logger.LogInformation(
                "HTTP {StatusCode} returned in {ElapsedMilliseconds}ms - {ContentType} {ContentLength} bytes",
                context.Response.StatusCode,
                stopwatch.ElapsedMilliseconds,
                context.Response.ContentType,
                responseBodyStream.Length);

            if (!string.IsNullOrEmpty(responseBody) && responseBodyStream.Length < 4000)
            {
                if (responseBody.Length > 500)
                {
                    responseBody = responseBody.Substring(0, 500) + "...";
                }
                _logger.LogDebug("Response Body: {ResponseBody}", responseBody);
            }

            responseBodyStream.Seek(0, SeekOrigin.Begin);
            await responseBodyStream.CopyToAsync(originalResponseBodyStream);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing request");
            throw;
        }
        finally
        {
            context.Response.Body = originalResponseBodyStream;
        }
    }

    private async Task<string> GetRequestBodyAsync(HttpRequest request)
    {
        if (!request.Body.CanRead || request.ContentLength == 0)
        {
            return string.Empty;
        }

        request.EnableBuffering();
        
        using var reader = new StreamReader(
            request.Body,
            encoding: Encoding.UTF8,
            detectEncodingFromByteOrderMarks: false,
            leaveOpen: true);
        
        var body = await reader.ReadToEndAsync();
        
        request.Body.Position = 0;
        
        return body;
    }

    private string SanitizeRequestBody(string body)
    {
        if (body.Length > 1000)
        {
            body = body.Substring(0, 1000) + "...";
        }
        
        body = Regex.Replace(body, "\"[a-zA-Z0-9_-]{20,}\"", "\"[API_KEY_REDACTED]\"");
        
        return body;
    }
}
