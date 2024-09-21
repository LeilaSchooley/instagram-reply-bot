import configparser
import re
import time
import traceback
from datetime import datetime

import pyanty as dolphin
from openai import OpenAI
from playwright.sync_api import sync_playwright
from pyanty import DolphinAPI


def type_like_human(text, element):
    for char in text:
        element.type(char)
        time.sleep(0.1)  # Simulate typing delay


class InstagramBot:
    def __init__(self, config_path="config.ini"):
        # Load configuration
        config = configparser.ConfigParser()
        config.read(config_path)

        self.DOLPHIN_TOKEN = config.get("DEFAULT", "DOLPHIN_TOKEN")
        self.OPENAI_KEY = config.get("DEFAULT", "OPENAI")
        self.api = DolphinAPI(api_key=self.DOLPHIN_TOKEN)
        self.client = OpenAI(api_key=self.OPENAI_KEY)
        self.response_list = []

        # Initialize Playwright and browser objects
        self.playwright = None
        self.browser = None
        self.page = None

    def start_playwright(self):
        """Initialize Playwright and connect to the browser."""
        profile_id = "459894232"
        profile_response = dolphin.run_profile(profile_id)
        port = profile_response['automation']['port']

        # Start Playwright
        self.playwright = sync_playwright().start()

        # Connect to the browser via CDP (Chrome DevTools Protocol)
        self.browser = self.playwright.chromium.connect_over_cdp(f"http://localhost:{port}")

        # Access the first context and page
        default_context = self.browser.contexts[0]
        self.page = default_context.pages[0]

        # If the page isn't in the inbox, navigate to the inbox
        if self.page.url != "https://www.instagram.com/direct/inbox/":
            self.page.goto('https://www.instagram.com/direct/inbox/')
        time.sleep(5)  # Wait for the page to load

    def wait_for_page_load(self, timeout=60000):
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        except Exception:
            pass

    def get_all_conversation_aria_labels(self):
        # Get all elements that have an aria-label
        all_elements = self.page.query_selector_all('[aria-label]')
        for element in all_elements:
            aria_label = element.get_attribute('aria-label')
            if aria_label and 'Conversation' in aria_label:
                return aria_label

    def generate_response(self, messages, last_message):
        # Prepare the context for OpenAI using the last 100 messages
        conversation_history = [{"role": "user", "content": message} for message in messages]
        conversation_history.append({
            "role": "user",
            "content": f"Reply to this Instagram message: {last_message}",
        })

        # Improve the prompt to make it clear the response should be in the first person
        conversation_history.append({
            "role": "system",
            "content": (
                "You are responding to a conversation. Always reply in the first person as if you're directly responding to the user. "
                "Use the context of the last 100 messages to formulate a coherent and relevant reply. "
                "Your response should feel natural, engaging, and polite. Avoid overly simple or generic replies like 'H' or smiley faces. "
                "Be as helpful as possible and provide meaningful feedback based on the conversation's flow."
            )
        })

        # Generate a response using the context
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # Using GPT-4 as specified
            messages=conversation_history,
            max_tokens=50
        )

        return response.choices[0].message.content.strip()

    def get_last_hundred_messages(self):

        time.sleep(3)
        self.wait_for_page_load()
        messages = []
        message_elements = self.page.locator(
            '[aria-label="Double tap to like"]').all()  # Adjust the selector based on Instagram's structure
        count = min(len(message_elements), 100)

        for i in range(count):
            message_text = message_elements[i].text_content().strip()
            if message_text:
                messages.append(message_text)

        print(f"Retrieved {len(messages)} messages.")
        return messages

    def get_last_message_time(self):
        try:
            # Wait for the page to fully load
            self.wait_for_page_load()

            # Locate elements with the aria-label "Double tap to like"
            presentations = self.page.locator('[aria-label="Double tap to like"]')

            if presentations.count() > 0:
                # Get the last presentation and hover over it
                last_presentation = presentations.nth(presentations.count() - 1)
                last_presentation.hover()
                print("Hovered over the last presentation.")

                self.page.get_by_label("Messages in conversation with").locator("div").filter(
                    has_text=re.compile(r"^More$")).nth(2).click()

                # Click the "More" button to reveal the message time
                print("Clicked 'More' button.")

                # Get the last message's time
                last_message_time = self.page.locator(
                    ".x1dm5mii > div > div > div > div > div > div").first.text_content()
                print(f"Last message time: {last_message_time}")

                return last_message_time

            else:
                print("No presentations found.")
                return None
        except:
            traceback.print_exc()

    def get_last_message_text(self):
        try:
            presentations = self.page.locator('[aria-label="Double tap to like"]')
            if presentations.count() > 0:
                last_presentation = presentations.nth(presentations.count() - 1)
                last_message_text = last_presentation.text_content().strip()
                print(f"Last message text: {last_message_text}")
                return last_message_text
            else:
                print("More button not found or not visible.")
                return None
        except Exception as e:
            print(f"Error fetching last message: {e}")
            return None

    def send_message(self, name=None):
        try:
            self.page.get_by_role("button", name="New message", exact=True).click()
            time.sleep(2)
            self.page.get_by_placeholder("Search...").fill(name)
            time.sleep(2)

            # Locate all <label> elements and click on the first one
            self.page.locator('label').first.click()

            time.sleep(2)

            self.page.get_by_role("button", name="Chat").click()
            time.sleep(2)

            last_message_text = self.get_last_message_text()
            messages = self.get_last_hundred_messages()
            print(f"Found message from: {name}, sent within 5 minutes. Replying")
            reply = self.generate_response(messages, last_message_text)
            print(f"Reply generated by OpenAI: {reply}")
            message_input = self.page.get_by_label("Message", exact=True)
            type_like_human(reply, message_input)
            self.page.keyboard.press("Enter")

            time.sleep(5)
            print(f"Sent message to {name}")
        except:
            print(traceback.print_exc())

    def is_last_message_within_5_minutes(self, last_message_text):
        try:
            potential_times = re.findall(r'\d{2}:\d{2}', last_message_text)
            if not potential_times:
                raise ValueError("No valid time patterns found in the message.")

            potential_times = list(dict.fromkeys(potential_times))
            message_time_str = potential_times[0]
            message_time = datetime.strptime(message_time_str, "%H:%M").time()
            current_datetime = datetime.now()
            message_datetime = datetime.combine(current_datetime.date(), message_time)
            time_difference = current_datetime - message_datetime
            time_difference_in_minutes = time_difference.total_seconds() / 60
            return time_difference_in_minutes >= 5
        except Exception as e:
            print(f"Error parsing last message time: {e}")
            return False

    def check_inbox_and_reply(self):
        while True:
            try:
                # self.page.pause()
                # Step 1: Check all conversations
                print("Starting to check all conversations...")
                elements = self.page.locator(".x13dflua")

                # Increase the timeout to handle slow elements
                count = elements.count()  # Wait up to 60 seconds for elements to load
                print(f"Number of conversations found: {count}")

                # Step 2: Loop through each conversation
                for i in range(count):
                    try:
                        element = elements.nth(i)
                        element_text = element.text_content(timeout=30000)  # Increased timeout for element text
                        class_attr = element.get_attribute("class")
                        print(f"Processing conversation {i}: {element_text} | Main class: {class_attr}")

                        # Step 3: Check for a specific class that indicates a new message
                        child_elements = element.locator('*')
                        child_count = child_elements.count()
                        # print(f"Number of child elements in conversation {i}: {child_count}")

                        # Step 4: Loop through all child elements to check for the specific class
                        for j in range(child_count):
                            try:
                                child_class = child_elements.nth(j).get_attribute("class")
                                # Check if the user has received a new message
                                if child_class and "xzolkzo" in child_class:
                                    print(f"Found new message from user in conversation {i}")

                                    # Step 5: Click the element to open the conversation
                                    element.click()
                                    print(f"Clicked on conversation {i} to open the message.")

                                    self.wait_for_page_load(self.page)
                                    print("Waiting for the page to fully load...")
                                    time.sleep(5)

                                    # Step 6: Get the last message time
                                    last_message_time = self.get_last_message_time()
                                    time.sleep(2)

                                    print(f"Last message time for conversation {i}: {last_message_time}")
                                    name = self.get_all_conversation_aria_labels()
                                    if "with " in name:
                                        name = name.split("with ")[1]
                                    self.response_list.append({
                                        "time": last_message_time,
                                        "name": name
                                    })

                                    # Step 8: Break out after processing the current message
                                    print(f"Breaking inner loop after processing conversation {i}.")
                                    self.page.go_back()
                                    self.wait_for_page_load(self.page)
                                    break  # Breaks the inner loop, continues to the next conversation
                            except TimeoutError:
                                print(f"Timeout while checking child elements of conversation {i}. Continuing...")
                                continue  # Continue to the next child element

                    except TimeoutError:
                        print(f"Timeout while processing conversation {i}. Skipping...")
                        continue  # Continue to the next conversation

                print(self.response_list)

                # Step 9: Process items in the response list (handling them in a FIFO manner)
                print(f"Processing {len(self.response_list)} items in response list...")

                for index, item in enumerate(
                        self.response_list):  # Create a shallow copy with self.response_list[:]
                    item_message_time = item['time']
                    username = item['name']

                    if self.is_last_message_within_5_minutes(item_message_time):
                        print(f"Item {index} is within 5 minutes, sending message.")

                        self.send_message(username)
                        print(f"Message sent for item {index}. Removing from response list.")

                        # Remove the processed element from the response list
                        self.response_list.pop(index)

                    else:
                        print(f"Item {index} is not within 5 minutes. Skipping...")

                # Step 10: Pause before checking again
                print("Pausing before checking again...")
                time.sleep(15)

            except Exception as e:
                # Debugging any general exception
                print(f"Error occurred: {e}")
                traceback.print_exc()

                # Attempt to reload the page in case of failure
                # try:
                #    self.page.reload()
                #    self.wait_for_page_load(self.page)
                # except Exception as reload_error:
                #    print(f"Error reloading the page: {reload_error}")
                #    self.page.pause()

    def close_playwright(self):
        """Gracefully close the Playwright browser and stop Playwright."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()


# Entry point to run the bot
if __name__ == "__main__":
    bot = InstagramBot()
    bot.start_playwright()  # Start Playwright and browser
    bot.check_inbox_and_reply()
