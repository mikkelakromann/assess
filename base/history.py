from . version import Version

class History():
    """
    Account for the history of the model so far.
    Provide information and functionality for viewing model history.
    The history of the table derived from data saved when a version
    is committed. There is (so far) no check on whether saved history
    matches the actual table.
    """

    def __init__(self,model):
        self.model = model
        self.model_name = self.model._meta.object_name.lower()
        self.context_data = [ ]

        # Proposed data are present in the database table, but has not yet
        # been assigned a version. Hence we need an empty object
        proposed = Version()
        proposed.set_version_id("proposed")
        proposed.set_metrics(self.model)
        if proposed.cells >0:
            proposed.status = "Proposed"
            proposed.version_link = self.model_name + "_version"
            proposed.change_link = self.model_name + "_change"
            proposed.commit_link = self.model_name + "_commit"
            proposed.revert_link = self.model_name + "_revert"
            proposed.idlink = "proposed"
            self.context_data.append(proposed)
        # All other versions than proposed can be loaded from the version table
        versions = Version.objects.filter(model_name=self.model_name).order_by('-date')
#        versions = Version.objects.all()
        # The current version is the newest (ideally, we need to check that the data table
        # has not been totaly archived by setting a version last on all records)
        if len(versions) > 0:
            current = versions[0]
        for version in versions:
            # It simplifies much in the datatable.load_model() to ask for "current" version
            # rather than the id of current version
            if version.id  == current.id:
                version.idlink = current.id
                version.status = "Current"
            else:
                version.idlink = version.id
                version.status = "Archived"
            version.version_link = self.model_name + "_version"
            version.change_link = self.model_name + "_change"
            self.context_data.append(version)


