import asyncio, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai
from google.genai import types

MODEL = "gemini-2.5-flash"

async def main(question):
    params = StdioServerParameters(command=sys.executable,
                                   args=["net_mcp_server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_tools = (await session.list_tools()).tools
            decls = [types.FunctionDeclaration(name=t.name,
                         description=t.description or "",
                         parameters=t.inputSchema) for t in mcp_tools]
            tools = [types.Tool(function_declarations=decls)]
            config = types.GenerateContentConfig(tools=tools)
            client = genai.Client()
            contents = [types.Content(role="user",
                                      parts=[types.Part(text=question)])]
            while True:
                resp = client.models.generate_content(model=MODEL,
                                          contents=contents, config=config)
                calls = resp.function_calls
                if not calls:
                    print(resp.text)
                    break
                contents.append(resp.candidates[0].content)
                parts = []
                for fc in calls:
                    print(f"[agent calls {fc.name}({dict(fc.args)})]")
                    r = await session.call_tool(fc.name, dict(fc.args))
                    text = r.content[0].text if r.content else ""
                    parts.append(types.Part.from_function_response(
                        name=fc.name, response={"result": text}))
                contents.append(types.Content(role="tool", parts=parts))

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "Which interfaces are up on R1?"
    asyncio.run(main(q))