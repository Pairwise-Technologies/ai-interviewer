from openai import OpenAI
import os

def get_client() -> OpenAI:
    '''
    Initalizes an instance of the client and returns it to the requested source 

    Parameters:
        None

    Returns:
        client : OpenAI
            returns the client used to send api calls  
    '''
    client = OpenAI(
        api_key=os.environ.get("OPENAI-API-KEY"),
    )
    return client 


def get_bot_response(client: OpenAI, conversation_history: list, model_type: str = "gpt-4o", tools: list = [], tool_choice: dict = None) -> dict:
    '''
    Gives the bot conversation history and then sends back a reply to the user. 

    Parameters: 
        client : OpenAI
            Uses the client to send the call
        conversation_history : list
            Gives the AI bot conversation history in list
        model_type : str
            Allows the function callers the option to change the model type if need be
        tools : 
            list of tools (optional)
        tool_choice : 
             dict (optional) → enforce specific tool usage

    Returns: 
            OpenAI message object
    '''
    response = client.chat.completions.create(
                messages=conversation_history,
                model=model_type,
                tools=tools,
                #tool_choice=tool_choice, # useful for multiple tools
             )

    return response.choices[0].message
    
