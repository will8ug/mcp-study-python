import os, re, asyncio, json
from dotenv import load_dotenv
from typing import Optional
from contextlib import AsyncExitStack
from lxml import etree

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

load_dotenv()

class MCPClient:
    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        self.sessions = {}
        self.messages = []

        with open("mcp_client/MCP_Prompt.txt", "r", encoding="utf-8") as f:
            self.system_prompt = f.read()

    async def connect_to_stdio_server(self, server_name: str, server_script_path: str):
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        stdio, write = stdio_transport
        session = await self.exit_stack.enter_async_context(
            ClientSession(stdio, write)
        )
        self.sessions[server_name] = session

        await session.initialize()
        response = await session.list_tools()
        available_tools = ['##' + server_name + 
                           '\n### Available Tools\n- ' + tool.name + 
                           "\n" + tool.description + 
                           "\n" + json.dumps(tool.inputSchema) 
                           for tool in response.tools]
        self.system_prompt = self.system_prompt.replace("<$MCP_INFO$>", "\n".join(available_tools)+"\n<$MCP_INFO$>")

        print(f"Connected to MCP server: {server_name}")
        print(f"Available tools: {response.tools}")

    def parse_tool_request(self, user_input: str) -> Optional[dict]:
        """Parse tool request from user input using regex patterns."""
        tool_pattern = r'(<use_mcp_tool>.*?</use_mcp_tool>)'
        
        match = re.search(tool_pattern, user_input, re.DOTALL)
        if match:
            tool_xml_root = etree.fromstring(match.group(0))
            server_name = tool_xml_root.find('server_name').text.strip()
            tool_name = tool_xml_root.find('tool_name').text.strip()
            arguments_str = tool_xml_root.find('arguments').text.strip()
            
            try:
                arguments = json.loads(arguments_str)
                return {
                    "server_name": server_name,
                    "tool_name": tool_name,
                    "arguments": arguments
                }
            except json.JSONDecodeError:
                print("Error: Invalid JSON in tool arguments")
                return None
        
        return None

    async def call_mcp_tool(self, params: dict) -> str:
        """Call an MCP tool and return the result.
        
        Args:
            params: Dictionary containing:
                - tool_name: Name of the tool to call
                - arguments: Tool arguments dict
                - server_name: Name of the server (optional)
        """
        try:
            tool_name = params.get('tool_name')
            arguments = params.get('arguments', {})
            server_name = params.get('server_name')
            
            result = await self.sessions[server_name].call_tool(tool_name, arguments)
            
            # Handle different result formats
            if hasattr(result, 'content') and result.content:
                # Extract text from content
                text_content = []
                for content in result.content:
                    if hasattr(content, 'text'):
                        text_content.append(content.text)
                return "\n".join(text_content) if text_content else str(result)
            else:
                return str(result)
                
        except Exception as e:
            return f"Error calling tool {params.get('tool_name', 'unknown')}: {str(e)}"

    async def process_natural_language(self, user_input: str) -> str:
        """Process natural language input using OpenAI to extract tool calls."""
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"User asks: {user_input}\n\nPlease respond with the appropriate tool call if needed, or provide a helpful response."}
            ]
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=2048,
                temperature=0.1
            )
            
            response_msg = response.choices[0].message
            print(f"Model response: {response_msg}")
            return response_msg.content
            
        except Exception as e:
            return f"Error processing with AI: {str(e)}"

    async def chat_loop(self):
        """Main chat loop that handles user input and tool calls."""
        print("\n=== MCP Weather Chat ===")
        print("Type 'quit' to exit, or ask questions about weather!")
        print("Example: 'What's the weather in London?'")
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ["quit", "exit", "bye"]:
                    print("Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("Processing your request...")
                ai_response = await self.process_natural_language(user_input)
                
                tool_request = self.parse_tool_request(ai_response)
                
                if tool_request:
                    print("AI suggested tool call")
                    print(f"Server: {tool_request['server_name']}")
                    print(f"Tool: {tool_request['tool_name']}")
                    print(f"Arguments: {tool_request['arguments']}")
                    result = await self.call_mcp_tool(tool_request)
                    print(f"Result: {result}")
                else:
                    print(f"AI Response: {ai_response}")
                        
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error in chat loop: {str(e)}")
            
    async def cleanup(self):
        """Clean up resources"""
        print("Cleaning up resources")
        await self.exit_stack.aclose()

async def main():
    client = MCPClient()
    try:
        await client.connect_to_stdio_server("weather", "mcp_server/server.py")
        await client.chat_loop()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
