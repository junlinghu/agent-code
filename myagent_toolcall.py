import asyncio

import json
from client import *

model="gpt-4o-mini"

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
                               "description": "The prompt that the user provided."}},
                "required": ["prompt"]}}
    },
]

# Simulated weather fetching function (replace with actual API call in production)
def get_current_weather(city):
    # Mocked response for demonstration
    weather_info = {
        "New York": {"temperature": "15°C", "condition": "Partly cloudy"},
        "San Francisco": {"temperature": "18°C", "condition": "Sunny"},
        "Mountain View": {"temperature": "20°C", "condition": "Sunny"},}
    return weather_info.get(city,{"temperature": "Unknown", "condition": "Unknown"}) #default= Unknown

def lookup_sales_data(prompt: str) -> str:
    table_name = "sales"
    
    return table_name


# Dictionary mapping function names to their funciton implementations
tool_functions = {
    "lookup_sales_data": lookup_sales_data,
    "get_current_weather": get_current_weather,
}

# Inform LLM about the tools available
def LLM_response(messages):
    response = client.chat.completions.create(model=model, messages=messages,temperature=0.0,
                                              tools=tools,tool_choice="auto")
    message = response.choices[0].message
    return message

"""
messages=[{'role': 'system', 'content': "You're a helpful assistant that provides information."}, 
          {'role': 'user', 'content': 'New York'}, 
          {'role': 'tool', 
           'tool_call_id': 'call_RhW4BkROCKKU4U7aPGOCr9M2', 
           'name': 'get_current_weather', 
           'content': {'temperature': '15°C', 'condition': 'Partly cloudy'}}
        ]

response=LLM_response(messages)
print(response.content)

"""
def handle_tool_call(tool_call, messages, message):
    function_name = tool_call.function.name #print(f"function_name: {function_name}")
    function = tool_functions[function_name]
    arguments = json.loads(tool_call.function.arguments)
    result = function(**arguments) #result: {'temperature': '20°C', 'condition': 'Sunny'}

    messages.append({"role": "tool",  "tool_call_id": tool_call.id,
                     "name": function_name, "content": json.dumps(result)})
    #print("messages: ", messages)

    # Send tool response back to LLM
    final_message = LLM_response(messages)
    #response = client.chat.completions.create(model=model, messages=messages,temperature=0.0)
    #final_message = response.choices[0].message
    return final_message

def tool_agent(userInput):
    messages=[{"role": "system", "content": "You're a helpful assistant that provides information."},
              {"role": "user", "content": userInput}]
    message = LLM_response(messages)
        #message:  ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=[], audio=None, 
        #                               function_call=None, 
        #                               tool_calls=[ChatCompletionMessageToolCall(id='call_3U4Je9rTNTyjrlBXrIkJ27sm', 
        #                                               function=Function(arguments='{"city":"New York"}', name='get_current_weather'), 
        #                                               type='function')])
    tool_calls = message.tool_calls
        #tool_calls:  [ChatCompletionMessageToolCall(
        #                   id='call_3U4Je9rTNTyjrlBXrIkJ27sm', 
        #                   function=Function(arguments='{"city":"New York"}', name='get_current_weather'), 
        #                   type='function')
        #              ]
    # Check if LLM requested a tool call
    if tool_calls:
        for tool_call in tool_calls: # Loop through each tool call
            messages.append(message) #This is required for LLM to understand the context, previous message is a tool call
            final_message=handle_tool_call(tool_call, messages, message)
            print(final_message.content)
    else:
        # LLM provided a direct answer without needing a tool
        print(message.content)


def main_loop():
    while True:
        userInput = input("Enter your request: ")
        if userInput.lower() == 'quit':
            print("Goodbye!")
            break

        #weather=get_current_weather(userInput)
        #print (weather)

        tool_agent(userInput)


if __name__ == "__main__":
    main_loop()

