import openai
from .blueSkyBot import *
from .functionImplementation import *
from .calendar_utils import *

load_dotenv()

# Define constants for run statuses
STATUS_COMPLETED = "completed"
STATUS_EXPIRED = "expired"
STATUS_REQUIRES_ACTION = "requires_action"
STATUS_IN_PROGRESS = "in_progress"
STATUS_IN_QUEUED = "queued"
STATUS_IN_CANCELLED = "cancelling"

# Initialize OpenAI client and retrieve required environment variables
client = openai.OpenAI()
key = os.getenv("OPENAI_API_KEY")
THREAD_ID = os.getenv("THREAD_ID")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

def run_thread(thread_id, assistant_id):
    """
    Starts a new thread execution for the assistant and returns the run ID.
    """
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )
    return run.id

def create_message(prompt, thread_id):
    """
    Sends a user message to a thread and returns the created message object.
    """
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt,
    )
    return message

def retrieve_run_instances(thread_id, run_id):
    """
    Retrieves the status of a specific thread run by its ID.
    """
    run_list = client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id
    )
    return run_list.status

def retrieve_message_list(thread_id):
    """
    Fetches the list of messages associated with a thread.
    """
    messages = client.beta.threads.messages.list(
        thread_id=thread_id
    )
    return messages.data

def fetch_all_tool_calls(thread_id, run_id):
    """
    Retrieves tool calls required for the thread run, if any, for further processing.
    """
    message = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
    if message.required_action and message.required_action.submit_tool_outputs:
        tool_calls = message.required_action.submit_tool_outputs.tool_calls
        return tool_calls
    else:
        return []

def submit_outputs(thread_id, run_id, tool_outputs):
    """
    Submits tool outputs back to the thread run for further processing.
    """
    run = client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_outputs
    )
    return run

def process_tool_calls(thread_id, run_id):
    """
    Continuously processes tool calls for a thread run based on its current status.
    Executes functions mapped to tool calls and submits the outputs back to the thread.
    """
    while True:
        status = retrieve_run_instances(thread_id, run_id)
        print(f"Status: {status}")

        if status == STATUS_COMPLETED:
            print("Run completed.")
            break
        if status == STATUS_IN_CANCELLED:
            print("Run cancelled.")
            break
        elif status == STATUS_IN_QUEUED:
            print("Run queued.")
            continue
        elif status == STATUS_IN_PROGRESS:
            print("Run is still in progress. Waiting...")
            continue
        elif status == STATUS_REQUIRES_ACTION:
            print("Processing tool calls...\n")
            tool_calls = fetch_all_tool_calls(thread_id, run_id)
            tool_outputs = []
            for tool_call in tool_calls:
                tool_call_id = tool_call.id
                function_name = tool_call.function.name

                try:
                    function_args = json.loads(tool_call.function.arguments)
                    print(f"Function '{function_name}' arguments: {function_args}")

                    if function_name == "get_weather_forecast":
                        output = get_weather_forecast(
                            function_args.get("location"),
                            function_args.get("start_date"),
                            function_args.get("end_date"),
                        )
                    elif function_name == "get_current_date":
                        output = get_current_date()
                    elif function_name == "get_flights":
                        output = get_flights(
                            function_args.get("departure"),
                            function_args.get("arrival"),
                            function_args.get("persons"),
                            function_args.get("outbound_date"),
                            function_args.get("return_date"),
                        )
                    elif function_name == "get_hotels":
                        output = get_hotels(
                            function_args.get("city"),
                            function_args.get("checkin_date"),
                            function_args.get("checkout_date"),
                            function_args.get("adults"),
                            function_args.get("rooms"),
                        )
                    elif function_name == "send_email_with_calendar":
                        output = send_email_with_calendar(
                            function_args.get("recipient"),
                            function_args.get("subject"),
                            function_args.get("body"),
                            function_args.get("calendar_event_details"),
                        )
                    elif function_name == "send_post":
                        output = send_post(
                            function_args.get("text"),
                        )
                    elif function_name == "get_events_in_date_range":
                        output = get_events_in_date_range(
                            function_args.get("start_date"),
                            function_args.get("end_date"),
                        )
                    elif function_name == "get_hotels_api_v2":
                        output = get_hotels_api_v2(
                            function_args.get("city"),
                            function_args.get("checkin_date"),
                            function_args.get("checkout_date"),
                            function_args.get("adults", 2),
                            function_args.get("children", 0),
                            function_args.get("rooms", 1),
                            function_args.get("locale", "en-gb"),
                            function_args.get("currency", "AED")
                        )
                    else:
                        output = {"error": "Function not implemented"}

                    print(f"Function '{function_name}' output: {output}")
                    tool_outputs.append({"tool_call_id": tool_call_id, "output": json.dumps(output)})

                except Exception as e:
                    print(f"Error processing tool call: {e}")
                    tool_outputs.append({"tool_call_id": tool_call_id, "output": json.dumps({"error": str(e)})})

            submit_outputs(thread_id, run_id, tool_outputs)

        elif status == STATUS_EXPIRED:
            print("Run expired.")
            break
        else:
            print("Unhandled status. Exiting.")
            break