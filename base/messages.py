### RENAME TO APP_MESSAGES
class Messages():
    """
    Class for organising multi-language messages to the user
    """

    # Data model to contain columns: language, app, action, result, message


    def __init__(self, language='EN', label='', kwargs={}):

        self.language = 'EN'
        # This is our temporary database. Replace with a Django model database
        # Messages blend with keyword arguments (dict), by enclosing keywords
        # in curly brackets
        self.messages = { }
        self.messages['EN'] = { }
        self.messages['EN']['no_such_message'] = "ERROR: Message label {label} does not exist in language {language}."

        # Item model specific messages
        self.messages['EN']['item_list_heading'] = 'Items in {model_name}'
        self.messages['EN']['item_list_no_items'] = 'There were no items in {model_name}'

        self.messages['EN']['item_update_fail_ID'] = "ERROR: Could not rename item_id {item_id} to {new_label}, as this item_id does not exist."
        self.messages['EN']['item_update_failure'] = "ERROR: Could not rename item {current_label} to {new_label}, as this name is used by another item."
        self.messages['EN']['item_update_success'] = "SUCCESS: Renamed item {current_label} to {new_label}."
        self.messages['EN']['item_update_heading'] = "Renaming item {current_label} in {model_name}:"
        self.messages['EN']['item_update_new_label'] = "Rename {current_label} to:"
        self.messages['EN']['item_update_confirm'] = "Yes, please use this name"
        self.messages['EN']['item_update_reject'] = "No, take me back"

        self.messages['EN']['item_create_heading'] = "Create new item in {model_name}:"
        self.messages['EN']['item_create_text'] = "Name of new item: "
        self.messages['EN']['item_create_confirm'] = "Yes, create item"
        self.messages['EN']['item_create_reject'] = "No, take me back"
        self.messages['EN']['item_create_duplicate'] = "ERROR: Could not create item {new_label}, as this name is used by another item."
        self.messages['EN']['item_create_maxlength'] = "ERROR: Could not create item {new_label}, as this name is longer than {max_length} characters."
        self.messages['EN']['item_create_success'] = "SUCCESS: Created item {new_label}."

        self.messages['EN']['item_delete_heading'] = "Delete item {delete_item} in {model_name}:"
        self.messages['EN']['item_delete_notice'] = "Beware: By deleting items, you also delete any data associated with these items."
        self.messages['EN']['item_delete_confirm'] = "Yes, delete please!"
        self.messages['EN']['item_delete_reject'] = "No thanks, take me back!"
        self.messages['EN']['item_delete_success'] = "SUCCESS: Deleted item {delete_item} in {model_name}."
        self.messages['EN']['item_delete_failure'] = "ERROR: Cannot delete item {delete_item} in {model_name} - it does not exist."

        self.messages['EN']['item_upload_heading'] = "Uploaded items to {model_name}:"
        self.messages['EN']['item_upload_report'] = "Added items {new_labels} to {model_name}. Ignored {duplicates}, as these were already present in {model_name}"
        
        # Table specific messages
        self.messages['EN']['table_commit_heading'] = 'Commit data for the table {model_name}.'
        self.messages['EN']['table_commit_notice'] = 'Please add information about the commit:'
        self.messages['EN']['table_commit_notables'] = 'No tables of this name is available.'
        self.messages['EN']['table_commit_submit'] = 'Yes, please commit these changes'
        self.messages['EN']['table_commit_reject'] = 'No, please do not commit'
        
        # Generic messages
        self.messages['EN']['i18n_user'] = 'User'
        self.messages['EN']['i18n_label'] = 'Label'
        self.messages['EN']['i18n_note'] = 'Note'
        
        self.label = label
        self.kwargs = kwargs

    def get(self, label='', kwargs={}) -> str:
        """
        Return function specific message to the user in chosen language

        message_label: str with database label for message
        kwargs: dict of str: str with inserts for message
        """

        if kwargs == {}: 
            kwargs = self.kwargs
        else:
            self.kwargs = kwargs
        if label == '':
            label = self.label
        else:
            self.label = label
        if label != "":
            try:
                msg = self.messages[self.language][label]
            except:
                msg = self.messages['EN']['no_such_message']
                kwargs = {'label': label, 'language': self.language }
            finally:
                return msg.format(**kwargs)
        else:
            return ""


    def get_context(self, app: str, action: str, result: str): # pragma no cover
        pass

# Possibly add infrastructure, so selected user groups can add languages
