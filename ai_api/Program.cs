using ai_api.LLMProviders;
using ai_api.Middleware;
using ai_api.Services;
using Microsoft.OpenApi.Models;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo { Title = "GenAI API", Version = "v1" });
});

builder.Services.AddSingleton<LLMProviderFactory>();
builder.Services.AddSingleton<ILLMProviderFactory>(sp => sp.GetRequiredService<LLMProviderFactory>());
builder.Services.AddSingleton<GenAIService>();
builder.Services.AddSingleton<IGenAIService>(sp => sp.GetRequiredService<GenAIService>());

builder.Services.AddHttpClient();

builder.Logging.AddConsole();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseMiddleware<RequestLoggingMiddleware>();

app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();

app.Run();
