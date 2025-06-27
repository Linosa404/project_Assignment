from .functionImplementation import get_hotels_api_v2

def get_function_definitions():
    """
    Returns a list of function definitions used by the assistant.
    Each function definition includes metadata and parameter specifications for dynamic invocation.
    """
    return [
        # File search capability for assistant to locate user data or related files
        {"type": "file_search"},
        # Code interpreter functionality to process and execute code dynamically
        {"type": "code_interpreter"},
        # Function: Get the current date
        {
            "type": "function",
            "function": {
                "name": "get_current_date",
                "description": "Retrieve the current date.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            }
        },
        # Function: Get weather forecast for a specified location and date range
        {
            "type": "function",
            "function": {
                "name": "get_weather_forecast",
                "description": "Retrieve the weather forecast for a specific location and date range for up to 15 days in the future. If the date is further in the future, weather data from the previous year can be used.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City, e.g., London."
                        },
                        "start_date": {
                            "type": "string",
                            "description": "The start date in the format yyyy-MM-dd. The date can be up to 15 days in the future. If the date is more than 15 days in the future, historical weather data from last year should be used."
                        },
                        "end_date": {
                            "type": "string",
                            "description": "The end date in the format yyyy-MM-dd. The date can be up to 15 days in the future. If the date is more than 15 days in the future, historical weather data from last year should be used."
                        }
                    },
                    "required": [
                        "location",
                        "start_date",
                        "end_date"
                    ],
                    "additionalProperties": False,
                },
            },
        },
        # Function: Retrieve flight information for a specified route and date range
        {
            "type": "function",
            "function": {
                "name": "get_flights",
                "description": "Retrieve round trip flight information including price, operator, flight duration, and stops for a specific route, number of passengers, and date range.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "departure": {
                            "type": "string",
                            "description": "Departure airport IATA code, e.g., BER for Berlin."
                        },
                        "arrival": {
                            "type": "string",
                            "description": "Arrival airport IATA code, e.g., PMI for Palma de Mallorca."
                        },
                        "persons": {
                            "type": "number",
                            "description": "Number of passengers traveling, e.g., 1 or 3."
                        },
                        "outbound_date": {
                            "type": "string",
                            "description": "Outbound flight date in the format yyyy-MM-dd, e.g., 2025-01-23. Date must be in the future."
                        },
                        "return_date": {
                            "type": "string",
                            "description": "Return flight date in the format yyyy-MM-dd, e.g., 2025-01-30. Date must be in the future."
                        }
                    },
                    "required": [
                        "departure",
                        "arrival",
                        "persons",
                        "outbound_date",
                        "return_date"
                    ],
                    "additionalProperties": False,
                },
            },
        },
        # Function: Retrieve hotel information for a specific city and date range
        {
            "type": "function",
            "function": {
                "name": "get_hotels",
                "description": "Retrieve hotel information for a specific city, date range, and group size, including name, price, distance from the city center, and other details.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "City where hotels should be searched, e.g., Berlin."
                        },
                        "checkin_date": {
                            "type": "string",
                            "description": "The check-in date in the format yyyy-MM-dd, e.g., 2025-02-10."
                        },
                        "checkout_date": {
                            "type": "string",
                            "description": "The check-out date in the format yyyy-MM-dd, e.g., 2025-02-20."
                        },
                        "adults": {
                            "type": "number",
                            "description": "Number of adults staying in the hotel, e.g., 2."
                        },
                        "rooms": {
                            "type": "number",
                            "description": "Number of rooms required, e.g., 2. Default is 1. If there are no explicit requests for more space, simply set it to 1."
                        }
                    },
                    "required": [
                        "city",
                        "checkin_date",
                        "checkout_date",
                        "adults",
                        "rooms"
                    ],
                    "additionalProperties": False,
                },
            },
        },
        # Function: Send an email with a calendar event attachment
        {
            "type": "function",
            "function": {
                "name": "send_email_with_calendar",
                "description": "Send an email with a calendar event attachment. The email includes recipient details, subject, body, and calendar event information.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recipient": {
                            "type": "string",
                            "description": "Email address of the recipient. Find the E-Mail address in the User_Description",
                        },
                        "subject": {
                            "type": "string",
                            "description": "Subject of the email, e.g., 'Meeting Invitation'."
                        },
                        "body": {
                            "type": "string",
                            "description": "Body text of the email, e.g., 'Please find the details of the meeting attached.' Provide all relevant information from the booking data. Date, city, flight, hotel, activity information should be provided."
                        },
                        "calendar_event_details": {
                            "type": "object",
                            "description": "Details of the calendar event to be created and attached to the email. It should be in a JSON format.",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "Title of the event, e.g., 'Team Meeting'. Default is 'No Title'."
                                },
                                "start": {
                                    "type": "string",
                                    "description": "Start date and time of the event in ISO 8601 format, e.g., '2025-02-10T10:00:00'."
                                },
                                "end": {
                                    "type": "string",
                                    "description": "End date and time of the event in ISO 8601 format, e.g., '2025-02-10T11:00:00'."
                                },
                                "location": {
                                    "type": "string",
                                    "description": "Location of the event, e.g., 'Room 101, Office Building'. Optional."
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Additional details about the event, e.g., 'Discuss Q1 targets'. Optional."
                                }
                            },
                            "required": [
                                "title",
                                "start",
                                "end",
                                "location",
                                "description"
                            ],
                            "additionalProperties": False
                        }
                    },
                    "required": [
                        "recipient",
                        "subject",
                        "body",
                        "calendar_event_details"
                    ],
                    "additionalProperties": False
                }
            },
        },
        # Function: Publish a new post on Bluesky
        {
            "type": "function",
            "function": {
                "name": "send_post",
                "description": "Publish a new post on Bluesky with the specified text content.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Write a blog text for the upcoming vacation with some additional information. Use Smiles and hashtags. Maximum of 300 characters."
                        }
                    },
                    "required": [
                        "text"
                    ],
                    "additionalProperties": False
                }
            }
        },
        # Function: Retrieve personal and holiday events from a Google Calendar
        {
            "type": "function",
            "function": {
                "name": "get_events_in_date_range",
                "description": "Retrieve personal and holiday events from a Google Calendar within a specified date range. Filters include 'busy' events for the personal calendar and official Berlin holidays for the holiday calendar.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "Start date of the range in the format yyyy-MM-dd, e.g., '2025-01-01'."
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date of the range in the format yyyy-MM-dd, e.g., '2025-01-31'."
                        }
                    },
                    "required": [
                        "start_date",
                        "end_date"
                    ],
                    "additionalProperties": False
                }
            }
        },
        # Function: Retrieve hotel information using Booking.com API v2 endpoints
        {
            "type": "function",
            "function": {
                "name": "get_hotels_api_v2",
                "description": "Retrieve hotel information for a specific city and date range using Booking.com API v2 endpoints (via RapidAPI). Returns a summary of the top hotels found.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string", "description": "City where hotels should be searched, e.g., Berlin."},
                        "checkin_date": {"type": "string", "description": "The check-in date in the format yyyy-MM-dd, e.g., 2025-02-10."},
                        "checkout_date": {"type": "string", "description": "The check-out date in the format yyyy-MM-dd, e.g., 2025-02-20."},
                        "adults": {"type": "number", "description": "Number of adults staying in the hotel, e.g., 2."},
                        "children": {"type": "number", "description": "Number of children staying in the hotel, e.g., 1. Default is 0."},
                        "rooms": {"type": "number", "description": "Number of rooms required, e.g., 2. Default is 1."},
                        "locale": {"type": "string", "description": "Locale for the search, e.g., en-gb. Default is en-gb."},
                        "currency": {"type": "string", "description": "Currency code, e.g., AED. Default is AED."}
                    },
                    "required": ["city", "checkin_date", "checkout_date"],
                    "additionalProperties": False
                }
            }
        },
    ]