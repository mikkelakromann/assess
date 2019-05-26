from django.db import models
from django.db.models import Sum

from . keys import Keys
from . messages import Messages


class Version(models.Model):
    """Django table holding meta information on versions for all apps."""

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


    def __str__(self):
        return self.label


    def set_version_id(self,version_string="") -> None:
        """Set version id with str: 'proposed', 'current' or an int"""

        self.current_version_id = self.get_current_version()

        # Current and archived versions has an id, proposed don't
        self.version_id = 0
        if version_string.isnumeric():
            self.version_id = int(float(version_string))
            if self.version_id == self.current_version_id:
                self.status = "current"
            else:
                self.status = "archived"
        elif version_string == "":
            self.version_id = self.current_version_id
            self.status = "current"
        elif version_string.lower() == "proposed":
            self.status = "proposed"
        else:
            self.status = "blank"
        if self.version_id == 0:
            v = ""
        else:
            v = "(" + str(self.version_id) + ")"
        self.name = self.status + v


    def get_current_version(self):
        """Returns current (latest committed) version number (int)"""

        q = Version.objects.values('id').order_by('-id')
        if len(q) > 0:
            return q[0]['id']
        else:
            return 0


    def set_metrics(self,model):
        """Calculate and set metrics for logging of version qualities."""
        keys = Keys(model)
        # Size of table is the product of item counts in all dimensions
        self.size = keys.size
        # Dimension is a text field describing the item sets
        # spanning the model table
        self.dimension = keys.dimension
        # Model is string model name
        self.model_name = model._meta.object_name.lower()

        # Get information related to current or proposed table
        if self.version_id > 0:
            f = self.kwargs_filter_current()
        else:
            f = self.kwargs_filter_proposed()
        # Number of cells is table is count of relevant rows
        self.cells = model.objects.filter(**f).count()
        # Metric is simple average of current cells
        metric = model.objects.filter(**f).aggregate(Sum('value'))
        if self.cells > 0:
            self.metric = metric['value__sum'] / self.cells
        else:
            self.metric = 0

        # Number of changes in table is count of updates in this version
        #fchg = self.kwargs_filter_changed_records(False,True)
        self.changes = model.objects.filter(**f).count()


    def kwargs_filter_load(self,changes: bool) -> dict:
        """Return kwargs dict for load model version, full or changes only."""

        kwargs = { }
        # Current and archived versions have a not_null version_first
        if self.version_id > 0:

            # The difference between versions is tied to that version id only
            if changes:
                kwargs['version_first'] = self.version_id
            # The history of a version might extend back to beginning of
            # time, so we need all less than or equal that version id
            # We might (easily) get too many entries, so that must be
            # sorted out afterwards
            else:
                kwargs['version_first__lte'] = self.version_id
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
                # Both have version_first is_null()
                kwargs['version_last__isnull'] = True
        # Current is always a view, not a diff, since current can be
        # composed of many versions.
        else:
            self.version = "current"
            kwargs['version_first__isnull'] = False
            kwargs['version_last__isnull'] = True

        return kwargs


    def kwargs_filter_proposed(self):
        """Return kwargs for proposed select filter."""

        # Proposed records has version_first and version_last set to Null
        return { 'version_first__isnull': True, 'version_last__isnull': True }


    def kwargs_filter_current(self):
        """Return kwargs for proposed select filter."""

        # Proposed records has version_first != null, version_last == Null
        return { 'version_first__isnull': False, 'version_last__isnull': True }


    def kwargs_filter_by_ids(self,ids):
        """Return kwargs for select filter by list of ids."""

        # Selecting by ids use list of ids
        return { 'pk__in': ids }


    def kwargs_update_proposed_to_current(self):
        """Return kwargs for updating proposed to current version."""

        # The current version is set to version_first
        return { 'version_first': self.id }


    def kwargs_update_current_to_archived(self):
        """Return kwargs for updating from current to archived version """

        # Archived version has version_last set to archieved version.id
        return { 'version_last': self.id }


    def kwargs_filter_changed_records(self):
        """Return kwargs identifying just changed current records."""

        # Changed records in this current version all have latest id
        return { 'version_first': self.id }

