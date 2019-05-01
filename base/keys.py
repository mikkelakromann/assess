from . models import Version

class Keys():
    
    def __init__(self,model):

        self.model = model
        self.index_fields = model.index_fields
        
        # Lookup dicts for index field names and item ids and item labels
        self.indices_ids_labels = {}    # Dict of dicts {field: {id: label}, }
        self.indices_labels_ids = {}    # Dict of dicts {field: {label: id}, }
        self.indices_labels = {}        # Dict of lists {field: [label, ]}
        # OBS: Trying to return the indices items for specified archied 
        # versions is going to be really messy. Current items are needed for
        # chekcing of user upload data integrity
        for column_name in self.index_fields:
            try:
                # Get the foreign key model items for each index in collection
                column_model = self.model._meta.get_field(column_name).remote_field.model
            except:
                # Bad stuff will happen when self.index_field supplied in 
                # app_name / models.py does not reflect the model's columns
                # ### OBS: Provide better error message from messages.py
                return column_name + "internal error."
            ids_labels = {}
            labels_ids = {}
            labels = []
            v = Version()
            fc = v.kwargs_filter_current()
            for item in column_model.objects.filter(**fc):
                ids_labels[item.id] = item.label
                labels_ids[item.label] = item.id
                labels.append(item.label)
            # Store the list and dicts in the collection object    
            self.indices_ids_labels[column_name] = ids_labels
            self.indices_labels_ids[column_name] = labels_ids
            self.indices_labels[column_name] = labels


    # combos(['Piger','Drenge','Lærere'], 
    #          {'Piger': ['Alberte', 'Liva', 'Harriet'], 
    #           'Drenge': ['Luca', 'Louie'], 
    #           'Lærere': ['Malou', 'Søren', 'Elisabeth']}, {})
    def item_combos(self,__order,__indices,__columns):
        """Span out all combination of indices to key dicts
            
            Arguments:
                order: list of str field names for ordering of the columns
                indices: dict of list of items still to be arranged in columns
                columns: dict of list of itmes alreadu arranged in columns
        """

        # indices1 = {f1: [iX,iY]}
        # indices2 = {f2: [iA,iB]}
        # keys = {f3: [i1,i2,i3]}
        # indices12 = {f1: [iX,iY], f2: [iA,iB] }
        # indices123 = {f1: [iX,iY], f2: [iA,iB], f3: [i1,i2,i3] }
        # F(indices2,keys) = {f2: [iA,iA,iA,iB,iB,iB], f3: [i1,i2,i3,i1,i2,i3]}
        # F(indices12,keys) F(indices1,F(indices2,keys))
        # F(indices123,[]) = F(indices12,indices3)

        # The routine rearranges the inputs - make copies
        order = __order.copy()
        indices = __indices.copy()
        columns = __columns.copy() 


        # Arrange to columns if there are more indices
        if len(indices) > 0:
            # Calculate the number of rows in already arranged columns
            if len(columns) > 0:
                # We must have a field name to select a dict item, use first
                first_field_name = list(columns.keys())[0]
                column_length = len(columns[first_field_name])
            else:
                column_length = 1
            # Find next field to arrange, and get its items for a new column
            field = order.pop()
            items = indices.pop(field)
            new_columns = { field: [] }
            # In the new column, the items are repeated with the length of 
            # the already arranged columns 
            for i in items:
                new_columns[field].extend([i]*column_length)
            # The already arranged columns are duplicated with the number 
            # of items in the new column
            for column_name in columns.keys():
                new_columns[column_name] = columns[column_name]*len(items)
            # Recursively call back 
            return self.item_combos(order,indices,new_columns)
        # If no more indices, we're done doing the arranged columns
        else:
            return columns


