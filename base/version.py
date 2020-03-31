from django.db import models


class Version(models.Model):
    """Django table holding meta information on versions for all apps."""
    # Provide filters for verison_first and version_last depending on version_id string
    # Provide metrics for the version of the model
    # Provide string description and link information for display tables
    label = models.CharField(max_length=15, default="no title")
    user =  models.CharField(max_length=15, default="no user")
    date =  models.DateTimeField(auto_now_add=True)
    note =  models.CharField(max_length=255, default="no notes")
    model_name = models.CharField(max_length=64, default="unknown")
    dimension = models.CharField(max_length=255, default="{ ? }")
    size = models.IntegerField(null=True, blank=True)
    cells = models.IntegerField(null=True, blank=True)
    changes = models.IntegerField(null=True, blank=True)
    metric = models.DecimalField(max_digits=16, decimal_places=6,null=True, blank=True)

    def __str__(self) -> str:
        return self.label

    # TODO: Rename to set_version_status - add to "docs/explanation" status
    def set_version_id(self,version_string="") -> None:
        """Use URL version string to calculate version_id, status and link"""
        # version_id: int   Used for filter kwargs and link_id
        # status: str       Used for internally choosing actions
        # link_id: str      Used for Django reverse url reference
        # Current and archived versions has an id, proposed don't
        # TODO: Rename 'archived' to 'specific' in entire project
        if version_string.isnumeric():
            self.version_id = int(float(version_string))
            self.status = "archived"
            self.link_id = str(self.version_id)
        elif version_string.lower() == "proposed":
            self.version_id = 0
            self.status = "proposed"
            self.link_id = 'proposed'
        else:
            self.version_id = self.get_current_version()
            self.status = "current"
            self.link_id = 'current'

    def get_current_version(self) -> int:
        """Returns current (latest committed) version number for self.model"""
        if self.model_name != 'unknown':
            fm = { 'model_name': self.model_name }
            q = Version.objects.filter(**fm).values('id').order_by('-id')
        else:
            # if self.model_name is not set, return latest for all models
            q = Version.objects.values('id').order_by('-id')
        if len(q) > 0:
            return q[0]['id']
        else:
            return 0
    
    def kwargs_filter_load(self, changes: bool) -> dict:
        """Return kwargs dict for load model version, full or changes only."""
        kwargs = { }
        # Current and archived versions have a not_null version_first
        if self.status == "current":
            # The difference between versions is tied to that version id only
            if changes:
                kwargs['version_first'] = self.version_id
            # The history of a version might extend back to beginning of
            # time, so we need all less than or equal that version id
            # We might (easily) get too many entries, so that must be
            # sorted out afterwards
            else:
                kwargs['version_first__isnull'] = False
                kwargs['version_last__isnull'] = True
        # Proposed has version_first and version_last is_null()
        elif self.status == 'proposed':
            # For diffs both first and last must be null
            if changes:
                # For diffs we exclude current version using that it has
                # not version_first is_null()
                kwargs['version_first__isnull'] = True
                kwargs['version_last__isnull'] = True
            else:
                # For views, we blend proposed and current.
                # Both have version_last is_null()
                kwargs['version_last__isnull'] = True
        # Current is always a view, not a diff, since current can be
        # composed of many versions.

        # Maybe rename "archived" to "version", version might contain both
        # current and archived records
        elif self.status == 'archived':
            # Archived is identified by version_last id
            if changes:
                # Changes only archived is exactly version_last id
                kwargs['version_first'] = self.version_id
            else:
                # Whole archived is less or equal version_last id
                kwargs['version_first__lte'] = self.version_id
        else:   # pragma: nocover 
                # this branch is reached only by failure in .set_version_id()
            # Default to current version
            kwargs['version_first__lte'] = self.version_id
        return kwargs

    def kwargs_filter(self,status,changes=False):
        """Return kwargs filter for Django object queries."""
        # Proposed all-records target proposed and current
        if status == 'proposed' and changes == False:
            r = { 'version_last__isnull': True }
        # Proposed changes-only target only new proposed records
        elif status == 'proposed' and changes == True:
            r = { 'version_first__isnull': True, 'version_last__isnull': True }
        # Current all-records target all records with no version_last 
        elif status == 'current' and changes == False:
            r = { 'version_first__isnull': False, 'version_last__isnull': True}
        # Current changes-only target version first exact version match 
        elif status == 'current' and changes == True:
            r ={ 'version_first': self.version_id }
        # Archived all-records targets version_first at or below version id
        elif status == 'archived' and changes == False:
            r = { 'version_first__lte': self.version_id }
        # Archived changes-only targets exact version_first
        elif status == 'archived' and changes == True:
            r = { 'version_first': self.version_id }
        # TODO: DEPRACATED - TO BE REMOVED FROM HERE AND OTHER PLACES IN CODE
        elif status == 'changes':
            r ={ 'version_first': self.version_id }
        else:
            r = { 'version_first__isnull': False, 'version_last__isnull': True}
        return r
        
