import asyncio

import json
from client import *

model="gpt-4o-mini"

# Simulated weather fetching function (replace with actual API call in production)
def get_current_weather(city):
    # Mocked response for demonstration
    weather_info = {
        "New York": {"temperature": "15°C", "condition": "Partly cloudy"},
        "San Francisco": {"temperature": "18°C", "condition": "Sunny"},
        "Mountain View": {"temperature": "20°C", "condition": "Sunny"},}
    return weather_info.get(city,{"temperature": "Unknown", "condition": "Unknown"}) #default= Unknown

# User's input about weather
user_message = "What's the weather like in Mountain View today?"

# Define the function schema for GPT-4o
tools = [
    {"type": "function",
     "function": {
            "name": "get_current_weather",
            "description": "Get the current weather for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string",
                             "description": "The city to fetch weather information for."}},
                "required": ["city"]}}
    },
    {"type": "function",
     "function": {
            "name": "lookup_sales_data",
            "description": "Look up data from Sales Promotions dataset",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", 
                               "description": "The unchanged prompt that the user provided."}},
                "required": ["prompt"]}}
    },
]


def tool_agent(userInput):
    messages=[{"role": "system", "content": "You're a helpful assistant that provides information."},
              {"role": "user", "content": userInput}]
    response = client.chat.completions.create(model=model, messages=messages,temperature=0.0,
                                              tools=tools,tool_choice="auto")
    message = response.choices[0].message

    # Check if GPT-4o requested a tool call
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        """
        # Execute the tool call (fetch weather)
        if function_name == "get_current_weather":
            city = arguments.get("city")
            weather_result = get_current_weather(city)

            # Send tool response back to GPT-4o
            second_response = openai.chat.completions.create(model=model,
                messages=[
                    {"role": "system", "content": "You're a helpful assistant that provides weather information."},
                    {"role": "user", "content": user_message},
                    message,  # previous GPT-4o message (requesting tool call)
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": json.dumps(weather_result)
                    }
                ],
                temperature=0.0
            )

            final_message = second_response.choices[0].message.content
            print(final_message)
        """

    else:
        # LLM provided a direct answer without needing a tool
        print(message.content)


async def main():
    while True:
        userInput = input("Enter your request: ")
        if userInput.lower() == 'quit':
            print("Goodbye!")
            break

        #weather=get_current_weather(userInput)
        #print (weather)

        result = await Runner.run(tool_agent_agent, input=userInput)
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())

