from . messages import Messages
from . version import Version

class AssessSet():
    """Class for set of item models."""


    def __init__(self, model: object) -> None:
        self.model = model
        self.name = model.__name__
        self.message = Messages()
        
        self.context = { }
        self.context['model_name'] = self.name.lower()
        self.context['item_model_name'] = self.name.lower()

        
        cv = {'version_first__isnull': False, 'version_last__isnull': True}
        self.labels_by_ids = {}
        self.ids_by_labels = {}
        self.items = {}
        self.labels = []
        # Provide dicts for lookup of items by label or id
        for item in model.objects.filter(**cv):
            self.labels.append(item.label)
            self.labels_by_ids[item.id] = item.label
            self.ids_by_labels[item.label] = item.id
            self.items[item.label] = item


    def delete(self,item_id_str: str) -> str:
        """Delete the item by setting version status to archived for item and its keys"""

        item_id = int(item_id_str)
        msg_kwargs = { 'model_name': self.name }
        try:
            # Identify label
            delete_label = self.labels_by_ids[item_id]
        except:
            # Provide error information if no existence
            msg = 'item_delete_failure'
            msg_kwargs['delete_item'] = '#' + str(item_id)
        else:
            # Otherwise delete by setting version_last to new version
            msg_kwargs['delete_item'] = delete_label
            msg = 'item_delete_success'
            l = self.message.get(msg, msg_kwargs)
            v = Version.objects.create(label=l, model_name=self.name)
            self.model.objects.filter(id=item_id).update(version_last=v.id)
        finally:
            # Provide success or error message and a list of items
            self.context['item_list_message'] = self.message.get(msg, msg_kwargs)
            self.set_list_context()
        return self.context
        ### OBS! A lot of maps and tables will have "current" records, for
        ### which the item is archived, so those are difficult to display
        ### Perhaps also set "archived" for all maps and tables using item???
        ### use apps.get_models() to loop through all app/models' index_fields
        

    def get_delete_form_context(self, item_id_str: str) -> dict:
        """Provide context for the delete item form."""
        
        item_id = int(item_id_str)
        d = { 'model_name': self.name }
        try:
            item_label = self.labels_by_ids[item_id]
        except:
            d ['delete_item'] = "#" + str(item_id)
            self.context['item_delete_heading'] = self.message.get('item_delete_heading',d)
            self.context['item_delete_failure'] = self.message.get('item_delete_failure',d)
        else:
            self.context['item_label'] = item_label
            d ['delete_item'] = item_label
            self.context['item_delete_id'] = item_id 
            self.context['item_delete_heading'] = self.message.get('item_delete_heading',d)
            self.context['item_delete_notice'] = self.message.get('item_delete_notice',d)
            self.context['item_delete_confirm'] = self.message.get('item_delete_confirm',d)
            self.context['item_delete_reject'] = self.message.get('item_delete_reject',d)
        return self.context

    
    def create(self,new_label: str) -> str:
        """Create new item with label name and commit to database."""
        
        d = { 'new_label': new_label  }
        if new_label in self.labels:
            self.context['item_list_message'] = self.message.get('item_create_failure',d)
        else:
            self.context['item_list_message'] = self.message.get('item_create_success',d) 
            l = self.message.get()
            v = Version.objects.create(label=l, model_name=self.name)
            item = self.model.objects.create(label=new_label,version_first=v)
            item.save()
        self.set_list_context()
        return self.context


    def get_create_form_context(self):
        """Return context for item create form."""

        d = { 'model_name': self.name }
        self.context['item_new_label'] = self.message.get('item_new_item_label', d)
        self.context['item_create_heading'] = self.message.get('item_create_heading', d)
        self.context['item_create_text'] = self.message.get('item_create_text', d)
        self.context['item_create_confirm'] =   self.message.get('item_create_confirm', d)
        self.context['item_create_reject'] =   self.message.get('item_create_reject', d)
        return self.context
    

    def upload_csv(self,csv_string: str) -> None:
        """Upload items in CSV format and commit to database."""

        duplicates = [ ]
        new_labels = [ ]

        # Split CSV string assuming no header and first column is label
        lines = csv_string.splitlines()
        for line in lines:
            cells = line.split("\t")
            new_label = cells[0]
            if new_label in self.labels:
                duplicates.append(new_label)
            else:
                new_labels.append(new_label)
        # For all new labels, load to database as current items
        if new_labels:
            l = self.message.get()
            v = Version.objects.create(label=l)
            for new_label in new_labels:
                item = self.model.objects.create(label=new_label, version_first=v)
                item.save()
        self.set_list_context()
        d = {'new_labels': new_labels, 'duplicates': duplicates, 'model_name': self.name }
        self.context['item_list_heading'] = self.message.get("item_upload_heading",d)
        self.context['item_list_message'] = self.message.get("item_upload_report",d)
        return self.context

    def update(self, POST) -> str:
        """Rename item_id label to new_label. Return succes/failure message"""

        # Renaming the label has no immediate effect on item__id's in
        # data and choice tables. However, the user must ensure that
        # new uploaded data take into account the new label names.

        # Get names of current items
        item_id = int(POST['id'])
        new_label = str(POST['label'])
        try:
            current_label = self.labels_by_ids[item_id]
        except:
            d = { 'current_label': item_id, 'new_label': new_label  }
            self.context['item_list_message'] = self.message.get('item_update_fail_ID',d) 
        else:
            d = { 'current_label': current_label, 'new_label': new_label  }
            if new_label in self.labels:
                self.context['item_list_message'] = self.message.get('item_update_failure',d)
            else:
                item = self.model.objects.get(pk=item_id)
                item.label = new_label
                item.save()
                self.context['item_list_message'] = self.message.get('item_update_success',d) 
        self.set_list_context()
        return self.context


    def get_update_form(self, item_id_str: str) -> dict:
        """Provide context for the item update form."""

        item_id = int(item_id_str)
        d = { 'model_name': self.name }
        try:
            item_label = self.labels_by_ids[item_id]
        except:
            d['current_label'] = "#" + str(item_id)
            self.context['item_update_heading'] = self.message.get('item_update_heading',d)
            self.context['item_update_failure'] = self.message.get('item_update_failure',d)
        else:
            self.context['item_update_label'] = item_label
            d['current_label'] = item_label
            self.context['item_update_id'] = item_id 
            self.context['item_update_heading'] = self.message.get('item_update_heading',d)
            self.context['item_update_new_label'] = self.message.get('item_update_new_label',d)
            self.context['item_update_confirm'] = self.message.get('item_update_confirm',d)
            self.context['item_update_reject'] = self.message.get('item_update_reject',d)
        return self.context
        

    def set_list_context(self):
        """Set the context for displaying list of items."""
        
        d = { 'model_name': self.name }
        self.context['item_list_heading'] = self.message.get('item_list_heading',d)
        self.context['item_list_no_items'] = self.message.get('item_list_no_items',{})
        #self.context['item_list_upload_command'] = 'Upload items.'
        
        kwargs = {'version_first__isnull': False, 'version_last__isnull': True}
        # must return list of dicts: [ { 'label': item_label }, { 'label': item_label }, ... ]
        query = self.model.objects.filter(**kwargs)
        self.context['item_row_list'] = query
        self.context['item_header_list'] = ['label']
        

    def get_context(self):
        """Returns context for listing (item_list.+friends) current items"""

        self.set_list_context()
        return self.context

