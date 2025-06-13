FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS base
WORKDIR /app
EXPOSE 80
EXPOSE 443

FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src
COPY ["ai_api/ai_api.csproj", "ai_api/"]
RUN dotnet restore "ai_api/ai_api.csproj"
COPY . .
WORKDIR "/src/ai_api"
RUN dotnet build "ai_api.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "ai_api.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "ai_api.dll"]
