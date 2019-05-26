### RENAME TO APP_MESSAGES
class Messages():
    """
    Class for organising multi-language messages to the user
    """

    # Data model to contain columns: language, app, action, result, message


    def __init__(self):

        self.language = 'EN'
        # This is our temporary database. Replace with a Django model database
        # Messages blend with keyword arguments (dict), by enclosing keywords
        # in curly brackets
        self.messages = { }
        self.messages['EN'] = { }
        self.messages['EN']['item_rename_failure'] = "ERROR: Could not rename item {current_label} to {new_label}, as this name is used by another item."
        self.messages['EN']['item_rename_success'] = "SUCCESS: Renamed item {current_label} to {new_label}."
        self.messages['EN']['item_create_failure'] = "ERROR: Could not create item {new_label}, as this name is used by another item."
        self.messages['EN']['item_create_success'] = "SUCCESS: Created item {new_label}."
        self.messages['EN']['item_delete_heading'] = "Delete {item_label} in {model_name}:"
        self.messages['EN']['item_delete_notice'] = "Beware: By deleting items, you also delete any data associated with these items."
        self.messages['EN']['item_delete_confirm'] = "Yes, delete please!"
        self.messages['EN']['item_delete_reject'] = "No thanks, take me back!"
        self.messages['EN']['item_upload_report'] = "Added items [{new_labels}] to {model_name}. Ignored [{duplicates}], as these were already present in {model_name}"


    def get(self, message_label: str, kwargs: dict) -> str:
        """
        Return function specific message to the user in chosen language

        message_label: str with database label for message
        kwargs: dict of str: str with inserts for message
        """

        message = self.messages[self.language][message_label]
        return message.format(**kwargs)

    def get_context(self, app: str, action: str, result: str):
        pass

# Possibly add infrastructure, so selected user groups can add languages
